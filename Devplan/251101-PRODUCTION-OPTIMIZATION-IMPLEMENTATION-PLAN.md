# 🚀 Production-Grade Pipeline Optimization - Implementation Plan

> **Date:** November 1, 2025  
> **Based on:** 251101-INGESTION-PIPELINE-DEEP-ANALYSIS.md  
> **Goal:** Transform current pipeline to production-grade with 99.6% cost reduction  
> **Timeline:** 5 phases, ~2-3 days total implementation  
> **Target:** Books 10MB-200MB (primary use case)

---

## 📋 EXECUTIVE SUMMARY

**Current State:**
- ✅ Works (100% success rate)
- ⚠️ Inefficient (chunk-level episodes, sequential-only)
- ⚠️ Expensive ($2.31 per 149MB book)
- ⚠️ Slow (6-7 hours per large book)

**Target State:**
- ✅ Production-grade
- ✅ Optimized (section-level + bulk)
- ✅ Cost-effective ($0.01 per book - 99.6% savings!)
- ✅ Fast (1-2 hours per large book - 75% faster!)

**Implementation Phases:**
1. **Phase 1:** Bulk Ingestion (`add_episode_bulk`) - 4 hours
2. **Phase 2:** Section-Level Episodes - 6 hours  
3. **Phase 3:** Dynamic Configuration System - 3 hours
4. **Phase 4:** Enhanced Monitoring - 4 hours
5. **Phase 5:** Production Hardening - 3 hours

**Total:** ~20 hours implementation + ~4 hours testing = **3 days**

---

## 🎯 PHASE 1: Implement Bulk Ingestion Mode

**Duration:** 4 hours  
**Priority:** CRITICAL (40-60% speedup)  
**Risk:** LOW (Graphiti native feature)

### Objectives

1. Add `add_episode_bulk` support to graphiti.py
2. Create toggle between sequential and bulk modes
3. Maintain backward compatibility with SafeIngestionQueue
4. Add configuration for bulk behavior

### Files to Modify

**1. `backend/app/integrations/graphiti.py`** (Main changes)

**2. `backend/app/core/config.py`** (New settings)

**3. `backend/app/core/processor.py`** (Pass config)

### Detailed Implementation

#### Step 1.1: Add Bulk Mode Toggle (30 min)

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...
    
    # NEW: Bulk Ingestion Configuration
    GRAPHITI_USE_BULK_INGESTION: bool = True  # Toggle bulk vs sequential
    GRAPHITI_BULK_BATCH_SIZE: int = 100  # Max episodes per bulk call
    GRAPHITI_SEMAPHORE_LIMIT: int = 15  # Concurrent operations in bulk mode
```

**Sanity Check:**
```bash
# Verify config loads
docker exec rag-backend python3 -c "from app.core.config import settings; print(f'Bulk: {settings.GRAPHITI_USE_BULK_INGESTION}')"
# Expected: "Bulk: True"
```

---

#### Step 1.2: Implement Bulk Ingestion Function (2 hours)

```python
# backend/app/integrations/graphiti.py

import os
from time import time

async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str] = None,
    processing_status: Optional[Dict] = None
) -> None:
    """
    Ingest chunks with AUTOMATIC mode selection (bulk vs sequential).
    
    Mode selection:
    - use_bulk = True (default): Fast, for static documents
    - use_bulk = False: Safe, with token tracking (legacy)
    """
    
    # Check mode from config
    use_bulk = getattr(settings, 'GRAPHITI_USE_BULK_INGESTION', True)
    
    if use_bulk:
        await _ingest_chunks_bulk(chunks, metadata, upload_id, processing_status)
    else:
        await _ingest_chunks_sequential(chunks, metadata, upload_id, processing_status)


async def _ingest_chunks_bulk(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str],
    processing_status: Optional[Dict]
) -> None:
    """
    BULK MODE: Prepare all episodes, single bulk API call.
    
    Performance:
    - 40-60% faster than sequential
    - Graphiti handles rate limiting internally
    - No need for SafeIngestionQueue
    
    Best for:
    - Static documents (books, manuals)
    - Initial graph population
    - Large batches
    """
    
    graphiti_client = await get_graphiti_client()
    
    # Set SEMAPHORE_LIMIT for concurrent processing
    semaphore_limit = getattr(settings, 'GRAPHITI_SEMAPHORE_LIMIT', 15)
    os.environ['SEMAPHORE_LIMIT'] = str(semaphore_limit)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🚀 BULK INGESTION MODE (Optimized)")
    logger.info("=" * 70)
    logger.info(f"   Total chunks: {len(chunks)}")
    logger.info(f"   Semaphore limit: {semaphore_limit}")
    logger.info(f"   Expected speedup: 40-60% vs sequential")
    logger.info("")
    
    # Prepare all episodes
    episodes = []
    for i, chunk in enumerate(chunks):
        chunk_text = chunk["text"]
        chunk_index = chunk["index"]
        total_chunks = chunk['metadata']['total_chunks']
        
        episodes.append({
            "name": f"{metadata.get('filename', 'unknown')} - Chunk {chunk_index+1}",
            "episode_body": chunk_text,
            "source": EpisodeType.text,
            "source_description": f"Document: {metadata.get('filename')}, Chunk {chunk_index+1}/{total_chunks}",
            "reference_time": datetime.now(timezone.utc),
            "group_id": metadata.get('upload_id', 'default')
        })
    
    logger.info(f"📦 Prepared {len(episodes)} episodes for bulk ingestion")
    
    # Split into batches if needed
    batch_size = getattr(settings, 'GRAPHITI_BULK_BATCH_SIZE', 100)
    batches = [episodes[i:i + batch_size] for i in range(0, len(episodes), batch_size)]
    
    logger.info(f"📊 Processing {len(batches)} batches of up to {batch_size} episodes each")
    
    # Process batches
    bulk_start = time()
    total_processed = 0
    
    for batch_num, batch in enumerate(batches, 1):
        batch_start = time()
        
        logger.info(f"")
        logger.info(f"🔄 Batch {batch_num}/{len(batches)}: {len(batch)} episodes")
        
        try:
            # Bulk add - Graphiti handles concurrency internally
            results = await graphiti_client.add_episode_bulk(batch)
            
            batch_duration = time() - batch_start
            total_processed += len(batch)
            
            logger.info(f"✅ Batch {batch_num} complete in {batch_duration:.1f}s")
            logger.info(f"   Processed: {total_processed}/{len(episodes)} episodes")
            
            # Update progress
            if processing_status and upload_id:
                overall_progress = 75 + int(25 * total_processed / len(episodes))
                processing_status[upload_id].update({
                    "progress": overall_progress,
                    "ingestion_progress": {
                        "chunks_completed": total_processed,
                        "chunks_total": len(episodes),
                        "progress_pct": int(100 * total_processed / len(episodes))
                    }
                })
        
        except Exception as e:
            logger.error(f"❌ Batch {batch_num} failed: {e}")
            # Continue with next batch (don't fail entire ingestion)
            continue
    
    bulk_duration = time() - bulk_start
    
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"✅ BULK INGESTION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"   Total episodes: {len(episodes)}")
    logger.info(f"   Successfully processed: {total_processed}")
    logger.info(f"   Total time: {bulk_duration:.1f}s ({bulk_duration/60:.1f} min)")
    logger.info(f"   Avg per episode: {bulk_duration/total_processed:.1f}s")
    logger.info("")


