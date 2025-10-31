# 🚨 URGENT: Chunking Fix - Revised Plan (ROOT CAUSE FOUND)

**Date:** October 31, 2025, 18:20 CET  
**Status:** 🔴 **CRITICAL ISSUE DISCOVERED**  
**Priority:** P0 - IMMEDIATE ACTION REQUIRED

---

## 🔍 ROOT CAUSE DISCOVERED

### The Real Problem

**HierarchicalChunker does NOT support max_tokens/min_tokens parameters!**

```python
# What we thought:
HierarchicalChunker(
    max_tokens=3000,   # ❌ IGNORED!
    min_tokens=1000,   # ❌ IGNORED!
    tokenizer="..."    # ❌ IGNORED!
)

# What HierarchicalChunker actually accepts:
HierarchicalChunker(
    merge_list_items=True,  # ✅ Only this
    delim="\n"              # ✅ And this
)
```

**Evidence:**
```bash
# Logs show:
"Token limits: 1000-3000 (was 64-256)"  ← We LOG it
"Created 204 semantic chunks"            ← But HierarchicalChunker IGNORES it

# Chunks created: 204 (same as before)
# Avg tokens: 18 (even WORSE than 105!)
```

**Conclusion:** `HierarchicalChunker` uses INTERNAL logic, ignores our token limits!

---

## ✅ THE REAL SOLUTION

### Use ARIA's RecursiveCharacterTextSplitter (Proven Pattern)

**ARIA's Production Code:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000 * 4,      # 3000 tokens ≈ 12000 chars
    chunk_overlap=200 * 4,    # 200 tokens ≈ 800 chars
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_text(doc_text)
```

**Why This Works:**
- ✅ Direct control over chunk size
- ✅ Proven in ARIA production (3 days, 100% success)
- ✅ Simple, predictable behavior
- ✅ No hidden logic

---

## ⚡ URGENT IMPLEMENTATION

### Quick Fix (15 minutes)

**File:** `backend/app/services/document_chunker.py`

**Replace HierarchicalChunker with RecursiveCharacterTextSplitter:**

```python
"""
Document Chunking avec LangChain RecursiveCharacterTextSplitter

ARIA-validated chunking strategy for production RAG systems.
"""
import logging
from typing import List, Dict, Any, Optional
from docling.datamodel.document import DoclingDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger('diveteacher.chunker')


