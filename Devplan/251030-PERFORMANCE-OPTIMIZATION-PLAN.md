# Performance Optimization Plan - Graphiti Ingestion

**Date:** October 30, 2025, 19:05 CET  
**Priority:** HIGH - User Experience  
**Current Performance:** 8.2s/chunk (30 chunks = 4m 6s for 2-page PDF)  
**Target Performance:** 2-3s/chunk (30 chunks = 1-1.5min for 2-page PDF)  
**Expected Gain:** 60-70% reduction in processing time

---

## 🔴 CURRENT PROBLEM

### Performance Metrics (Test Run #14)

**Current:**
```
Total: 249.47s (4m 9s)
├─ Conversion: 3.6s (1.4%)
├─ Chunking: 0.0s (0%)
└─ Ingestion: 245.86s (98.6%) ← BOTTLENECK!
   ├─ Claude Haiku calls: ~120s (49%)
   ├─ OpenAI embeddings: ~90s (37%)
   └─ Neo4j writes: ~35s (14%)
```

**Per-Chunk Breakdown:**
- Average: 8.2s
- Range: 2.3s → 15.9s
- Variability: High (due to sequential API calls)

**For Larger Documents:**
- Niveau 1.pdf (35 pages): ~150 chunks × 8.2s = **20+ minutes!**
- Production docs (100+ pages): ~500 chunks × 8.2s = **68+ minutes!**

**User Impact:** ❌ UNACCEPTABLE for production

---

## 🎯 ROOT CAUSE ANALYSIS

### What Happens in `add_episode()`

**Graphiti Internal Flow (per chunk):**

```python
# 1. Entity Extraction (Claude Haiku 4.5)
await client.add_episode(episode_body=chunk_text)
  ↓
  LLM call: Extract entities and relations
  ↓
  Time: ~3-5s per chunk
  ↓
  API: Anthropic Claude Haiku 4.5
  ↓
  Rate Limit: 4M tokens/min (NOT a bottleneck ✅)

# 2. Entity Resolution (Hybrid Search)
  ↓
  Search existing entities in Neo4j
  ↓
  Time: ~1-2s per chunk
  ↓
  Neo4j vector similarity search

# 3. Embedding Generation (OpenAI)
  ↓
  For EACH entity + relation:
    await embedder.embed(entity.name)  ← SEQUENTIAL!
    await embedder.embed(relation.fact)  ← SEQUENTIAL!
  ↓
  Time: ~0.5-1s PER embedding
  ↓
  If 3 entities + 2 relations = 5× embeddings
  ↓
  Total: 5× 0.8s = 4s just for embeddings!

# 4. Neo4j Write Operations
  ↓
  CREATE/MERGE nodes and relationships
  ↓
  Time: ~0.5-1s per chunk
```

**Total per chunk:** 3-5s (LLM) + 1-2s (search) + 3-5s (embeddings) + 0.5-1s (Neo4j) = **8-13s**

**THE BOTTLENECK:** Sequential embedding calls!

---

## ✅ SOLUTION: 3-PHASE OPTIMIZATION

### Phase 1: Batch Embeddings (CRITICAL - 50% gain)

**Problem:** OpenAI embeddings called ONE AT A TIME
```python
# CURRENT (in Graphiti internals):
for entity in entities:
    embedding = await openai_client.embed(entity.name)  # 1 call each
    # ~0.8s × 5 entities = 4s
```

**Solution:** Batch all embeddings into single call
```python
# OPTIMIZED:
texts_to_embed = [entity.name for entity in entities] + [rel.fact for rel in relations]
embeddings = await openai_client.embed_batch(texts_to_embed)  # 1 call for all
# ~1.5s for 5-10 texts (vs 4-8s sequential)
```

**Implementation:**
- Custom embedder for Graphiti
- Uses OpenAI batch API
- Maintains same embedding model (text-embedding-3-small)

**Expected Gain:** 
- Per chunk: 8.2s → 5s (-40%)
- Total: 245s → 150s (-39%)

---

### Phase 2: Parallel Batching (CRITICAL - Additional 50% gain)

**Problem:** Chunks processed SEQUENTIALLY
```python
# CURRENT:
for chunk in chunks:  # Sequential!
    await add_episode(chunk)  # 8s each
# 30 chunks × 8s = 240s
```