async def _ingest_chunks_sequential(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str],
    processing_status: Optional[Dict]
) -> None:
    """
    SEQUENTIAL MODE: Original implementation with SafeIngestionQueue.
    
    Use when:
    - Need precise token tracking
    - Conservative rate limiting required
    - Testing/debugging
    
    Performance:
    - Slower than bulk (SafeQueue overhead)
    - BUT: Guaranteed zero rate limit errors
    """
    
    # Original implementation (from current graphiti.py)
    safe_queue = SafeIngestionQueue()
    graphiti_client = await get_graphiti_client()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🔒 SEQUENTIAL INGESTION MODE (Conservative)")
    logger.info("=" * 70)
    logger.info(f"   Total chunks: {len(chunks)}")
    logger.info(f"   SafeIngestionQueue: Enabled")
    logger.info(f"   Token tracking: Active")
    logger.info("")
    
    # ... rest of original sequential implementation ...
    for i, chunk in enumerate(chunks):
        chunk_text = chunk["text"]
        # ... existing code ...
        
        await safe_queue.safe_add_episode(
            graphiti_client,
            name=f"...",
            episode_body=chunk_text,
            ...
        )
```

**Sanity Check (End of Step 1.2):**
```bash
# Test bulk mode toggle
docker exec rag-backend python3 << 'EOF'
import asyncio
from app.integrations.graphiti import ingest_chunks_to_graph

# Mock chunks
test_chunks = [
    {"index": 0, "text": "Test chunk 1", "metadata": {"total_chunks": 2}},
    {"index": 1, "text": "Test chunk 2", "metadata": {"total_chunks": 2}}
]

async def test():
    # Should use bulk mode (config default)
    await ingest_chunks_to_graph(
        chunks=test_chunks,
        metadata={"filename": "test.pdf", "upload_id": "test123"}
    )
    print("✅ Bulk mode test passed")

asyncio.run(test())
EOF

# Expected output: "🚀 BULK INGESTION MODE"
```

---

#### Step 1.3: Update Processor Integration (30 min)

```python
# backend/app/core/processor.py

async def process_document(...):
    # ... existing code ...
    
    # STEP 3: Ingest to Knowledge Graph
    # Mode is now controlled by config (GRAPHITI_USE_BULK_INGESTION)
    await ingest_chunks_to_graph(
        chunks=chunks,
        metadata=enriched_metadata,
        upload_id=upload_id,
        processing_status=processing_status
    )
    # Bulk vs sequential is handled automatically based on config
```

**No code changes needed** - mode selection is automatic!

---

#### Step 1.4: Integration Test (1 hour)

**Test 1: Bulk Mode with Niveau 1.pdf**
```bash
# 1. Ensure config has GRAPHITI_USE_BULK_INGESTION=True
# 2. Clear Neo4j
curl -s -X POST http://localhost:8000/api/neo4j/clean

# 3. Upload Niveau 1.pdf
curl -X POST http://localhost:8000/api/upload -F "file=@TestPDF/Niveau 1.pdf"

# 4. Monitor for "BULK INGESTION MODE" in logs
docker logs -f rag-backend | grep "BULK"

# 5. Verify completion time
# Expected: 2-3 min (vs 3.9 min sequential)
# Savings: ~30-40%
```

**Test 2: Sequential Mode (Fallback)**
```bash
# 1. Set GRAPHITI_USE_BULK_INGESTION=False in .env
# 2. Restart backend
# 3. Upload test.pdf
# 4. Verify "SEQUENTIAL INGESTION MODE" in logs
# Expected: Same behavior as before
```

**Acceptance Criteria:**
- ✅ Bulk mode works (chunks ingested)
- ✅ Sequential mode still works (fallback)
- ✅ Entities/relations extracted correctly
- ✅ Time savings: 30-40% in bulk mode
- ✅ No errors in logs

---

### Phase 1 Deliverables

- ✅ `graphiti.py` updated (bulk + sequential modes)
- ✅ `config.py` updated (new settings)
- ✅ Integration tests passed
- ✅ Documentation updated
- ✅ Git commit: "feat: Add bulk ingestion mode (40-60% speedup)"

### Phase 1 Exit Criteria

- [ ] Bulk mode tested with Niveau 1.pdf
- [ ] Time improvement measured (30-40% faster)
- [ ] No regression in quality (entity/relation counts similar)
- [ ] Sequential mode still works (fallback validated)

---

## 🎯 PHASE 2: Section-Level Episode Grouping

**Duration:** 6 hours  
**Priority:** CRITICAL (99.6% cost reduction!)  
**Risk:** MEDIUM (requires heading extraction)

### Objectives

1. Extract headings from Docling chunks
2. Group chunks by top-level heading (sections)
3. Create ONE episode per section (not per chunk)
4. Add granularity configuration (chunk/section/document)

### Files to Modify

**1. `backend/app/services/section_grouper.py`** (NEW FILE)

**2. `backend/app/integrations/graphiti.py`** (Add section mode)

**3. `backend/app/core/config.py`** (Add granularity setting)

### Detailed Implementation

#### Step 2.1: Create Section Grouper Module (2 hours)

```python
# backend/app/services/section_grouper.py (NEW FILE)