class DocumentChunker:
    """
    ARIA-validated chunking strategy
    
    Uses RecursiveCharacterTextSplitter with:
    - 3000 tokens per chunk (optimal for entity extraction)
    - 200 token overlap (context preservation)
    - Character-based splitting (4 chars ≈ 1 token)
    
    Proven in ARIA production: 3 days, 100% success rate
    """
    
    def __init__(
        self,
        chunk_tokens: int = 3000,      # ARIA standard
        overlap_tokens: int = 200,     # ARIA standard
        chars_per_token: int = 4       # Standard approximation
    ):
        """
        Initialize RecursiveCharacterTextSplitter with ARIA config
        
        Args:
            chunk_tokens: Target tokens per chunk (ARIA: 3000)
            overlap_tokens: Token overlap between chunks (ARIA: 200)
            chars_per_token: Character-to-token ratio (standard: 4)
        """
        chunk_size = chunk_tokens * chars_per_token     # 3000 × 4 = 12000 chars
        chunk_overlap = overlap_tokens * chars_per_token  # 200 × 4 = 800 chars
        
        logger.info(f"🔧 Initializing RecursiveCharacterTextSplitter (ARIA Pattern)...")
        logger.info(f"   Chunk size: {chunk_tokens} tokens ({chunk_size} chars)")
        logger.info(f"   Overlap: {overlap_tokens} tokens ({chunk_overlap} chars)")
        logger.info(f"   Expected chunks for Niveau 1.pdf: ~17 (was 204 with HierarchicalChunker)")
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.chunk_tokens = chunk_tokens
        self.overlap_tokens = overlap_tokens
        
        logger.info("✅ RecursiveCharacterTextSplitter initialized (ARIA Pattern)")
    
    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        filename: str,
        upload_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a DoclingDocument using ARIA strategy
        
        Args:
            docling_doc: DoclingDocument from converter
            filename: Original filename
            upload_id: Upload ID
            
        Returns:
            List of chunks with text + metadata
        """
        logger.info(f"[{upload_id}] 🔪 Starting chunking (ARIA Pattern): {filename}")
        
        # Extract text from DoclingDocument
        doc_text = docling_doc.export_to_markdown()
        
        # Split using RecursiveCharacterTextSplitter
        chunk_texts = self.splitter.split_text(doc_text)
        
        logger.info(f"[{upload_id}] ✅ Created {len(chunk_texts)} semantic chunks (ARIA: ~17 expected)")
        
        # Format chunks for RAG pipeline
        formatted_chunks = []
        for i, chunk_text in enumerate(chunk_texts):
            formatted_chunk = {
                "index": i,
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "upload_id": upload_id,
                    "chunk_index": i,
                    "total_chunks": len(chunk_texts),
                    "chunk_tokens": len(chunk_text.split()),  # Approximate
                    "chunking_strategy": "ARIA RecursiveCharacterTextSplitter"
                }
            }
            formatted_chunks.append(formatted_chunk)
        
        # Log statistics
        token_counts = [len(c["text"].split()) for c in formatted_chunks]
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)
            
            logger.info(f"[{upload_id}] 📊 Chunking stats (ARIA Pattern):")
            logger.info(f"   Average tokens: {avg_tokens:.0f} (expected: ~{self.chunk_tokens})")
            logger.info(f"   Token range: {min_tokens}-{max_tokens}")
            logger.info(f"   Total chunks: {len(formatted_chunks)} (expected: ~17 for Niveau 1.pdf)")
        
        return formatted_chunks


# Singleton instance
_chunker_instance: Optional[DocumentChunker] = None


def get_chunker() -> DocumentChunker:
    """
    Get or create singleton chunker (ARIA Pattern)
    """
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = DocumentChunker()
    return _chunker_instance
```

**Changes:**
1. Replace `HierarchicalChunker` with `RecursiveCharacterTextSplitter`
2. Use ARIA's exact configuration (3000 tokens, 200 overlap)
3. Extract markdown from DoclingDocument
4. Split with proven LangChain splitter

---

## 🎯 WHY THIS FIXES THE PROBLEM

### HierarchicalChunker (Current - BROKEN)
```
- Uses internal hierarchical logic
- IGNORES max_tokens/min_tokens parameters
- Creates 204 micro-chunks (18 tokens avg!)
- Not suitable for our use case
```

### RecursiveCharacterTextSplitter (ARIA - PROVEN)
```
- Respects chunk_size parameter
- Creates consistent chunks (~3000 tokens)
- 200-token overlap for context
- Proven in ARIA production (100% success)
```

---

## ⏱️ IMPLEMENTATION TIMELINE

**Immediate (15 minutes):**

1. **Modify document_chunker.py** (10 min)
   - Replace import
   - Replace class implementation
   - Use ARIA pattern exactly

2. **Rebuild + Test** (5 min)
   - Rebuild backend
   - Quick test upload
   - Verify ~17 chunks created

---

## 📊 EXPECTED RESULTS AFTER FIX

```
Niveau 1.pdf:
├─ Chunks: ~17 (currently 204)
├─ Avg chunk size: ~3000 tokens (currently 18)
├─ Processing time: ~3 minutes (currently 36 min)
└─ Quality: Better (more context per chunk)
```

---

## 🚀 NEXT STEPS

**Immediate:**
1. Stop current upload (already timeout)
2. Implement RecursiveCharacterTextSplitter
3. Rebuild backend
4. Test with Niveau 1.pdf
5. Validate 12× speedup

**Expected:** ✅ 17 chunks, 3 minutes, ARIA pattern validated

---

**Status:** 🔴 **URGENT REVISION REQUIRED**  
**Issue:** HierarchicalChunker doesn't support token limits  
**Solution:** Use ARIA's RecursiveCharacterTextSplitter (proven)  
**Time:** 15 minutes to fix + 5 minutes to test