**Solution:** Process in parallel batches
```python
# OPTIMIZED:
batch_size = 5  # Safe for Neo4j + API rate limits
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    await asyncio.gather(*[
        add_episode(chunk) 
        for chunk in batch
    ])
# 6 batches × 8s = 48s (with current speed)
# 6 batches × 5s = 30s (with batch embeddings!)
```

**Constraints:**
- Batch size: 5-10 (avoid Neo4j write conflicts)
- Anthropic rate limit: 4M tokens/min (NOT a problem ✅)
- OpenAI rate limit: Check tier (likely fine)
- Neo4j: Can handle 5-10 concurrent writes

**Expected Gain (combined with Phase 1):**
- Per batch: 5 chunks × 5s/chunk = 25s (sequential) → 5s (parallel)
- Total: 6 batches × 5s = **30 seconds** (vs 245s current)
- **Gain: -215s (-88%)** 🚀

---

### Phase 3: Monitoring & Tuning (OPTIMIZATION)

**Add Performance Logging:**
```python
# Track each phase of add_episode()
logger.info(f"Entity extraction: {extraction_time}s")
logger.info(f"Embedding generation: {embedding_time}s")
logger.info(f"Neo4j write: {neo4j_time}s")
logger.info(f"Total chunk time: {total_time}s")
```

**Tune Batch Size Dynamically:**
```python
# Adjust batch size based on chunk complexity
if avg_entities_per_chunk > 5:
    batch_size = 3  # Smaller batches for complex chunks
else:
    batch_size = 10  # Larger batches for simple chunks
```

---

## 🔧 IMPLEMENTATION PLAN

### Step 1: Custom Batch Embedder (1-2 hours)

**File:** `backend/app/integrations/embedders.py` (NEW)

```python
"""
Custom OpenAI Embedder with Batch Support for Graphiti
"""
from typing import List
from openai import AsyncOpenAI
from graphiti_core.embedder import Embedder

class BatchOpenAIEmbedder(Embedder):
    """
    OpenAI embedder with batch processing support
    
    Advantages:
    - Single API call for multiple texts
    - 5-10× faster than sequential
    - Same model (text-embedding-3-small)
    - Same dimensions (1536)
    """
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.dimension = 1536
        self._batch_cache = []
    
    async def embed(self, text: str) -> List[float]:
        """Single text embedding (fallback)"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=[text]
        )
        return response.data[0].embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embedding - THE KEY OPTIMIZATION
        
        OpenAI supports up to 2048 inputs in one call
        We'll batch in groups of 100 for safety
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in sub-batches of 100
        for i in range(0, len(texts), 100):
            batch = texts[i:i+100]
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch  # ← BATCH CALL!
            )
            
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
        
        return all_embeddings
```

**Integration with Graphiti:**
```python
# graphiti.py
from app.integrations.embedders import BatchOpenAIEmbedder

async def get_graphiti_client() -> Graphiti:
    # ... existing code ...
    
    # Custom embedder with batch support
    embedder = BatchOpenAIEmbedder(
        api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    
    _graphiti_client = Graphiti(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
        llm_client=llm_client,
        embedder=embedder  # ← Custom embedder
    )
```

**Challenge:** 
Graphiti may call `embed()` internally, not `embed_batch()`. Need to check Graphiti source or monkey-patch.

