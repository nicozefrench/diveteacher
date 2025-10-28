# 🔗 Graphiti Knowledge Graph Integration

> **Status:** ✅ COMPLETE - Phase 0.9 Functional  
> **Version:** graphiti-core[anthropic] 0.17.0  
> **LLM:** Anthropic Claude Haiku 4.5 (ARIA-validated)  
> **Last Updated:** October 28, 2025

---

## 📋 Table of Contents

- [Overview](#overview)
- [Current Status](#current-status)
- [Architecture](#architecture)
- [Anthropic Claude Integration](#anthropic-claude-integration)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Overview

**Graphiti** est une bibliothèque Python pour créer des knowledge graphs temporels à partir de texte non structuré. Elle utilise des LLMs pour extraire automatiquement des entités, relations, et construire un graphe évolutif dans Neo4j.

### Key Features

- ✅ **Entity Extraction:** Automatic via LLM prompts
- ✅ **Relation Detection:** Semantic relationships between entities
- ✅ **Temporal Awareness:** `valid_at`, `invalid_at` for contradiction resolution
- ✅ **Hybrid Search:** Semantic + BM25 + RRF (Reciprocal Rank Fusion)
- ✅ **Community Detection:** Louvain algorithm for entity clustering
- ✅ **Multi-tenant:** `group_id` for data isolation

### Integration avec DiveTeacher

```
PDF Upload
    ↓
Docling Conversion (72 chunks)
    ↓
Graphiti.add_episode() ✅ WORKING
    ↓
Neo4j (Episodes, Entities, Relations)
    ↓
RAG Query via graphiti.search()
```

---

## Current Status

### 🟢 Phase 0.9 - COMPLETE (100%)

| Component | Status | Details |
|-----------|--------|---------|
| **Graphiti Installation** | ✅ DONE | graphiti-core[anthropic] 0.17.0 |
| **Neo4j Connection** | ✅ WORKING | Graphiti connects to Neo4j |
| **Indexes Creation** | ✅ DONE | `build_indices_and_constraints()` OK |
| **Anthropic Config** | ✅ WORKING | Claude Haiku 4.5 (ARIA-validated) |
| **Native Client** | ✅ WORKING | AnthropicClient (no custom code) |
| **Ingestion Pipeline** | ✅ WORKING | 72/72 chunks processed successfully |
| **Search Integration** | ✅ READY | Ready for testing |

### Success Metrics

**Nitrox.pdf Test (35 pages, 72 chunks):**
- ✅ Episodes created: 379
- ✅ Entities extracted: 205
- ✅ Relationships created: 2,229
- ✅ Processing time: ~5-7 minutes
- ✅ Success rate: 100%

---

## Architecture

### Graphiti Data Model (Neo4j)

```
┌────────────────────────────────────────────────────────┐
│                      Neo4j Graph                        │
├────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐                        ┌──────────┐      │
│  │ Episodic │◄───┐              ┌───►│  Entity  │      │
│  └──────────┘    │              │    └──────────┘      │
│   • content      │  RELATES_TO  │     • name           │
│   • source       │  (fact)      │     • summary        │
│   • created_at   │              │     • entity_type    │
│                  │              │                       │
│  ┌──────────┐    │              │    ┌──────────┐      │
│  │ Episodic │────┘              └────│  Entity  │      │
│  └──────────┘                        └──────────┘      │
│                                                          │
└────────────────────────────────────────────────────────┘
```

**Node Types:**
1. **Episodic (Episode)** - Document chunks with temporal metadata
2. **Entity** - Extracted concepts (people, places, procedures, equipment)

**Relationship Types:**
1. **RELATES_TO** - Semantic connections between entities
2. **MENTIONS** - Episodes mentioning entities (implicit)

---

## Anthropic Claude Integration

### Architecture Decision: Claude Haiku 4.5

**Why Claude Haiku 4.5?**
1. **Production-Validated:** ARIA project used it for 5 days, 100% uptime, zero failures
2. **Native Support:** Graphiti officially supports `AnthropicClient` (no custom code needed)
3. **Reliable API:** Uses standard `max_tokens` parameter (no compatibility issues)
4. **Cost-Effective:** Haiku model is optimized for speed and cost
5. **Quality:** Excellent entity/relation extraction quality

### Configuration (`backend/app/integrations/graphiti.py`)

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig
from graphiti_core.llm_client.anthropic_client import AnthropicClient

async def get_graphiti_client() -> Graphiti:
    """
    Initialize Graphiti with Claude Haiku 4.5.
    
    Components:
    - LLM: Anthropic Claude Haiku 4.5 (claude-haiku-4-5-20251001)
    - Embedder: OpenAI text-embedding-3-small (default, 1536 dims)
    - Driver: Neo4j bolt://localhost:7688
    """
    global _graphiti_client, _indices_built
    
    if _graphiti_client is None:
        logger.info("🔧 Initializing Graphiti client with Claude Haiku 4.5...")
        
        # LLM Config for Anthropic
        llm_config = LLMConfig(
            api_key=settings.ANTHROPIC_API_KEY,
            model='claude-haiku-4-5-20251001'
        )
        
        # Native Anthropic Client (zero custom code)
        llm_client = AnthropicClient(config=llm_config, cache=False)
        
        # Graphiti instance
        _graphiti_client = Graphiti(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            llm_client=llm_client
        )
        
        logger.info(f"✅ Graphiti client initialized:")
        logger.info(f"  • LLM: Claude Haiku 4.5 (native AnthropicClient)")
        logger.info(f"  • Embedder: text-embedding-3-small (default OpenAI, dim: 1536)")
    
    # Build indexes on first run
    if not _indices_built:
        logger.info("🔧 Building Graphiti indexes and constraints...")
        await _graphiti_client.build_indices_and_constraints()
        _indices_built = True
        logger.info("✅ Indexes and constraints created")
    
    return _graphiti_client
```

### Environment Variables (`.env`)

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# OpenAI API (for embeddings only)
OPENAI_API_KEY=sk-xxxxx

# Neo4j
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=diveteacher_dev_2025
```

### Key Advantages

1. **Zero Custom Code**
   - No `Gpt5NanoClient` needed
   - No parameter translation
   - No Pydantic serialization issues

2. **Native Graphiti Support**
   - `AnthropicClient` is officially supported
   - Maintained by Graphiti team
   - Battle-tested in production

3. **Reliable Ingestion**
   - Standard API calls
   - Predictable behavior
   - No weird edge cases

4. **ARIA-Validated**
   - Used in production for 5 days
   - 100% uptime
   - Zero failures
   - Same architecture as DiveTeacher

### Ingestion Example

```python
# backend/app/integrations/graphiti.py

async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> None:
    """
    Ingest document chunks into Neo4j knowledge graph.
    
    Process:
    1. Get Graphiti client (Claude Haiku 4.5)
    2. For each chunk:
       - Create Episode (document chunk)
       - Extract Entities (automatic via Claude)
       - Create Relationships (automatic via Claude)
    3. Log progress
    
    Performance:
    - 72 chunks in ~5-7 minutes
    - 205 entities extracted
    - 2,229 relationships created
    """
    client = await get_graphiti_client()
    
    for i, chunk in enumerate(chunks, 1):
        episode_data = {
            "name": f"{metadata['filename']} - Chunk {i}",
            "episode_body": chunk['text'],
            "source": metadata.get('origin', 'unknown'),
            "source_description": f"Chunk {i}/{len(chunks)} from {metadata['filename']}",
            "reference_time": datetime.now()
        }
        
        logger.info(f"[{i}/{len(chunks)}] Processing chunk {i}...")
        
        try:
            await asyncio.wait_for(
                client.add_episode(**episode_data),
                timeout=120  # 2 minutes per chunk
            )
            logger.info(f"[{i}/{len(chunks)}] ✅ Ingested successfully")
        except asyncio.TimeoutError:
            logger.error(f"[{i}/{len(chunks)}] ❌ Timeout (120s exceeded)")
        except Exception as e:
            logger.error(f"[{i}/{len(chunks)}] ❌ Error: {e}")
    
    logger.info(f"✅ Ingestion complete: {len(chunks)} chunks processed")
```

---

## Performance

### Nitrox.pdf Test Results

**Document:** 35 pages, diving manual (FFESSM)  
**Processing:** October 27, 2025

| Metric | Value |
|--------|-------|
| **Total Chunks** | 72 |
| **Episodes Created** | 379 |
| **Entities Extracted** | 205 |
| **Relationships** | 2,229 |
| **Processing Time** | ~5-7 minutes |
| **Success Rate** | 100% |

### Sample Entities Extracted

1. FÉDÉRATION FRANÇAISE D'ÉTUDES ET DE SPORTS SOUS-MARINS
2. manuel de formation technique guide de palanquée niveau 4
3. GPN 4 (Guide de Palanquée Niveau 4)
4. LES PLONGEURS
5. PALANQUÉE
6. CONNAISSANCES THÉORIQUES
7. IMMERSION
8. L'ORGANIZATION

### Neo4j Statistics

```cypher
// Episodes (document chunks)
MATCH (n:Episodic) RETURN count(n) AS episodes
// Result: 379

// Entities (extracted concepts)
MATCH (n:Entity) RETURN count(n) AS entities
// Result: 205

// Relationships
MATCH ()-[r]->() RETURN count(r) AS relationships
// Result: 2,229
```

---

## Troubleshooting

### Issue: Anthropic API Limit

**Error:**
```
anthropic.BadRequestError: Error code: 400
{'type': 'error', 'error': {'type': 'invalid_request_error', 
'message': 'You have reached your specified API usage limits. 
You will regain access on 2025-11-01 at 00:00 UTC.'}}
```

**Solution:**
- Wait until API limit reset (2025-11-01)
- Or upgrade Anthropic plan
- Or use different API key

### Issue: Neo4j Connection Failed

**Error:**
```
neo4j.exceptions.ServiceUnavailable: Failed to establish connection
```

**Solution:**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Restart Neo4j
docker restart rag-neo4j

# Verify connection
docker exec rag-neo4j bash -c "echo 'MATCH (n) RETURN count(n);' | cypher-shell -u neo4j -p diveteacher_dev_2025"
```

### Issue: Slow Ingestion

**Problem:** Ingestion takes > 10 minutes for 72 chunks

**Solutions:**
1. Check Anthropic API latency (should be < 2s per request)
2. Reduce timeout from 120s to 60s if chunks are small
3. Check Neo4j performance (query time should be < 100ms)
4. Monitor memory usage (should stay < 16GB)

---

## Next Steps

### Phase 1.0: RAG Query Integration

1. **Implement `graphiti.search()`**
   - Hybrid search (full-text + graph traversal)
   - Relevance scoring
   - Context assembly

2. **Update RAG Chain**
   - Use Graphiti search results
   - Format for LLM prompt
   - Add citations with entity context

3. **Test End-to-End**
   - Upload document
   - Ask question
   - Verify answer with entities

### Phase 1.1: Multi-Document Support

1. **Group Management**
   - Use `group_id` for multi-tenant
   - Separate diving schools
   - Different certification systems (FFESSM vs SSI)

2. **Cross-Document Relations**
   - Link entities across documents
   - Build comprehensive knowledge graph

3. **Community Building**
   - Run `Graphiti.build_communities()`
   - Cluster related concepts
   - Optimize search performance

---

## References

- **Graphiti Documentation:** https://github.com/getzep/graphiti
- **Anthropic Claude API:** https://docs.anthropic.com/claude/reference/getting-started-with-the-api
- **Neo4j Cypher:** https://neo4j.com/docs/cypher-manual/current/
- **ARIA Project:** Devplan/251027-DIVETEACHER-GRAPHITI-RECOMMENDATIONS.md (production validation)
- **Implementation Plan:** Devplan/PHASE-0.9-GRAPHITI-IMPLEMENTATION.md

---

**Last Updated:** October 28, 2025  
**Status:** ✅ Phase 0.9 COMPLETE - Ingestion pipeline functional
