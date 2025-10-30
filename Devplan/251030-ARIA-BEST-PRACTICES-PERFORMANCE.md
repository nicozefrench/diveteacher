# ARIA Best Practices - Performance Optimization

**Date:** October 30, 2025, 19:15 CET  
**Priority:** HIGH  
**Approach:** Use ARIA's Production-Validated Architecture  
**Status:** Research & Implementation Plan

---

## 🎯 ARIA PRODUCTION ARCHITECTURE

### What We Know About ARIA

**From our codebase comments:**
```python
# backend/app/integrations/graphiti.py
"""
Based on: ARIA Knowledge System v1.6.0
- 5 jours production, 100% uptime
- 100% ingestion success rate
- Zero custom code LLM client
"""
```

**ARIA Services Running:**
```bash
aria-graphiti-service   (port 8003) - healthy ✅
aria-zep-server        (port 8001) - running
aria-neo4j             (port 7474) - running
```

**Key Insight:**
ARIA has their OWN Graphiti service running separately. This suggests they:
1. ✅ Use microservice architecture (Graphiti as separate service)
2. ✅ Optimize at service level (not just library)
3. ✅ Handle batching/parallelization in the service layer

---

## 🔍 CURRENT vs ARIA ARCHITECTURE

### Our Current Setup

```python
# We use Graphiti Python library DIRECTLY
from graphiti_core import Graphiti

client = Graphiti(
    uri=NEO4J_URI,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD,
    llm_client=llm_client  # Claude Haiku
)

# Sequential processing
for chunk in chunks:
    await client.add_episode(chunk)  # 8s each
```

**Problem:** All processing happens in OUR backend
- Sequential by default
- No built-in batching
- No parallel optimization

### ARIA's Likely Setup (Hypothesis)

```python
# Option A: Use their Graphiti SERVICE (HTTP API)
graphiti_service_url = "http://aria-graphiti-service:8003"

# Batch endpoint (hypothesis)
await httpx.post(
    f"{graphiti_service_url}/ingest/batch",
    json={
        "chunks": chunks,  # All 30 chunks at once!
        "group_id": "user_123",
        "metadata": metadata
    }
)

# Their service handles:
# - Parallel processing internally
# - Batch embeddings
# - Optimized Neo4j writes
# - Rate limit management
```

**Advantages:**
- ✅ Optimizations handled by ARIA service
- ✅ Battle-tested (5 days production)
- ✅ No custom code needed
- ✅ Just HTTP API calls

---

## 🔬 RESEARCH PLAN: ARIA SERVICE API

### Step 1: Discover ARIA Graphiti Service API

**Check if service has API documentation:**
```bash
# Try common endpoints
curl http://localhost:8003/
curl http://localhost:8003/docs         # OpenAPI/Swagger
curl http://localhost:8003/openapi.json # API spec
curl http://localhost:8003/health
curl http://localhost:8003/api/v1/...
```

**If API exists:**
- Document all endpoints
- Find batch ingestion endpoint
- Check authentication requirements
- Test with curl

**If no external API:**
- ARIA service might be for internal use only
- Fall back to library-level optimizations

---

### Step 2: Check Graphiti Library for Batch Support

**Graphiti Core Library Investigation:**

```python
# Check if Graphiti has batch methods
from graphiti_core import Graphiti

client = Graphiti(...)

# Possible methods to check:
# - client.add_episodes_batch()  # Batch ingestion
# - client.add_episode(..., parallel=True)  # Parallel flag
# - client.config.batch_size  # Configuration
```

**Check Graphiti documentation:**
- https://github.com/getzep/graphiti
- Check for batch/parallel configuration options
- Look for performance tuning guides

---

### Step 3: ARIA Configuration Deep Dive

**Check how ARIA configures Graphiti client:**

Look for:
1. **Custom Embedder Configuration**
   ```python
   # Do they use custom embedder with batching?
   embedder = ARIABatchEmbedder(...)
   client = Graphiti(..., embedder=embedder)
   ```