"""
Section Grouper for Episode Organization

Groups chunks by document sections (chapters) for optimal Graphiti ingestion.
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger('diveteacher.section_grouper')


class SectionGrouper:
    """
    Groups document chunks by section/chapter based on headings.
    
    Strategy:
    1. Extract top-level heading from each chunk
    2. Group consecutive chunks with same heading
    3. Create one episode per section
    
    Result: 3,083 chunks → 15 sections (for typical book)
    """
    
    def __init__(self, min_section_tokens: int = 500):
        """
        Initialize section grouper.
        
        Args:
            min_section_tokens: Minimum tokens for a section (skip tiny sections)
        """
        self.min_section_tokens = min_section_tokens
    
    def group_chunks_by_section(
        self,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group chunks by top-level heading.
        
        Args:
            chunks: List of chunks from ARIA chunker
            
        Returns:
            Dict mapping section names to lists of chunks
            
        Example:
            {
                "Introduction": [chunk1, chunk2, chunk3],
                "Chapter 1: Equipment": [chunk4, chunk5],
                "Chapter 2: Safety": [chunk6, chunk7, chunk8],
                ...
            }
        """
        sections = defaultdict(list)
        current_section = "Introduction"  # Default for chunks before first heading
        
        for chunk in chunks:
            # Try to extract heading from chunk metadata
            # Docling stores headings in chunk.meta.headings
            heading = self._extract_heading(chunk)
            
            if heading:
                current_section = heading
            
            sections[current_section].append(chunk)
        
        logger.info(f"📚 Grouped {len(chunks)} chunks into {len(sections)} sections")
        
        # Log section sizes
        for section_name, section_chunks in sections.items():
            total_tokens = sum(c.get("metadata", {}).get("num_tokens", 0) 
                             for c in section_chunks)
            logger.info(f"   • {section_name}: {len(section_chunks)} chunks, ~{total_tokens} tokens")
        
        # Filter out tiny sections
        filtered_sections = {
            name: chunks_list 
            for name, chunks_list in sections.items()
            if sum(c.get("metadata", {}).get("num_tokens", 0) for c in chunks_list) >= self.min_section_tokens
        }
        
        if len(filtered_sections) < len(sections):
            removed = len(sections) - len(filtered_sections)
            logger.info(f"   Filtered out {removed} tiny sections (< {self.min_section_tokens} tokens)")
        
        return filtered_sections
    
    def _extract_heading(self, chunk: Dict[str, Any]) -> Optional[str]:
        """
        Extract top-level heading from chunk metadata.
        
        Docling chunk metadata structure:
        chunk = {
            "text": "...",
            "metadata": {
                "headings": ["Chapter 1", "Section 1.1"],  # ← Extract this
                "doc_items": [...],
                ...
            }
        }
        
        Returns:
            Top-level heading (first in list) or None
        """
        metadata = chunk.get("metadata", {})
        headings = metadata.get("headings", [])
        
        if headings and len(headings) > 0:
            # Return top-level heading (first element)
            return headings[0]
        
        return None
    
    def combine_section_chunks(
        self,
        section_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Combine all chunks in a section into single text.
        
        Args:
            section_chunks: List of chunks belonging to same section
            
        Returns:
            Combined text with section boundaries preserved
        """
        # Combine with double newline (paragraph separator)
        combined_text = "\n\n".join([c["text"] for c in section_chunks])
        
        return combined_text
    
    def create_section_metadata(
        self,
        section_name: str,
        section_chunks: List[Dict[str, Any]],
        base_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create metadata for section episode.
        
        Includes:
        - Section name
        - Chunk count
        - Token count
        - Original document metadata
        """
        total_tokens = sum(c.get("metadata", {}).get("num_tokens", 0) 
                          for c in section_chunks)
        
        return {
            "section_name": section_name,
            "num_chunks": len(section_chunks),
            "total_tokens": total_tokens,
            "filename": base_metadata.get("filename"),
            "upload_id": base_metadata.get("upload_id"),
            "source": "section_grouper"
        }


# Singleton instance
_section_grouper: Optional[SectionGrouper] = None


def get_section_grouper() -> SectionGrouper:
    """Get or create SectionGrouper singleton."""
    global _section_grouper
    if _section_grouper is None:
        min_tokens = getattr(settings, 'GRAPHITI_SECTION_MIN_TOKENS', 500)
        _section_grouper = SectionGrouper(min_section_tokens=min_tokens)
        logger.info(f"🏗️  SectionGrouper initialized (min_tokens: {min_tokens})")
    return _section_grouper
```

**Sanity Check (Step 2.1):**
```python
# Test section grouper
docker exec rag-backend python3 << 'EOF'
from app.services.section_grouper import SectionGrouper

# Mock chunks with headings
chunks = [
    {"text": "intro", "metadata": {"headings": [], "num_tokens": 100}},
    {"text": "ch1-1", "metadata": {"headings": ["Chapter 1"], "num_tokens": 200}},
    {"text": "ch1-2", "metadata": {"headings": ["Chapter 1"], "num_tokens": 150}},
    {"text": "ch2-1", "metadata": {"headings": ["Chapter 2"], "num_tokens": 180}},
]

grouper = SectionGrouper(min_section_tokens=100)
sections = grouper.group_chunks_by_section(chunks)

print(f"Sections: {list(sections.keys())}")
# Expected: ['Introduction', 'Chapter 1', 'Chapter 2']

print(f"Chapter 1 chunks: {len(sections['Chapter 1'])}")
# Expected: 2

print("✅ Section grouper test passed")
EOF
```

---

#### Step 2.2: Implement Section-Level Ingestion (2 hours)

```python
# backend/app/integrations/graphiti.py

from app.services.section_grouper import get_section_grouper

async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str] = None,
    processing_status: Optional[Dict] = None
) -> None:
    """
    Ingest with AUTOMATIC granularity selection.
    
    Granularity modes:
    - chunk: One episode per chunk (current/legacy)
    - section: One episode per section (RECOMMENDED for books)
    - document: One episode per document (ultimate optimization)
    """
    
    # Get configuration
    use_bulk = getattr(settings, 'GRAPHITI_USE_BULK_INGESTION', True)
    granularity = getattr(settings, 'GRAPHITI_EPISODE_GRANULARITY', 'section')
    
    logger.info(f"📋 Ingestion config: granularity={granularity}, bulk={use_bulk}")
    
    # Route to appropriate implementation
    if granularity == 'section':
        await _ingest_section_level(chunks, metadata, upload_id, processing_status, use_bulk)
    elif granularity == 'document':
        await _ingest_document_level(chunks, metadata, upload_id, processing_status)
    else:  # chunk (default/legacy)
        if use_bulk:
            await _ingest_chunks_bulk(chunks, metadata, upload_id, processing_status)
        else:
            await _ingest_chunks_sequential(chunks, metadata, upload_id, processing_status)


async def _ingest_section_level(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str],
    processing_status: Optional[Dict],
    use_bulk: bool = True
) -> None:
    """
    SECTION-LEVEL MODE: One episode per book section/chapter.
    
    Performance:
    - 95% fewer LLM calls vs chunk-level
    - 99.6% cost reduction
    - 95% time reduction
    
    Best for:
    - Books, manuals, technical docs (10MB-200MB)
    - Static reference content
    - Budget-conscious production
    """
    
    graphiti_client = await get_graphiti_client()
    grouper = get_section_grouper()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("📚 SECTION-LEVEL INGESTION MODE (Optimized)")
    logger.info("=" * 70)
    logger.info(f"   Input chunks: {len(chunks)}")
    logger.info("")
    
    # Group chunks by section
    sections = grouper.group_chunks_by_section(chunks)
    
    logger.info(f"   Grouped into: {len(sections)} sections")
    logger.info(f"   Reduction: {len(chunks)} chunks → {len(sections)} episodes")
    logger.info(f"   Savings: {100 * (1 - len(sections)/len(chunks)):.1f}% fewer episodes")
    logger.info("")
    
    # Prepare section episodes
    episodes = []
    for section_name, section_chunks in sections.items():
        # Combine chunks
        combined_text = grouper.combine_section_chunks(section_chunks)
        section_meta = grouper.create_section_metadata(section_name, section_chunks, metadata)
        
        episodes.append({
            "name": f"{metadata.get('filename', 'unknown')}_{section_name}",
            "episode_body": combined_text,
            "source": EpisodeType.text,
            "source_description": f"Section: {section_name} ({len(section_chunks)} chunks)",
            "reference_time": datetime.now(timezone.utc),
            "group_id": metadata.get('upload_id', 'default')
        })
    
    logger.info(f"📦 Prepared {len(episodes)} section-level episodes")
    
    # Ingest episodes (bulk or sequential based on config)
    if use_bulk:
        logger.info(f"🚀 Using bulk mode for {len(episodes)} sections")
        
        bulk_start = time()
        results = await graphiti_client.add_episode_bulk(episodes)
        bulk_duration = time() - bulk_start
        
        logger.info("")
        logger.info(f"✅ Section-level bulk ingestion complete")
        logger.info(f"   Episodes: {len(episodes)}")
        logger.info(f"   Time: {bulk_duration:.1f}s ({bulk_duration/60:.1f} min)")
        logger.info(f"   Avg per section: {bulk_duration/len(episodes):.1f}s")
        logger.info("")
    else:
        # Sequential section ingestion (rare case)
        for i, episode_data in enumerate(episodes):
            await graphiti_client.add_episode(**episode_data)
            
            # Update progress
            if processing_status and upload_id:
                overall_progress = 75 + int(25 * (i+1) / len(episodes))
                processing_status[upload_id].update({"progress": overall_progress})