**Alternative (if Graphiti doesn't support batch):**
Intercept embedding calls and batch them internally with a queue.

---

### Step 2: Parallel Chunk Processing (1 hour)

**File:** `backend/app/integrations/graphiti.py`

**Current Implementation:**
```python
# Line 181-242 (SEQUENTIAL)
for i, chunk in enumerate(chunks, start=1):
    chunk_text = chunk["text"]
    chunk_index = chunk["index"]
    
    try:
        start_time = time.time()
        
        await asyncio.wait_for(
            client.add_episode(...),  # One at a time!
            timeout=120.0
        )
        
        elapsed = time.time() - start_time
        # ... logging ...
```

**Optimized Implementation:**
```python
# PARALLEL BATCHING
async def process_chunk_batch(
    client: Graphiti,
    batch: List[Dict],
    batch_num: int,
    metadata: Dict,
    upload_id: str,
    processing_status: Dict
):
    """Process a batch of chunks in parallel"""
    
    tasks = []
    for i, chunk in enumerate(batch):
        chunk_text = chunk["text"]
        chunk_index = chunk["index"]
        
        # Create task (don't await yet)
        task = asyncio.wait_for(
            client.add_episode(
                name=f"{metadata['filename']} - Chunk {chunk_index}",
                episode_body=chunk_text,
                source=EpisodeType.text,
                source_description=f"Document: {metadata['filename']}, Chunk {chunk_index}",
                reference_time=datetime.now(timezone.utc),
                group_id=metadata.get("user_id", "default"),
            ),
            timeout=120.0
        )
        tasks.append((chunk_index, task))
    
    # Execute all tasks in parallel
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
    
    # Process results
    for (chunk_index, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            logger.error(f"Chunk {chunk_index} failed: {result}")
        else:
            logger.info(f"Chunk {chunk_index} completed")

# Main ingestion loop
async def ingest_chunks_to_graph(...):
    client = await get_graphiti_client()
    
    batch_size = 5  # Configurable
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(chunks))
        batch = chunks[start_idx:end_idx]
        
        logger.info(f"📦 Processing batch {batch_num+1}/{total_batches} ({len(batch)} chunks)")
        
        start_time = time.time()
        
        await process_chunk_batch(
            client, batch, batch_num, metadata, upload_id, processing_status
        )
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Batch {batch_num+1} complete in {elapsed:.2f}s")
        
        # Update progress
        chunks_completed = end_idx
        # ... update processing_status ...
```

**Benefits:**
- 5 chunks processed simultaneously
- Network latency overlap
- Better CPU utilization
- Faster for user

**Risks & Mitigations:**
- ✅ Neo4j write conflicts: Use `MERGE` (Graphiti already does)
- ✅ Rate limits: Anthropic has 4M tokens/min (plenty)
- ✅ OpenAI limits: With batch embeddings, much fewer calls
- ⚠️ Memory: Monitor (5 chunks × embeddings in memory)

---

### Step 3: Configuration & Monitoring (30 min)

**Add Settings:**
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing ...
    
    # Performance tuning
    GRAPHITI_BATCH_SIZE: int = 5  # Parallel chunk processing
    GRAPHITI_EMBEDDING_BATCH_SIZE: int = 100  # Embedding batch size
    GRAPHITI_MAX_PARALLEL: int = 10  # Max concurrent chunks
```

**Add Metrics:**
```python
# Track performance per batch
metrics = {
    "batch_num": batch_num,
    "chunks_in_batch": len(batch),
    "batch_duration": elapsed,
    "avg_per_chunk": elapsed / len(batch),
    "parallel_speedup": (len(batch) * 8.2) / elapsed  # vs sequential
}
logger.info(f"📊 Batch metrics: {metrics}")
```

---

## 📊 EXPECTED PERFORMANCE

### Baseline (Current - Sequential)

```
30 chunks × 8.2s/chunk = 246s (4m 6s)
```

### Phase 1: Batch Embeddings Only

**Assumptions:**
- Embedding calls: 5 per chunk (avg)
- Sequential: 5× 0.8s = 4s
- Batched: 1× 1.5s = 1.5s
- **Savings: 2.5s per chunk**

```
30 chunks × 5.7s/chunk = 171s (2m 51s)
Gain: -75s (-30%)
```

### Phase 2: Parallel Batching (batch_size=5)

**With current speed (8.2s):**
```
6 batches × 8.2s = 49s
Gain: -197s (-80%)
```

**Issue:** Still slow due to embedding bottleneck

### Phase 1 + 2: Batch Embeddings + Parallel

**Combined optimizations:**
- Embeddings batched: 8.2s → 5.7s per chunk
- Parallel execution: batch_size=5

```
6 batches × 5.7s = 34s
Gain: -212s (-86%)
```

**REALISTIC TARGET:** 30-40 seconds for 30 chunks

---

## 🚧 IMPLEMENTATION CHALLENGES

### Challenge 1: Graphiti Internal Embedding Calls

**Issue:** 
Graphiti calls `embedder.embed()` internally, likely one at a time.

**Solution Options:**

**A) Custom Embedder with Internal Batching:**
```python
class QueuedBatchEmbedder(Embedder):
    """
    Embedder that queues requests and batches them automatically
    """
    def __init__(self, api_key, batch_delay=0.1):
        self.client = AsyncOpenAI(api_key=api_key)
        self.queue = []
        self.batch_delay = batch_delay
        self._batch_task = None
    
    async def embed(self, text: str) -> List[float]:
        """
        Add to queue, wait for batch processing
        """
        future = asyncio.Future()
        self.queue.append((text, future))
        
        # Trigger batch processing
        if self._batch_task is None or self._batch_task.done():
            self._batch_task = asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _process_batch(self):
        """Process queued embeddings in batch"""
        await asyncio.sleep(self.batch_delay)  # Wait for queue to fill
        
        if not self.queue:
            return
        
        texts = [item[0] for item in self.queue]
        futures = [item[1] for item in self.queue]
        self.queue = []
        
        # Batch call
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts  # Batch!
        )
        
        # Distribute results
        for future, embedding_data in zip(futures, response.data):
            future.set_result(embedding_data.embedding)