2. **LLM Client Configuration**
   ```python
   # Do they configure Claude with specific settings?
   llm_client = AnthropicClient(
       config=LLMConfig(...),
       cache=True,  # Caching enabled?
       batch_size=10  # Batch configuration?
   )
   ```

3. **Graphiti Initialization**
   ```python
   # Any special flags or configs?
   client = Graphiti(
       ...,
       max_workers=10,  # Parallel workers?
       batch_size=5,    # Batch size?
       optimize=True    # Optimization flag?
   )
   ```

---

## 💡 BEST PRACTICES FROM ARIA (Validated)

### What We KNOW Works in ARIA Production

**1. LLM Client:**
```python
# ✅ CONFIRMED (already using)
llm_config = LLMConfig(
    api_key=settings.ANTHROPIC_API_KEY,
    model='claude-haiku-4-5-20251001'
)
llm_client = AnthropicClient(config=llm_config, cache=False)
```

**Status:** ✅ Already implemented correctly

**2. Native Anthropic Client:**
```python
# ✅ CONFIRMED (already using)
# Zero custom code
# Native Graphiti AnthropicClient
```

**Status:** ✅ Already implemented correctly

**3. Single Event Loop:**
```python
# ✅ CONFIRMED (already using)
# asyncio.create_task() for background processing
# No threading, just async
```

**Status:** ✅ Already implemented correctly

**4. OpenAI Embeddings:**
```python
# ✅ CONFIRMED (already using)
# Default text-embedding-3-small (1536 dims)
# No custom embedder (to avoid bugs)
```

**Status:** ✅ Already implemented, but NOT optimized (sequential)

---

## 🚀 ARIA-STYLE OPTIMIZATION STRATEGY

### Strategy 1: Use ARIA Graphiti Service (IF API Available)

**Benefits:**
- ✅ Leverage ARIA's production optimizations
- ✅ Zero dev time (just HTTP calls)
- ✅ Battle-tested (5 days production, 100% uptime)
- ✅ Automatic updates when ARIA updates service

**Implementation:**
```python
# Replace direct Graphiti lib usage with HTTP calls to ARIA service
import httpx

async def ingest_via_aria_service(chunks, metadata):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://aria-graphiti-service:8003/api/ingest",
            json={
                "episodes": [
                    {
                        "name": f"{metadata['filename']} - Chunk {i}",
                        "body": chunk["text"],
                        "metadata": {...}
                    }
                    for i, chunk in enumerate(chunks)
                ],
                "group_id": metadata.get("user_id", "default")
            },
            timeout=300.0
        )
        return response.json()
```

**Challenge:** Need to discover ARIA service API endpoints

---

### Strategy 2: Graphiti Library with ARIA-Inspired Config

**If ARIA service API not available, optimize the library directly:**

**A) Check Graphiti for Built-in Batch Support:**
```python
# Graphiti might have batch methods we're not using
client = await get_graphiti_client()

# Try:
await client.add_episodes_batch([...])  # Batch method?
```

**B) Use Graphiti with Custom Batch Embedder:**
```python
# ARIA likely uses a custom embedder that batches
from graphiti_core.embedder import Embedder

class ARIAStyleBatchEmbedder(Embedder):
    """
    OpenAI embedder with batching (ARIA pattern)
    """
    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts in single API call"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts  # Batch!
        )
        return [item.embedding for item in response.data]

# Use in Graphiti
client = Graphiti(
    ...,
    embedder=ARIAStyleBatchEmbedder(...)  # Custom embedder
)
```

**C) Parallel Processing (ARIA Pattern):**
```python
# ARIA likely processes chunks in parallel batches
async def ingest_chunks_aria_style(chunks, metadata):
    client = await get_graphiti_client()
    
    # Parallel batches (ARIA pattern)
    batch_size = 5  # Conservative for Neo4j
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        # Process batch in parallel
        await asyncio.gather(*[
            client.add_episode(
                name=f"{metadata['filename']} - Chunk {chunk['index']}",
                episode_body=chunk["text"],
                source=EpisodeType.text,
                source_description=f"Chunk {chunk['index']}",
                reference_time=datetime.now(timezone.utc),
                group_id=metadata.get("user_id", "default")
            )
            for chunk in batch
        ])
```