```

**Sanity Check (Step 2.2):**
```bash
# Test section-level with Niveau 1.pdf
# Expected: 1-3 sections (small PDF)
# Time: 30-60 seconds (vs 3.9 min)
# Cost: ~$0.001 (vs $0.01)

docker logs rag-backend --tail 50 | grep "section"
# Expected output:
# "Grouped into: 2 sections"
# "Reduction: 3 chunks → 2 episodes"
# "Savings: 33.3% fewer episodes"
```

---

#### Step 2.3: Add Episode Granularity Config (1 hour)

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... existing ...
    
    # NEW: Episode Granularity Configuration
    GRAPHITI_EPISODE_GRANULARITY: str = "section"  # chunk|section|document
    GRAPHITI_SECTION_MIN_TOKENS: int = 500  # Min tokens for valid section
    GRAPHITI_USE_BULK_INGESTION: bool = True
    GRAPHITI_BULK_BATCH_SIZE: int = 100
    GRAPHITI_SEMAPHORE_LIMIT: int = 15
```

**Environment Variables:**
```bash
# .env file
GRAPHITI_EPISODE_GRANULARITY=section  # chunk|section|document
GRAPHITI_SECTION_MIN_TOKENS=500
GRAPHITI_USE_BULK_INGESTION=true
GRAPHITI_SEMAPHORE_LIMIT=15
```

---

#### Step 2.4: Implement Document-Level Mode (1 hour)

```python
# backend/app/integrations/graphiti.py

async def _ingest_document_level(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    upload_id: Optional[str],
    processing_status: Optional[Dict]
) -> None:
    """
    DOCUMENT-LEVEL MODE: One episode = entire document.
    
    Ultimate optimization:
    - 99.9% cost reduction
    - 98% time reduction
    - Single episode for entire book
    
    Use when:
    - Static reference materials
    - Budget critical
    - Don't need chunk attribution
    
    Claude Haiku 4.5 context: 200K tokens
    → Can handle most books as single episode
    """
    
    graphiti_client = await get_graphiti_client()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("📄 DOCUMENT-LEVEL INGESTION MODE (Ultimate)")
    logger.info("=" * 70)
    logger.info(f"   Input chunks: {len(chunks)}")
    logger.info(f"   Creating: 1 episode (entire document)")
    logger.info("")
    
    # Combine ALL chunks into single text
    combined_text = "\n\n".join([c["text"] for c in chunks])
    total_tokens = sum(c.get("metadata", {}).get("num_tokens", 0) for c in chunks)
    
    logger.info(f"   Total text: {len(combined_text)} chars")
    logger.info(f"   Total tokens: ~{total_tokens}")
    
    # Verify fits in Claude context (200K tokens)
    if total_tokens > 180000:  # Safety margin
        logger.warning(f"⚠️  Document too large ({total_tokens} tokens > 180K limit)")
        logger.warning(f"   Falling back to section-level mode")
        await _ingest_section_level(chunks, metadata, upload_id, processing_status, use_bulk=True)
        return
    
    logger.info(f"   ✅ Fits in Claude context (< 180K tokens)")
    logger.info("")
    
    # Create single episode for entire document
    doc_start = time()
    
    await graphiti_client.add_episode(
        name=f"book_{metadata.get('filename', 'unknown')}",
        episode_body=combined_text,
        source=EpisodeType.text,
        source_description=f"Complete book: {metadata.get('filename')} ({len(chunks)} chunks)",
        reference_time=datetime.now(timezone.utc),
        group_id=metadata.get('upload_id', 'default')
    )
    
    doc_duration = time() - doc_start
    
    logger.info("")
    logger.info("✅ Document-level ingestion complete")
    logger.info(f"   Episodes: 1")
    logger.info(f"   Time: {doc_duration:.1f}s ({doc_duration/60:.1f} min)")
    logger.info(f"   Estimated LLM calls: 3-5 total")
    logger.info("")
```

**Sanity Check (Step 2.4):**
```bash
# Test document-level with test.pdf
# Set GRAPHITI_EPISODE_GRANULARITY=document
# Expected: 1 episode created
# Time: 10-30 seconds
# Cost: ~$0.0001
```

---

#### Step 2.5: Integration Test - Section vs Chunk vs Document (2 hours)

**Test Matrix:**

| Mode | Document | Expected Episodes | Expected Time | Expected Cost |
|------|----------|-------------------|---------------|---------------|
| chunk | Niveau 1.pdf (3 chunks) | 3 | 3.9 min | $0.01 |
| section | Niveau 1.pdf | 1-2 | 30-60s | $0.001 |
| document | Niveau 1.pdf | 1 | 10-30s | $0.0001 |

**Test Procedure:**
```bash
# Test 1: Chunk-level (baseline)
export GRAPHITI_EPISODE_GRANULARITY=chunk
export GRAPHITI_USE_BULK_INGESTION=true
# Upload Niveau 1.pdf
# Measure: time, cost, entity count

# Test 2: Section-level (recommended)
export GRAPHITI_EPISODE_GRANULARITY=section
# Upload Niveau 1.pdf (different upload_id)
# Measure: time, cost, entity count
# Compare with Test 1

# Test 3: Document-level (ultimate)
export GRAPHITI_EPISODE_GRANULARITY=document
# Upload Niveau 1.pdf (different upload_id)
# Measure: time, cost, entity count
# Compare with Test 1 & 2
```

**Acceptance Criteria:**
- ✅ All 3 modes work
- ✅ Section mode: 60-90% time savings
- ✅ Document mode: 95% time savings
- ✅ Entity counts similar across modes (±10%)
- ✅ Quality maintained

---

### Phase 2 Deliverables

- ✅ `section_grouper.py` created (new module)
- ✅ `graphiti.py` updated (section + document modes)
- ✅ `config.py` updated (granularity settings)
- ✅ All 3 modes tested and validated
- ✅ Git commit: "feat: Add section/document-level episodes (99.6% cost reduction)"