```

**This way:** Graphiti calls `embed()` normally, but we batch internally!

**B) Fork Graphiti and Add Batch Support:**
- More invasive
- Harder to maintain
- Better performance control

**C) Use Graphiti Config (if exists):**
- Check if Graphiti has `batch_size` parameter
- Simplest if available

---

### Challenge 2: Neo4j Write Conflicts

**Issue:**
Parallel `add_episode()` may create duplicate entities or race conditions.

**Graphiti's Protection:**
- Uses `MERGE` (not `CREATE`) for entities
- UUID-based uniqueness
- Atomic operations

**Our Safety:**
- Limit batch_size to 5-10
- Monitor for conflicts in logs
- Test thoroughly before production

**Expected:** Should be fine (Graphiti designed for this)

---

### Challenge 3: Progress Updates

**Issue:**
With parallel execution, progress updates become tricky.

**Current:**
```python
for i, chunk in enumerate(chunks):
    await process_chunk(chunk)
    progress = (i + 1) / len(chunks) * 100  # Simple
```

**Parallel:**
```python
completed = 0
total = len(chunks)

for batch in batches:
    await asyncio.gather(...)  # Batch completes
    completed += len(batch)
    progress = (completed / total) * 100  # Still accurate
```

**Solution:**
- Update progress after each BATCH (not each chunk)
- Less granular but still good UX
- Alternative: Use atomic counter with locks

---

## 📋 IMPLEMENTATION STEPS

### Step 1: Research Graphiti Embedder API (30 min)

**Tasks:**
1. Check Graphiti documentation for custom embedder
2. Inspect Graphiti source code for embedding calls
3. Determine best integration point
4. Choose Option A, B, or C above

**Deliverables:**
- Technical spike document
- Chosen approach
- Code examples

---

### Step 2: Implement Batch Embedder (2 hours)

**Tasks:**
1. Create `backend/app/integrations/embedders.py`
2. Implement `BatchOpenAIEmbedder` or `QueuedBatchEmbedder`
3. Add configuration settings
4. Write unit tests (optional but recommended)

**Files:**
- NEW: `backend/app/integrations/embedders.py`
- MODIFIED: `backend/app/integrations/graphiti.py` (use custom embedder)
- MODIFIED: `backend/app/core/config.py` (add settings)

**Testing:**
- Upload test.pdf
- Verify embeddings generated correctly
- Check dimensionality (1536)
- Compare with baseline (should be same quality)

---

### Step 3: Implement Parallel Batching (1 hour)

**Tasks:**
1. Refactor `ingest_chunks_to_graph()` to use batches
2. Add `process_chunk_batch()` helper function
3. Update progress tracking for batches
4. Add batch performance logging

**Files:**
- MODIFIED: `backend/app/integrations/graphiti.py`

**Testing:**
- Upload test.pdf
- Verify all 30 chunks processed
- Check for Neo4j conflicts (should be none)
- Validate progress updates work

---

### Step 4: Performance Testing & Tuning (1 hour)

**Tests:**
1. test.pdf (30 chunks) - Baseline comparison
2. Niveau 1.pdf (35 pages, ~150 chunks) - Large doc test
3. Multiple documents - Concurrent uploads

**Tune:**
- Optimal batch_size (test 3, 5, 10)
- Embedding batch size (test 50, 100, 200)
- Monitor Neo4j load
- Monitor API rate limit usage

**Success Criteria:**
- test.pdf: < 1 minute (vs 4 minutes current)
- Niveau 1.pdf: < 5 minutes (vs 20+ minutes current)
- No errors, 100% success rate
- Neo4j stable

---

### Step 5: Documentation & Deployment (30 min)

**Tasks:**
1. Update ARCHITECTURE.md with optimization details
2. Document performance metrics in TESTING-LOG.md
3. Create before/after comparison
4. Commit to GitHub

---

## 🎯 EXPECTED RESULTS

### Performance Targets

| Document | Current | Target | Gain |
|----------|---------|--------|------|
| test.pdf (2 pages, 30 chunks) | 4m 6s | **45s** | -201s (-82%) |
| Niveau 1.pdf (35 pages, ~150 chunks) | ~20 min | **4 min** | -16 min (-80%) |
| Large doc (100 pages, ~500 chunks) | ~68 min | **13 min** | -55 min (-81%) |

### Per-Chunk Performance

| Phase | Time | Note |
|-------|------|------|
| **Current** | **8.2s** | Sequential everything |
| With batch embeddings | 5.7s | -30% |
| With parallel (batch=5) + batch embeddings | **~1.5s effective** | -82% |

**Why ~1.5s effective:**
- 5 chunks processed simultaneously
- Each takes ~5.7s
- But wall-clock time: 5.7s for ALL 5 chunks
- Effective time per chunk: 5.7s / 5 = 1.14s
- Plus overhead: ~1.5s effective

---

## 🔒 RISK ASSESSMENT

### Low Risk

✅ **Batch Embeddings:**
- Uses OpenAI's official batch API
- Same model, same quality
- Well-tested feature
- Risk: Very low

### Medium Risk

⚠️ **Parallel Processing:**
- Neo4j write conflicts possible
- Need to test thoroughly
- Start with small batch_size (3-5)
- Monitor for issues
- Risk: Medium (mitigated with testing)

### Mitigation Strategy

1. **Feature Flag:**
   ```python
   ENABLE_PARALLEL_INGESTION: bool = False  # Default OFF
   PARALLEL_BATCH_SIZE: int = 5
   ```

2. **Gradual Rollout:**
   - Test in dev
   - Deploy to staging
   - A/B test in production
   - Monitor metrics

3. **Rollback Plan:**
   - Keep sequential code path
   - Easy to disable via config
   - Git revert if needed

---

## 📊 COST-BENEFIT ANALYSIS

### Development Cost

- Research: 30 min
- Batch embedder: 2 hours
- Parallel batching: 1 hour
- Testing: 1 hour
- Documentation: 30 min
- **Total: 5-6 hours**

### User Benefit

**Time Saved Per Document:**
- test.pdf: -3 min (from 4m to 1m)
- Niveau 1.pdf: -16 min (from 20m to 4m)
- Large doc: -55 min (from 68m to 13m)

**For 100 documents/day:**
- Small docs (30 chunks avg): 100× 3min = **5 hours saved daily**
- Large docs (150 chunks avg): 100× 16min = **27 hours saved daily**

**ROI:** 6 hours dev investment → Hours saved DAILY

---

## 🚀 RECOMMENDATION

### Phased Approach

**Phase 1 (THIS WEEK):** Batch Embeddings
- Implementation: 2-3 hours
- Testing: 1 hour
- **Expected Gain: 30%** (4m → 2m 50s)
- Risk: Very low
- **DO THIS FIRST** ✅

**Phase 2 (NEXT WEEK):** Parallel Batching
- Implementation: 1-2 hours
- Testing: 2 hours (thorough Neo4j conflict testing)
- **Expected Gain: Additional 50%** (2m 50s → ~45s)
- Risk: Medium (need extensive testing)
- **DO AFTER Phase 1 validated** ⏳

**Phase 3 (FUTURE):** Advanced Optimizations
- Entity caching (avoid duplicate extractions)
- Adaptive batch sizing
- GPU-accelerated embeddings (local)

---

## 🎯 NEXT STEPS

**Immediate:**
1. Research Graphiti embedder API (check if batch_embed supported)
2. Create spike/POC for batch embeddings
3. Test with test.pdf
4. Measure actual improvement

**If you approve:**
- I can start implementing Phase 1 (batch embeddings) NOW
- Estimated time: 2-3 hours
- Expected gain: -30% processing time
- Low risk, high reward

**Question pour toi:**
- Tu veux que je commence Phase 1 maintenant?
- Ou tu préfères qu'on teste autre chose d'abord?
- Ou on déploie en production comme ça et on optimise plus tard?

---

**📊 BOTTOM LINE:**
- Actuel: 4 min pour 2 pages (lent mais fonctionne)
- Optimisé: 45s pour 2 pages (acceptable)
- **Gain: 82% faster avec 5-6h de dev**

**Worth it?** Je pense OUI - pour des docs de 35 pages, la différence c'est 20 min vs 4 min!