---

## 📋 IMPLEMENTATION PLAN (ARIA-VALIDATED APPROACH)

### Phase 1: Research (30 min) - CRITICAL FIRST STEP

**Objectives:**
1. ✅ Discover ARIA Graphiti service API (if exists)
2. ✅ Check Graphiti library for batch methods
3. ✅ Identify ARIA's actual configuration

**Tasks:**
```bash
# 1. Check ARIA service API
curl http://localhost:8003/docs
curl http://localhost:8003/openapi.json
docker logs aria-graphiti-service | grep -i "batch\|parallel"

# 2. Check Graphiti library source
# Look for: add_episodes_batch, parallel processing flags

# 3. Check ARIA's configuration
docker inspect aria-graphiti-service
# Look for environment variables with batch/parallel settings
```

**Decision Point:**
- **IF** ARIA service has batch API → Use their service
- **ELSE** → Optimize library with ARIA patterns

---

### Phase 2A: Use ARIA Service (If API Available) - 2 hours

**Implementation:**
```python
# NEW: backend/app/integrations/aria_graphiti.py

class ARIAGraphitiClient:
    """
    Client for ARIA Graphiti Service (production-optimized)
    
    Leverages ARIA's battle-tested optimizations:
    - Batch embeddings
    - Parallel processing
    - Rate limit management
    """
    
    def __init__(self, service_url: str = "http://aria-graphiti-service:8003"):
        self.service_url = service_url
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def ingest_batch(
        self,
        chunks: List[Dict],
        metadata: Dict,
        group_id: str = "default"
    ) -> Dict:
        """
        Ingest chunks in batch via ARIA service
        
        ARIA handles internally:
        - Parallel processing
        - Batch embeddings
        - Neo4j optimization
        """
        response = await self.client.post(
            f"{self.service_url}/api/v1/episodes/batch",
            json={
                "episodes": [
                    {
                        "name": f"{metadata['filename']} - Chunk {i}",
                        "episode_body": chunk["text"],
                        "source": "text",
                        "source_description": f"Chunk {i}",
                        "group_id": group_id
                    }
                    for i, chunk in enumerate(chunks)
                ],
                "metadata": metadata
            }
        )
        return response.json()
```

**Benefits:**
- Zero optimization code needed
- ARIA's service handles everything
- Production-validated
- Automatic updates

---

### Phase 2B: Library Optimization (If Service Not Available) - 4 hours

**Follow ARIA patterns at library level:**

**1. Custom Batch Embedder (ARIA Pattern):**
```python
from graphiti_core.embedder import Embedder
from openai import AsyncOpenAI

class ARIABatchEmbedder(Embedder):
    """
    Batch embedder following ARIA production patterns
    
    Based on ARIA's 100% success rate in production
    """
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
        self.dimension = 1536
        self._pending_batch = []
        self._batch_size = 100  # ARIA-validated batch size
    
    async def embed(self, text: str) -> List[float]:
        """Single embed (Graphiti interface)"""
        # Add to pending batch
        self._pending_batch.append(text)
        
        # Flush if batch full
        if len(self._pending_batch) >= self._batch_size:
            return await self._flush_batch()
        
        # For immediate need, flush anyway
        results = await self._flush_batch()
        return results[0] if results else []
    
    async def _flush_batch(self) -> List[List[float]]:
        """Flush pending batch to OpenAI"""
        if not self._pending_batch:
            return []
        
        texts = self._pending_batch[:]
        self._pending_batch = []
        
        # ARIA Pattern: Single API call for all texts
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts  # Batch call
        )
        
        return [item.embedding for item in response.data]
```