### Phase 2 Exit Criteria

- [ ] Section grouper extracts headings correctly
- [ ] Section-level mode: 60%+ time savings validated
- [ ] Document-level mode: 95%+ time savings validated
- [ ] Entity/relation quality maintained (no degradation)
- [ ] All tests passed

---

## 🎯 PHASE 3: Dynamic Configuration System

**Duration:** 3 hours  
**Priority:** HIGH (enables production flexibility)  
**Risk:** LOW (config only)

### Objectives

1. Make all critical settings configurable
2. Add dynamic timeout calculation
3. Increase file size limits
4. Add mode selection helpers

### Files to Modify

**1. `backend/app/core/config.py`** (Comprehensive config)

**2. `backend/app/api/upload.py`** (Dynamic limits)

**3. `backend/app/integrations/dockling.py`** (Dynamic timeout)

### Detailed Implementation

#### Step 3.1: Comprehensive Configuration (1 hour)

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...
    
    # ═══════════════════════════════════════════════════════════
    # PRODUCTION-GRADE CONFIGURATION (2025-11-01)
    # ═══════════════════════════════════════════════════════════
    
    # File Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 200  # Increased from 50 (for large books)
    MAX_UPLOAD_SIZE_AUTO: bool = True  # Auto-adjust based on Docker memory
    ALLOWED_EXTENSIONS: str = "pdf,ppt,pptx,doc,docx"
    
    # Docling Processing
    DOCLING_TIMEOUT_BASE: int = 900  # 15 min base
    DOCLING_TIMEOUT_PER_PAGE: int = 60  # +60s per page (dynamic)
    DOCLING_TIMEOUT_MAX: int = 10800  # 3 hours max
    DOCLING_OCR_ENABLED: bool = True
    DOCLING_TABLE_MODE: str = "ACCURATE"  # ACCURATE|FAST
    
    # ARIA Chunking (RecursiveCharacterTextSplitter)
    ARIA_CHUNK_SIZE_TOKENS: int = 3000  # ARIA production standard
    ARIA_CHUNK_OVERLAP_TOKENS: int = 200
    ARIA_CHARS_PER_TOKEN: int = 4
    
    # Graphiti Episode Configuration
    GRAPHITI_EPISODE_GRANULARITY: str = "section"  # chunk|section|document
    GRAPHITI_SECTION_MIN_TOKENS: int = 500  # Min section size
    GRAPHITI_USE_BULK_INGESTION: bool = True  # Bulk vs sequential
    GRAPHITI_BULK_BATCH_SIZE: int = 100  # Episodes per bulk call
    GRAPHITI_SEMAPHORE_LIMIT: int = 15  # Concurrent operations
    
    # SafeIngestionQueue (for sequential mode)
    GRAPHITI_SAFE_QUEUE_ENABLED: bool = True
    GRAPHITI_RATE_LIMIT_TOKENS_PER_MIN: int = 4_000_000
    GRAPHITI_SAFETY_BUFFER_PCT: float = 0.80
    GRAPHITI_ESTIMATED_TOKENS_PER_CHUNK: int = 3_000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_docling_timeout(self, num_pages: int) -> int:
        """
        Calculate dynamic timeout based on page count.
        
        Formula: base + (pages × per_page), capped at max
        
        Examples:
        - 10 pages: 900 + (10×60) = 1,500s = 25 min
        - 146 pages: 900 + (146×60) = 9,660s → capped at 10,800s = 3h
        """
        if not self.DOCLING_TIMEOUT_PER_PAGE:
            return self.DOCLING_TIMEOUT_BASE
        
        timeout = self.DOCLING_TIMEOUT_BASE + (num_pages * self.DOCLING_TIMEOUT_PER_PAGE)
        return min(timeout, self.DOCLING_TIMEOUT_MAX)
```

---

#### Step 3.2: Dynamic File Size Limit (30 min)

```python
# backend/app/api/upload.py

async def upload_document(file: UploadFile = File(...)):
    # ... existing code ...
    
    # Dynamic max size check
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    # If AUTO mode, check Docker available memory
    if settings.MAX_UPLOAD_SIZE_AUTO:
        import psutil
        available_mb = psutil.virtual_memory().available / (1024 * 1024)
        max_size = min(max_size, int(available_mb * 0.3))  # Use max 30% available RAM
        logger.info(f"Dynamic upload limit: {max_size / (1024*1024):.0f} MB (30% of {available_mb:.0f} MB available)")
    
    # Validate file size
    if total_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum: {max_size / (1024*1024):.0f}MB"
        )
```

---

#### Step 3.3: Dynamic Timeout (30 min)

```python
# backend/app/integrations/dockling.py

async def convert_document_to_docling(
    file_path: str,
    upload_id: str
) -> DoclingDocument:
    """Convert with DYNAMIC timeout based on PDF page count."""
    
    # Try to get page count before conversion (quick PDF inspection)
    try:
        import fitz  # PyMuPDF (lightweight)
        doc = fitz.open(file_path)
        num_pages = len(doc)
        doc.close()
    except:
        num_pages = 100  # Default estimate if can't read
    
    # Calculate dynamic timeout
    timeout = settings.get_docling_timeout(num_pages)
    
    logger.info(f"📄 PDF: {num_pages} pages")
    logger.info(f"⏱️  Timeout: {timeout}s ({timeout/60:.1f} min)")
    
    # Use calculated timeout
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_docling_executor.submit, converter.convert, file_path).result,
            timeout=timeout  # ← Dynamic timeout
        )
    except asyncio.TimeoutError:
        raise TimeoutError(f"Conversion exceeded {timeout}s for {num_pages} pages")
```

**Sanity Check (Step 3.3):**
```python
# Test dynamic timeout calculation
from app.core.config import settings

print(f"10 pages: {settings.get_docling_timeout(10)}s")  # 1,500s = 25 min
print(f"146 pages: {settings.get_docling_timeout(146)}s")  # 10,800s = 3h (capped)
```

---

#### Step 3.4: Configuration Helper (1 hour)

```python
# backend/app/core/config_helper.py (NEW FILE)

"""
Configuration helpers for pipeline optimization.
"""

from app.core.config import settings
import logging

logger = logging.getLogger('diveteacher.config')


def recommend_granularity(file_size_mb: float, num_pages: int = None) -> str:
    """
    Recommend optimal episode granularity based on document characteristics.
    
    Rules:
    - < 1MB or < 10 pages: document-level (fastest)
    - 1-10MB: section-level (balanced)
    - 10-200MB: section-level (cost-effective)
    - > 200MB: must split before upload
    
    Returns:
        "chunk"|"section"|"document"
    """
    if file_size_mb < 1 or (num_pages and num_pages < 10):
        return "document"
    elif file_size_mb >= 10:
        return "section"
    else:
        return "section"  # Default for 1-10MB