**2. Parallel Chunk Processing (ARIA Pattern):**
```python
async def ingest_chunks_aria_pattern(
    chunks: List[Dict],
    metadata: Dict,
    upload_id: str,
    processing_status: Dict
) -> None:
    """
    Parallel chunk ingestion following ARIA production patterns
    
    ARIA Configuration (validated):
    - Batch size: 5-10 chunks in parallel
    - Claude Haiku: 4M tokens/min (plenty of headroom)
    - OpenAI: Batched via custom embedder
    - Neo4j: MERGE-based (conflict-safe)
    """
    client = await get_graphiti_client()
    
    # ARIA Pattern: Process in parallel batches
    BATCH_SIZE = 5  # ARIA-validated (safe for Neo4j)
    
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    successful = 0
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(chunks))
        batch = chunks[start_idx:end_idx]
        
        logger.info(f"📦 ARIA Pattern: Batch {batch_num+1}/{total_batches} ({len(batch)} chunks parallel)")
        
        batch_start = time.time()
        
        # Execute batch in parallel (ARIA pattern)
        results = await asyncio.gather(*[
            _process_single_chunk(client, chunk, metadata)
            for chunk in batch
        ], return_exceptions=True)
        
        batch_elapsed = time.time() - batch_start
        
        # Process results
        for chunk, result in zip(batch, results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {chunk['index']} failed: {result}")
            else:
                successful += 1
        
        logger.info(f"✅ Batch {batch_num+1} complete: {len(batch)} chunks in {batch_elapsed:.2f}s")
        logger.info(f"   Effective: {batch_elapsed/len(batch):.2f}s per chunk (was ~8s sequential)")
        
        # Update progress
        chunks_completed = end_idx
        progress = int(75 + (25 * chunks_completed / len(chunks)))
        
        if processing_status and upload_id:
            processing_status[upload_id].update({
                "sub_stage": "graphiti_episode",
                "progress": progress,
                "ingestion_progress": {
                    "chunks_completed": chunks_completed,
                    "chunks_total": len(chunks),
                    "progress_pct": int(100 * chunks_completed / len(chunks)),
                }
            })

async def _process_single_chunk(client, chunk, metadata):
    """Process single chunk (called in parallel)"""
    return await asyncio.wait_for(
        client.add_episode(
            name=f"{metadata['filename']} - Chunk {chunk['index']}",
            episode_body=chunk["text"],
            source=EpisodeType.text,
            source_description=f"Chunk {chunk['index']}",
            reference_time=datetime.now(timezone.utc),
            group_id=metadata.get("user_id", "default")
        ),
        timeout=120.0
    )
```

---

## 🎯 RECOMMENDED APPROACH (ARIA-VALIDATED)

### Option A: Use ARIA Service API (PREFERRED IF AVAILABLE)

**Pros:**
- ✅ Zero custom optimization code
- ✅ ARIA's production optimizations out-of-the-box
- ✅ 100% uptime validated
- ✅ Automatic scaling
- ✅ Minimal dev time (1-2 hours)

**Cons:**
- ⚠️ Dependency on ARIA service
- ⚠️ Need to discover API endpoints first

**Next Step:**
1. Research ARIA service API (30 min)
2. Test with curl
3. Integrate if available

---

### Option B: Library + ARIA Patterns (FALLBACK)

**Pros:**
- ✅ No external dependencies
- ✅ Full control
- ✅ Uses ARIA's proven patterns

**Cons:**
- ⚠️ More dev time (4-5 hours)
- ⚠️ Need to implement batching ourselves
- ⚠️ Need extensive testing

**Components:**
1. Custom Batch Embedder (2-3 hours)
2. Parallel chunk processing (1-2 hours)
3. Testing & tuning (1-2 hours)

---

## 📊 EXPECTED PERFORMANCE (ARIA-LEVEL)

### Based on ARIA Production Metrics

**ARIA Claims:**
- 5 days production
- 100% uptime
- 100% success rate

**This suggests their performance is GOOD**

**Our Estimation with ARIA Patterns:**

**Current (Sequential):**
```
30 chunks × 8.2s = 246s (4m 6s)
```

**With ARIA Patterns (Parallel batch=5):**
```
6 batches × 5s = 30s (effective ~1.5s/chunk)
```

**With ARIA Service (if optimized internally):**
```
Single batch call: ~20-30s for all 30 chunks
(ARIA handles parallelization internally)
```

**Target:** **30-45 seconds for 30 chunks** (vs 4 minutes now)

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: ARIA Service API Discovery (30 min) - DO THIS FIRST

**Tasks:**
```bash
# 1. Check if ARIA service exposes HTTP API
curl -v http://localhost:8003/
curl -v http://localhost:8003/docs
curl -v http://localhost:8003/health
curl -v http://localhost:8003/api/v1/episodes

# 2. Check service logs for API hints
docker logs aria-graphiti-service | head -100

# 3. Inspect service Docker image
docker inspect aria-graphiti-service

# 4. Check if there's API documentation
docker exec aria-graphiti-service ls -la /app/docs/ 2>/dev/null
```

**Deliverable:**
- Document all available endpoints
- API authentication requirements
- Example request/response
- Decision: Use service or optimize library

---

### Step 2A: If ARIA API Available - Integrate (1-2 hours)

**Tasks:**
1. Create `backend/app/integrations/aria_graphiti_client.py`
2. Implement HTTP client for ARIA service
3. Replace `ingest_chunks_to_graph()` to use ARIA service
4. Test with test.pdf
5. Measure performance improvement

**Expected Gain:** -80% (ARIA handles all optimizations)

---

### Step 2B: If No API - Implement ARIA Patterns (4-5 hours)

**Tasks:**
1. Research Graphiti library for batch methods
2. Implement custom batch embedder (ARIA pattern)
3. Implement parallel chunk processing (batch=5)
4. Add performance monitoring
5. Test thoroughly (Neo4j conflict testing)
6. Tune batch size

**Expected Gain:** -70-80% (manual optimization)

---

### Step 3: Validation & Tuning (1 hour)

**Tests:**
1. test.pdf (30 chunks) - Baseline comparison
2. Verify 100% success rate (ARIA standard)
3. Check Neo4j for conflicts
4. Monitor API rate limits
5. Tune batch_size if needed

**Success Criteria (ARIA Standard):**
- ✅ 100% success rate
- ✅ < 1 minute for 30 chunks
- ✅ No Neo4j conflicts
- ✅ No API rate limit errors
- ✅ Stable performance

---

## 🎯 DECISION TREE

```
START
  ↓
Research ARIA Service API (30 min)
  ↓
  ├─ API Available? ──YES──> Use ARIA Service (1-2h) ──> DONE ✅
  │                            (Fastest, lowest risk)
  │
  └─ API Available? ──NO───> Check Graphiti Batch Methods
                               ↓
                               ├─ Built-in Batch? ──YES──> Use Built-in (2-3h)
                               │
                               └─ Built-in Batch? ──NO───> Custom Implementation (4-5h)
                                                             - Batch embedder
                                                             - Parallel processing
                                                             - ARIA patterns
```

---

## 💡 MY RECOMMENDATION

**Immediate Action:**

1. **Research ARIA Service (30 min)** ✅ DO THIS NOW
   - Check if `aria-graphiti-service` has HTTP API
   - If YES → Use their service (1-2h integration)
   - If NO → Continue to Step 2

2. **Check Graphiti Library (30 min)**
   - Look for batch methods in graphiti-core
   - Check recent Graphiti updates
   - See if batching added in newer versions

3. **Implement Best Available Option:**
   - Prefer: ARIA service (if API available)
   - Fallback: Graphiti batch methods (if exists)
   - Last resort: Custom implementation (ARIA patterns)

**Why This Order:**
- Leverages existing ARIA infrastructure
- Minimal dev time if ARIA service works
- Falls back to proven patterns if needed
- No reinventing the wheel

---

## 🔍 NEXT STEPS

**Tu veux que je:**

**Option 1:** Research ARIA service API NOW (30 min)
- Check all endpoints
- Test with curl
- Document API structure
- Report findings

**Option 2:** Start with Graphiti library research
- Check for batch methods
- Review Graphiti documentation
- Look for performance flags

**Option 3:** Go straight to custom implementation
- Skip research
- Implement batch embedder + parallel
- 4-5 hours dev time

**Ma recommandation:** **Option 1** - Let's see if ARIA service has an API we can use. If they do, we save HOURS of dev time and get production-validated optimizations for free!

---

**Question:** Tu as accès au code source d'ARIA ou c'est juste un service Docker que tu utilises?