def get_recommended_config(file_size_mb: float, num_pages: int = None) -> Dict[str, Any]:
    """
    Get recommended configuration for a document.
    
    Returns complete config dict for optimal processing.
    """
    granularity = recommend_granularity(file_size_mb, num_pages)
    
    config = {
        "granularity": granularity,
        "use_bulk": True,  # Always use bulk for production
        "timeout": settings.get_docling_timeout(num_pages or 100),
        "semaphore_limit": 15 if file_size_mb > 50 else 10
    }
    
    logger.info(f"📋 Recommended config for {file_size_mb:.1f}MB:")
    logger.info(f"   Granularity: {config['granularity']}")
    logger.info(f"   Bulk mode: {config['use_bulk']}")
    logger.info(f"   Timeout: {config['timeout']}s")
    
    return config
```

---

### Phase 3 Deliverables

- ✅ Comprehensive configuration system
- ✅ Dynamic timeout calculation
- ✅ Increased file size limits (200MB)
- ✅ Configuration helper utilities
- ✅ Git commit: "feat: Production-grade configuration system"

### Phase 3 Exit Criteria

- [ ] All settings configurable via .env
- [ ] Dynamic timeout works for 10-146 pages
- [ ] File size limit accepts 200MB
- [ ] Config helper recommends correct modes

---

## 🎯 PHASE 4: Enhanced Monitoring Integration

**Duration:** 4 hours  
**Priority:** HIGH (production observability)  
**Risk:** LOW (monitoring only)

### Objectives

1. Add granular metrics for each ingestion mode
2. Integrate with existing monitoring tools
3. Add cost tracking per episode/section
4. Create mode-specific dashboards

### Files to Modify/Create

**1. `backend/app/integrations/graphiti.py`** (Add metrics)

**2. `scripts/monitor_ingestion.sh`** (Update for modes)

**3. `scripts/monitor-mode-performance.sh`** (NEW - mode comparison)

### Detailed Implementation

#### Step 4.1: Add Granular Metrics (1.5 hours)

```python
# backend/app/integrations/graphiti.py

async def _ingest_section_level(...):
    # ... existing code ...
    
    # Track metrics
    metrics = {
        "mode": "section-level",
        "input_chunks": len(chunks),
        "output_episodes": len(episodes),
        "reduction_pct": 100 * (1 - len(episodes)/len(chunks)),
        "total_duration_s": bulk_duration,
        "avg_per_episode_s": bulk_duration / len(episodes),
        "estimated_llm_calls": len(episodes) * 3,
        "estimated_cost_usd": (len(episodes) * 3 * 3000 * 0.25) / 1_000_000
    }
    
    logger.info("")
    logger.info("📊 INGESTION METRICS:")
    logger.info(f"   Mode: {metrics['mode']}")
    logger.info(f"   Reduction: {metrics['input_chunks']} chunks → {metrics['output_episodes']} episodes ({metrics['reduction_pct']:.1f}%)")
    logger.info(f"   Duration: {metrics['total_duration_s']:.1f}s")
    logger.info(f"   Est. LLM calls: {metrics['estimated_llm_calls']}")
    logger.info(f"   Est. cost: ${metrics['estimated_cost_usd']:.4f}")
    logger.info("")
    
    # Store metrics in processing_status
    if processing_status and upload_id:
        processing_status[upload_id]["metrics"]["ingestion_mode"] = metrics
```

---

#### Step 4.2: Update Monitoring Scripts (1 hour)

```bash
# scripts/monitor_ingestion.sh

# Add mode-specific keywords
docker logs -f rag-backend 2>&1 | grep --line-buffered -E \
  "BULK INGESTION MODE|SECTION-LEVEL|DOCUMENT-LEVEL|Reduction:|Est. cost:" \
  | while read line; do
    # Color-code by mode
    if echo "$line" | grep -q "BULK"; then
        echo -e "${GREEN}${line}${NC}"
    elif echo "$line" | grep -q "SECTION"; then
        echo -e "${YELLOW}${line}${NC}"
    elif echo "$line" | grep -q "Reduction"; then
        echo -e "${CYAN}${line}${NC}"
    else
        echo "$line"
    fi
done
```

---

#### Step 4.3: Create Mode Performance Monitor (NEW) (1.5 hours)

```bash
# scripts/monitor-mode-performance.sh (NEW FILE)

#!/bin/bash
#
# Mode Performance Monitor
# Compares chunk vs section vs document modes in real-time
#

echo "📊 INGESTION MODE PERFORMANCE MONITOR"
echo "======================================"
echo ""

# Get last 3 uploads (one for each mode)
UPLOADS=$(curl -s http://localhost:8000/api/queue/status | jq -r '.completed_count')

echo "Recent uploads: $UPLOADS"
echo ""

# For each completed upload, show metrics
curl -s http://localhost:8000/api/queue/status | jq -r '.completed_documents[] | 
    "\(.filename): 
    Mode: \(.metrics.ingestion_mode.mode)
    Episodes: \(.metrics.ingestion_mode.output_episodes)
    Time: \(.metrics.ingestion_mode.total_duration_s)s
    Cost: $\(.metrics.ingestion_mode.estimated_cost_usd)
    "' | head -30

echo ""
echo "Mode Comparison:"
echo "  chunk: Many episodes, slow, expensive"
echo "  section: Few episodes, fast, cheap ✅"
echo "  document: 1 episode, fastest, cheapest"
```

---

### Phase 4 Deliverables

- ✅ Granular metrics per mode
- ✅ Updated monitoring scripts
- ✅ New mode performance monitor
- ✅ Cost tracking integrated
- ✅ Git commit: "feat: Enhanced monitoring for optimized pipeline"

### Phase 4 Exit Criteria

- [ ] Metrics logged for all modes
- [ ] Monitor scripts show mode info
- [ ] Cost estimates accurate (±10%)
- [ ] Performance dashboard working

---

## 🎯 PHASE 5: Production Hardening

**Duration:** 3 hours  
**Priority:** MEDIUM (production resilience)  
**Risk:** LOW (quality improvements)

### Objectives

1. Add checkpointing for large documents
2. Improve error messages
3. Add validation warnings
4. Create production deployment checklist

### Detailed Implementation

#### Step 5.1: Checkpointing System (1.5 hours)

```python
# backend/app/services/checkpoint_manager.py (NEW FILE)

"""
Checkpoint Manager for Large Document Ingestion
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger('diveteacher.checkpoint')


class CheckpointManager:
    """
    Saves ingestion progress for large documents.
    
    Allows resume if processing fails mid-way.
    """
    
    def __init__(self, checkpoint_dir: str = "/uploads/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save_checkpoint(
        self,
        upload_id: str,
        progress: Dict[str, Any]
    ) -> None:
        """
        Save checkpoint for upload.
        
        Progress dict:
        {
            "chunks_processed": 1500,
            "chunks_total": 3083,
            "sections_processed": 8,
            "sections_total": 15,
            "last_section": "Chapter 8",
            "timestamp": "2025-11-01T20:00:00"
        }
        """
        checkpoint_file = self.checkpoint_dir / f"{upload_id}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(progress, f, indent=2)
        
        logger.info(f"💾 Checkpoint saved: {upload_id} ({progress['chunks_processed']}/{progress['chunks_total']})")
    
    def load_checkpoint(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint if exists."""
        checkpoint_file = self.checkpoint_dir / f"{upload_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        with open(checkpoint_file, 'r') as f:
            progress = json.load(f)
        
        logger.info(f"📂 Checkpoint loaded: {upload_id} (resume from {progress['chunks_processed']})")
        return progress
    
    def clear_checkpoint(self, upload_id: str) -> None:
        """Clear checkpoint after successful completion."""
        checkpoint_file = self.checkpoint_dir / f"{upload_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info(f"🗑️  Checkpoint cleared: {upload_id}")


# Integrate in graphiti.py
async def _ingest_section_level(...):
    checkpoint_mgr = CheckpointManager()
    
    # Check for existing checkpoint
    checkpoint = checkpoint_mgr.load_checkpoint(upload_id)
    start_from = checkpoint['sections_processed'] if checkpoint else 0
    
    # Process sections
    for i, (section_name, section_chunks) in enumerate(sections.items()):
        if i < start_from:
            continue  # Skip already processed
        
        # Process section...
        
        # Save checkpoint every 5 sections
        if (i + 1) % 5 == 0:
            checkpoint_mgr.save_checkpoint(upload_id, {
                "sections_processed": i + 1,
                "sections_total": len(sections),
                ...
            })
    
    # Clear checkpoint on success
    checkpoint_mgr.clear_checkpoint(upload_id)
```

---

#### Step 5.2: Enhanced Error Messages (30 min)

```python
# backend/app/integrations/graphiti.py

# Add helpful error messages
try:
    await graphiti_client.add_episode_bulk(episodes)
except Exception as e:
    # Enhanced error context
    logger.error("")
    logger.error("=" * 70)
    logger.error("❌ BULK INGESTION FAILED")
    logger.error("=" * 70)
    logger.error(f"   Error: {str(e)}")
    logger.error(f"   Episodes attempted: {len(episodes)}")
    logger.error(f"   Mode: {granularity}")
    logger.error(f"   File: {metadata.get('filename')}")
    logger.error("")
    logger.error("💡 Troubleshooting:")
    logger.error("   1. Check Anthropic API key is valid")
    logger.error("   2. Verify Neo4j connection")
    logger.error("   3. Check episode body size (< 200K tokens)")
    logger.error("   4. Try reducing SEMAPHORE_LIMIT to 10")
    logger.error("   5. Fallback to sequential mode (use_bulk=False)")
    logger.error("")
    raise
```

---

#### Step 5.3: Production Deployment Checklist (1 hour)

Create comprehensive checklist document:

```markdown
# Production Deployment Checklist

## Pre-Deployment

- [ ] Environment variables configured (.env)
  - [ ] GRAPHITI_EPISODE_GRANULARITY=section
  - [ ] GRAPHITI_USE_BULK_INGESTION=true
  - [ ] GRAPHITI_SEMAPHORE_LIMIT=15
  - [ ] MAX_UPLOAD_SIZE_MB=200
  - [ ] DOCLING_TIMEOUT_PER_PAGE=60

- [ ] Dependencies installed
  - [ ] langchain-text-splitters==0.3.2
  - [ ] graphiti-core==0.17.0
  - [ ] All requirements.txt

- [ ] Docker resources
  - [ ] Memory: 16GB allocated
  - [ ] Storage: 50GB available

## Testing

- [ ] Test with small PDF (< 1MB)
  - [ ] Mode: document-level
  - [ ] Time: < 30s
  
- [ ] Test with medium PDF (5-10MB)
  - [ ] Mode: section-level
  - [ ] Time: < 10 min
  
- [ ] Test with large book section (10 pages)
  - [ ] Mode: section-level
  - [ ] Time: < 60 min
  - [ ] Validate entity extraction

## Monitoring

- [ ] monitor-queue.sh working
- [ ] monitor_ingestion.sh shows mode info
- [ ] Logs show cost estimates
- [ ] Sentry configured

## Production Ready

- [ ] All tests passed
- [ ] Documentation updated
- [ ] Team trained on new modes
- [ ] Rollback plan documented
```

---

### Phase 5 Deliverables

- ✅ Checkpoint system implemented
- ✅ Enhanced error messages
- ✅ Production deployment checklist
- ✅ Validation warnings
- ✅ Git commit: "feat: Production hardening (checkpoints + validation)"

### Phase 5 Exit Criteria

- [ ] Checkpoints save/load correctly
- [ ] Error messages are helpful
- [ ] Deployment checklist complete
- [ ] System ready for 100 book batch

---

## 📊 COMPLETE IMPLEMENTATION TIMELINE

### Summary by Phase

| Phase | Task | Duration | Complexity | Risk |
|-------|------|----------|------------|------|
| **Phase 1** | Bulk ingestion | 4h | Low | Low |
| **Phase 2** | Section-level | 6h | Medium | Medium |
| **Phase 3** | Configuration | 3h | Low | Low |
| **Phase 4** | Monitoring | 4h | Low | Low |
| **Phase 5** | Hardening | 3h | Low | Low |
| **TOTAL** | | **20h** | | |

### Critical Path

```
Day 1 (8 hours):
├─ Phase 1: Bulk ingestion (4h)
│  └─ Sanity test: Niveau 1.pdf bulk mode
├─ Phase 2: Start section-level (4h)
│  └─ Section grouper + basic implementation

Day 2 (8 hours):
├─ Phase 2: Complete section-level (2h)
│  └─ Sanity test: All 3 modes with Niveau 1.pdf
├─ Phase 3: Configuration system (3h)
│  └─ Sanity test: Dynamic config
├─ Phase 4: Start monitoring (3h)

Day 3 (4 hours):
├─ Phase 4: Complete monitoring (1h)
│  └─ Sanity test: All monitors show mode info
├─ Phase 5: Production hardening (3h)
│  └─ Final integration test: 10-page section
```

---

## ✅ SANITY TESTS (End of Each Phase)

### Phase 1 Sanity Test

```bash
# Test: Bulk mode with Niveau 1.pdf
1. Set GRAPHITI_USE_BULK_INGESTION=true
2. Upload Niveau 1.pdf
3. Verify logs show "BULK INGESTION MODE"
4. Measure time (expect 2-3 min vs 3.9 min)
5. Check entity count (expect similar to baseline)

Pass criteria:
✅ Time: 2-3 min (30%+ faster)
✅ Entities: 300-350 (similar to baseline 325)
✅ No errors in logs
```

### Phase 2 Sanity Test

```bash
# Test: All 3 modes with Niveau 1.pdf

Test A (chunk-level):
- GRAPHITI_EPISODE_GRANULARITY=chunk
- Upload → Expect 3 episodes, 3-4 min

Test B (section-level):
- GRAPHITI_EPISODE_GRANULARITY=section
- Upload → Expect 1-2 episodes, 30-60s

Test C (document-level):
- GRAPHITI_EPISODE_GRANULARITY=document
- Upload → Expect 1 episode, 10-30s

Pass criteria:
✅ All modes work
✅ Section mode: 60%+ time savings
✅ Document mode: 90%+ time savings
✅ Entity counts within ±20% across modes
```

### Phase 3 Sanity Test

```bash
# Test: Dynamic configuration

Test 1: Small PDF (test.pdf - 2 pages)
- Recommended: document-level
- Timeout: 15 min (base)
- Verify auto-selection works

Test 2: Medium PDF (Niveau 1.pdf - 16 pages)
- Recommended: section-level
- Timeout: 22 min (900 + 16×60)
- Verify calculation correct

Test 3: Large estimate (146 pages)
- Timeout: 3h (capped at max)
- Verify cap works

Pass criteria:
✅ Recommendations make sense
✅ Timeouts calculated correctly
✅ Config loaded from .env
```

### Phase 4 Sanity Test

```bash
# Test: Monitoring integration

1. Upload document in each mode
2. Run ./scripts/monitor_ingestion.sh
3. Verify mode-specific metrics shown
4. Check cost estimates in logs

Pass criteria:
✅ Monitors show granularity mode
✅ Cost estimates displayed
✅ Metrics accurate
```

### Phase 5 Sanity Test

```bash
# Test: Production readiness

1. Simulate failure mid-ingestion
2. Verify checkpoint saved
3. Restart ingestion
4. Verify resumes from checkpoint

Pass criteria:
✅ Checkpoint saves every 5 sections
✅ Resume works correctly
✅ No duplicate episodes
```

---

## 🎯 ACCEPTANCE CRITERIA (Final Validation)

### Functional Requirements

- [ ] Bulk mode works (40%+ speedup validated)
- [ ] Section mode works (99% cost reduction validated)
- [ ] Document mode works (99.9% savings validated)
- [ ] All modes produce quality graphs (entity counts similar)
- [ ] Configuration system flexible (easy mode switching)

### Performance Requirements

**For 149MB PDF (plongee-plaisir-niveau-1.pdf):**

| Mode | Time | Cost | Episodes | Pass? |
|------|------|------|----------|-------|
| **Section-level** | < 2h | < $0.05 | 10-20 | ✅ Target |
| **Document-level** | < 10min | < $0.01 | 1 | ✅ Stretch goal |

### Quality Requirements

- [ ] Entity extraction quality maintained (baseline: 325 entities for Niveau 1)
- [ ] Relation detection working (baseline: 617 relations)
- [ ] Graph queryable (RAG search returns results)
- [ ] No data loss vs baseline

### Operational Requirements

- [ ] Monitoring shows mode selection
- [ ] Logs include cost estimates
- [ ] Checkpoints work for large docs
- [ ] Error messages helpful
- [ ] Documentation complete

---

## 📝 ROLLBACK PLAN

**If Optimizations Cause Issues:**

```bash
# Rollback to current working implementation
git checkout HEAD~5 -- backend/app/integrations/graphiti.py
git checkout HEAD~5 -- backend/app/core/config.py

# Or use feature flag:
export GRAPHITI_USE_BULK_INGESTION=false
export GRAPHITI_EPISODE_GRANULARITY=chunk

# System reverts to current safe behavior
```

**Rollback Time:** 5 minutes  
**Data Loss:** None (Neo4j can be cleared and re-ingested)

---

## 🚀 EXPECTED OUTCOMES

### Performance Improvements

**For Single 149MB Book:**
- Current: 6-7 hours, $2.31
- Optimized: 1-2 hours, $0.01
- **Improvement: 75% time, 99.6% cost! 🎉**

**For 100 Book Batch (Week 1):**
- Current: 600-700 hours, $231
- Optimized: 100-200 hours, $1
- **Improvement: 500 hours, $230 saved! 💰**

### Code Quality

- ✅ More flexible (3 modes vs 1)
- ✅ Better documented
- ✅ Production-grade error handling
- ✅ Comprehensive monitoring
- ✅ Checkpointing for resilience

### Business Impact

- ✅ Week 1 launch feasible (100 hours vs 600)
- ✅ Budget sustainable ($1 vs $231)
- ✅ Scalable to 1000s of books
- ✅ Professional production system

---

## 📋 IMPLEMENTATION CHECKLIST

### Before Starting

- [ ] Read this plan completely
- [ ] Understand all 5 phases
- [ ] Backup current working code
- [ ] Create feature branch
- [ ] Clear schedule for 3 days

### During Implementation

- [ ] Follow phases in order
- [ ] Run sanity test after each phase
- [ ] Don't skip to next phase if test fails
- [ ] Document any deviations
- [ ] Commit after each phase

### After Completion

- [ ] Run all acceptance tests
- [ ] Validate with 10-page section
- [ ] Update all documentation
- [ ] Train team on new modes
- [ ] Deploy to production

---

## 🎓 KNOWLEDGE TRANSFER

### New Concepts Team Needs to Learn

1. **Episode Granularity:**
   - Chunk: One episode per 3000-token chunk
   - Section: One episode per chapter/section
   - Document: One episode per book

2. **Bulk vs Sequential:**
   - Bulk: Fast, Graphiti handles rate limits
   - Sequential: Safe, SafeQueue token tracking

3. **Mode Selection:**
   - < 1MB: document-level
   - 10-200MB: section-level (RECOMMENDED)
   - Special cases: chunk-level

### Configuration Changes

Team must know how to set:
```bash
GRAPHITI_EPISODE_GRANULARITY=section  # Most important!
GRAPHITI_USE_BULK_INGESTION=true      # Enable speedup
GRAPHITI_SEMAPHORE_LIMIT=15           # Concurrent ops
```

---

## 📚 DOCUMENTATION TO UPDATE

After implementation:

1. **docs/ARCHITECTURE.md**
   - Add section on episode granularity
   - Document bulk mode

2. **docs/API.md**
   - New configuration options
   - Mode selection guidelines

3. **docs/USER-GUIDE.md**
   - When to use each mode
   - Cost implications

4. **scripts/SCRIPTS-USAGE-GUIDE.md**
   - Monitoring for each mode
   - Performance comparison

---

## 🎯 SUCCESS METRICS

**Implementation Success:**
- All 5 phases completed
- All sanity tests passed
- All acceptance criteria met

**Performance Success (149MB PDF):**
- Time: < 2 hours (vs 6-7h baseline)
- Cost: < $0.05 (vs $2.31 baseline)
- Quality: ±10% entity count vs baseline

**Production Success (100 Books):**
- Total time: < 200 hours (vs 600-700h)
- Total cost: < $5 (vs $231)
- Success rate: 100%

---

**Implementation Plan Status:** ✅ READY FOR EXECUTION  
**Estimated ROI:** 62.5× (500 hours saved / 8 hours invested)  
**Risk Level:** LOW (all optimizations proven in Graphiti docs)  
**Confidence:** 95% (based on best practices + analysis)

**PROCEED WITH IMPLEMENTATION!** 🚀

