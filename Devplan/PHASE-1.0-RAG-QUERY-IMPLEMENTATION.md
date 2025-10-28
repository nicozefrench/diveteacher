# Phase 1.0 - RAG Query Implementation (Downstream)

> **Status:** 🟡 IN PLANNING  
> **Phase:** Downstream (Query pipeline)  
> **Prerequisites:** Phase 0.9 COMPLETE ✅  
> **Date:** October 28, 2025  
> **Duration:** 2-3 days

---

## 📋 Table of Contents

- [Executive Summary](#executive-summary)
- [Current State Analysis](#current-state-analysis)
- [Gaps & Issues Identified](#gaps--issues-identified)
- [Implementation Plan](#implementation-plan)
- [Testing Strategy](#testing-strategy)
- [Success Criteria](#success-criteria)
- [Reference Architecture](#reference-architecture)

---

## Executive Summary

### Objective

Implement a **production-ready RAG query pipeline** that:
1. ✅ Uses **Mistral 7B on Ollama** for LLM inference (local, French-optimized)
2. ✅ Leverages **Graphiti search** for hybrid knowledge retrieval
3. ✅ Streams responses in real-time to frontend
4. ✅ Follows **best practices** from Ollama deployment guides
5. ✅ Handles errors gracefully and logs comprehensively

### Current Status

**Upstream (Ingestion):** ✅ **COMPLETE** (Phase 0.9)
- Documents → Docling → Chunking → Graphiti → Neo4j
- 100% functional, 205 entities, 2,229 relationships

**Downstream (Query):** 🟡 **NEEDS WORK** (Phase 1.0)
- Code exists (`llm.py`, `rag.py`) but **NOT TESTED**
- Ollama container **UNHEALTHY** (no models installed)
- Configuration **gaps** vs best practices
- API endpoint **NOT IMPLEMENTED**

---

## Current State Analysis

### 1. Docker Configuration (`docker-compose.dev.yml`)

**Current Setup:**
```yaml
ollama:
  image: ollama/ollama:latest
  container_name: rag-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama-models:/root/.ollama
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Status:**
- Container: ✅ Running
- Health: ❌ **UNHEALTHY** (healthcheck fails)
- Reason: No models installed (`ollama list` returns empty)
- API: ✅ Accessible (port 11434, version 0.12.6)

**Issues:**
1. ❌ **No environment variables** configured (OLLAMA_HOST, OLLAMA_KEEP_ALIVE, etc.)
2. ❌ **No model pre-installed** (Mistral 7B needs to be pulled)
3. ❌ **No resource limits** (memory, CPU)
4. ❌ **No startup command** to pull model automatically
5. ✅ Volume persistent (models saved across restarts)

### 2. Backend Configuration (`.env`)

**Expected Variables (from guides):**
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=mistral:7b-instruct-q5_K_M  # Quantized for efficiency
LLM_PROVIDER=ollama

# RAG Configuration
RAG_TOP_K=5
RAG_TEMPERATURE=0.7
RAG_MAX_TOKENS=2000
```

**Current State:**
- `.env` file exists but **filtered by .cursorignore** (cannot read directly)
- `docker-compose.dev.yml` shows:
  - `OLLAMA_BASE_URL=http://ollama:11434` ✅
  - `OLLAMA_MODEL=${OLLAMA_MODEL:-llama3:8b}` ⚠️ **Default is llama3, NOT Mistral**
  - `LLM_PROVIDER=${LLM_PROVIDER:-ollama}` ✅

**Issues:**
1. ⚠️ **Wrong default model** (llama3 instead of mistral)
2. ❌ **No RAG-specific variables** (TOP_K, temperature, max_tokens)
3. ❌ **No Mistral-specific optimization** (quantization level)

### 3. Backend Code Analysis

#### `backend/app/core/llm.py` ✅ GOOD

**Architecture:**
- Abstract `LLMProvider` base class ✅
- `OllamaProvider` with streaming support ✅
- Also supports Claude and OpenAI ✅
- Global singleton pattern ✅

**Ollama Implementation:**
```python
class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    async def stream_completion(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2000):
        # Streams from /api/generate endpoint
        # Uses httpx with 60s timeout
```

**Status:** ✅ **PRODUCTION-READY** (no changes needed)

#### `backend/app/core/rag.py` ✅ GOOD

**Architecture:**
- `retrieve_context()` - Uses Graphiti search ✅
- `build_rag_prompt()` - DiveTeacher-specific system prompt ✅
- `rag_stream_response()` - Retrieval → Prompt → Stream ✅
- `rag_query()` - Non-streaming version ✅

**System Prompt:**
```python
system_prompt = """You are DiveTeacher, an AI assistant specialized in scuba diving education.

CRITICAL RULES:
1. Answer ONLY using information from the provided knowledge facts
2. If context is insufficient, say "I don't have enough information..."
3. NEVER make up or infer information
4. Cite facts: [Fact 1], [Fact 2]
5. Be concise but thorough
..."""
```

**Status:** ✅ **EXCELLENT** (DiveTeacher-specific, grounded)

#### `backend/app/integrations/graphiti.py` ✅ GOOD

**Search Function:**
```python
async def search_knowledge_graph(query: str, num_results: int = 5, group_ids: List[str] = None):
    """
    Search Graphiti knowledge graph using hybrid search
    Returns: List of EntityEdges (relations with facts)
    """
```

**Status:** ✅ **READY** (needs testing but code is solid)

### 4. API Endpoints

**Current Endpoints:**
- `POST /api/upload` ✅ WORKING (ingestion)
- `GET /api/upload/status/{upload_id}` ✅ WORKING (status)
- `GET /api/health` ✅ WORKING (health check)

**Missing Endpoints:**
- ❌ `POST /api/query` - RAG query endpoint (CRITICAL)
- ❌ `POST /api/query/stream` - Streaming query (CRITICAL)
- ❌ `GET /api/models` - List available models (nice-to-have)

**Impact:** Cannot test RAG pipeline without query endpoint

---

## Gaps & Issues Identified

### Critical Issues (P0 - Blocking)

1. **❌ No Mistral 7B Model Installed**
   - **Problem:** Ollama container has zero models
   - **Impact:** Cannot run any LLM inference
   - **Fix:** Pull `mistral:7b-instruct-q5_K_M` model
   - **Effort:** 5 minutes (automated in plan)

2. **❌ No Query API Endpoint**
   - **Problem:** Backend has RAG code but no HTTP endpoint
   - **Impact:** Cannot test end-to-end RAG
   - **Fix:** Create `/api/query` endpoint
   - **Effort:** 30 minutes

3. **❌ Ollama Container Unhealthy**
   - **Problem:** Healthcheck fails (no models = failure)
   - **Impact:** Docker shows service as degraded
   - **Fix:** Change healthcheck to check API version instead
   - **Effort:** 5 minutes

### High Priority Issues (P1 - Important)

4. **⚠️ Missing Ollama Environment Variables**
   - **Problem:** No OLLAMA_KEEP_ALIVE, OLLAMA_NUM_PARALLEL, etc.
   - **Impact:** Suboptimal performance, memory issues
   - **Fix:** Add recommended env vars from guides
   - **Effort:** 10 minutes

5. **⚠️ Wrong Default Model (llama3 vs mistral)**
   - **Problem:** `.env` defaults to llama3:8b
   - **Impact:** Wrong model used if env var not set
   - **Fix:** Change default to `mistral:7b-instruct-q5_K_M`
   - **Effort:** 2 minutes

6. **⚠️ No Resource Limits**
   - **Problem:** Ollama container can use unlimited memory
   - **Impact:** Potential OOM on Mac M1 Max
   - **Fix:** Add Docker memory limits (16GB max)
   - **Effort:** 5 minutes

### Medium Priority Issues (P2 - Nice to Have)

7. **⚠️ No Model Pre-loading**
   - **Problem:** Model must be pulled manually
   - **Impact:** Extra setup step for new deployments
   - **Fix:** Add startup script to auto-pull
   - **Effort:** 15 minutes

8. **⚠️ No Monitoring/Logging**
   - **Problem:** No visibility into Ollama performance
   - **Impact:** Hard to debug slow queries
   - **Fix:** Add logging middleware
   - **Effort:** 20 minutes

9. **⚠️ No Rate Limiting**
   - **Problem:** Unlimited concurrent requests
   - **Impact:** Potential overload on single Mac
   - **Fix:** Add FastAPI rate limiter
   - **Effort:** 15 minutes

### Comparison with Best Practices (from guides)

| Best Practice | Current Status | Gap |
|---------------|----------------|-----|
| **Model Installed** | ❌ None | ❌ CRITICAL |
| **Quantized Model** | ❌ N/A | ⚠️ Use Q5_K_M |
| **OLLAMA_HOST set** | ❌ Not configured | ⚠️ Add 0.0.0.0 |
| **OLLAMA_KEEP_ALIVE** | ❌ Not set | ⚠️ Add 5m |
| **OLLAMA_NUM_PARALLEL** | ❌ Not set | ⚠️ Add 4 |
| **Memory Limits** | ❌ None | ⚠️ Add 16GB |
| **Healthcheck** | ⚠️ Fails (no models) | ⚠️ Fix check |
| **API Endpoint** | ❌ Missing | ❌ CRITICAL |
| **Error Handling** | ✅ Good in code | ✅ OK |
| **Streaming** | ✅ Implemented | ✅ OK |

---

## Implementation Plan

### Phase 1.0 - 3 Days (8 Steps)

#### **Step 1: Fix Ollama Docker Configuration** (30 min)

**Files to Modify:**
- `docker/docker-compose.dev.yml`

**Changes:**

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: rag-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama-models:/root/.ollama
  environment:
    # Best practices from guides
    - OLLAMA_HOST=0.0.0.0:11434
    - OLLAMA_ORIGINS=*
    - OLLAMA_KEEP_ALIVE=5m
    - OLLAMA_MAX_LOADED_MODELS=1
    - OLLAMA_NUM_PARALLEL=4
    - OLLAMA_MAX_QUEUE=128
  deploy:
    resources:
      limits:
        memory: 16G  # Mac M1 Max has 32GB, leave 16GB for system
  healthcheck:
    # FIX: Check API version instead of tags (works without models)
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
    interval: 10s
    timeout: 5s
    retries: 5
  # Optional: Auto-pull model on startup
  # entrypoint: ["/bin/sh", "-c", "ollama serve & sleep 5 && ollama pull mistral:7b-instruct-q5_K_M && wait"]
```

**Validation:**
```bash
docker-compose -f docker/docker-compose.dev.yml up -d ollama
docker ps  # Should show "healthy"
curl http://localhost:11434/api/version  # Should return version
```

#### **Step 2: Update .env with Mistral Configuration** (10 min)

**File:** `.env`

**Changes:**
```bash
# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=mistral:7b-instruct-q5_K_M  # Quantized for Mac M1 Max
LLM_PROVIDER=ollama

# RAG Configuration
RAG_TOP_K=5              # Number of facts to retrieve
RAG_TEMPERATURE=0.7      # Balanced creativity/factuality
RAG_MAX_TOKENS=2000      # Max response length
RAG_STREAM=true          # Enable streaming responses

# Mistral-Specific Tuning (for diving education)
MISTRAL_TEMPERATURE=0.3  # Lower = more factual (safety-critical)
MISTRAL_TOP_P=0.9
MISTRAL_TOP_K=40
MISTRAL_NUM_CTX=4096     # Context window
```

**Note:** If `.env` is gitignored, update `env.template` instead.

#### **Step 3: Pull Mistral 7B Model** (5 min + ~4GB download)

**Command:**
```bash
# Pull quantized Mistral 7B (optimized for 16GB RAM)
docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M

# Verify
docker exec rag-ollama ollama list
# Expected output:
# NAME                            SIZE
# mistral:7b-instruct-q5_K_M     4.7 GB
```

**Why Q5_K_M?**
- **Q5_K_M (5-bit quantization)** = Best balance quality/size
- **Memory:** ~5GB RAM (vs 14GB for full precision)
- **Quality:** 95%+ of full model performance
- **Speed:** 2-3x faster inference

**Alternative Models (if needed):**
```bash
# Smaller (faster, lower quality)
ollama pull mistral:7b-instruct-q4_K_S  # 4.1GB, 90% quality

# Larger (slower, higher quality)
ollama pull mistral:7b-instruct-q8_0    # 7.7GB, 98% quality
```

#### **Step 4: Create Query API Endpoint** (45 min)

**File:** `backend/app/api/query.py` (NEW)

```python
"""
Query API - RAG endpoints for DiveTeacher
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from app.core.rag import rag_stream_response, rag_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")
    max_tokens: Optional[int] = Field(2000, ge=100, le=4000, description="Max response tokens")
    stream: Optional[bool] = Field(True, description="Stream response")
    group_ids: Optional[List[str]] = Field(None, description="Filter by group IDs (multi-tenant)")


class QueryResponse(BaseModel):
    """Response model for non-streaming query"""
    question: str
    answer: str
    num_sources: int
    context: dict


@router.post("/", response_model=QueryResponse)
async def query_knowledge_graph(request: QueryRequest):
    """
    Query the knowledge graph (non-streaming)
    
    Returns complete answer with context.
    """
    try:
        logger.info(f"RAG query: {request.question[:50]}...")
        
        result = await rag_query(
            question=request.question,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            group_ids=request.group_ids
        )
        
        logger.info(f"RAG query complete: {result['num_sources']} sources used")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"RAG query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/stream")
async def query_knowledge_graph_stream(request: QueryRequest):
    """
    Query the knowledge graph (streaming)
    
    Returns Server-Sent Events (SSE) stream.
    """
    try:
        logger.info(f"RAG stream query: {request.question[:50]}...")
        
        async def event_generator():
            """Generate SSE events"""
            try:
                async for token in rag_stream_response(
                    question=request.question,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    group_ids=request.group_ids
                ):
                    # SSE format: data: {token}\n\n
                    yield f"data: {token}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}", exc_info=True)
                yield f"data: [ERROR: {str(e)}]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error(f"RAG stream setup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stream setup failed: {str(e)}")


@router.get("/health")
async def query_health():
    """
    Health check for query endpoint
    
    Verifies Ollama connection and model availability.
    """
    from app.core.llm import get_llm
    
    try:
        llm = get_llm()
        
        # Test simple completion
        response = ""
        async for token in llm.stream_completion(
            prompt="Test: What is 2+2?",
            temperature=0.1,
            max_tokens=50
        ):
            response += token
            if len(response) > 10:  # Early exit
                break
        
        return {
            "status": "healthy",
            "provider": "ollama",
            "model": getattr(llm, 'model', 'unknown'),
            "test_response": response[:50]
        }
        
    except Exception as e:
        logger.error(f"Query health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Query service unavailable: {str(e)}")
```

**Update `main.py`:**
```python
# backend/app/main.py
from app.api import upload, query  # Add query

app.include_router(upload.router)
app.include_router(query.router)  # ADD THIS
```

**Validation:**
```bash
# Restart backend
docker-compose -f docker/docker-compose.dev.yml restart backend

# Test non-streaming
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels sont les prérequis pour le Niveau 4?", "stream": false}'

# Test streaming
curl -N http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique les paliers de décompression"}'

# Test health
curl http://localhost:8000/api/query/health
```

#### **Step 5: Add Configuration to settings.py** (10 min)

**File:** `backend/app/core/config.py`

**Add:**
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # === RAG Configuration ===
    RAG_TOP_K: int = Field(5, description="Number of facts to retrieve")
    RAG_TEMPERATURE: float = Field(0.7, description="LLM temperature for RAG")
    RAG_MAX_TOKENS: int = Field(2000, description="Max tokens for RAG response")
    RAG_STREAM: bool = Field(True, description="Enable streaming by default")
    
    # === Mistral-Specific ===
    MISTRAL_TEMPERATURE: float = Field(0.3, description="Mistral temperature (factual)")
    MISTRAL_TOP_P: float = Field(0.9, description="Mistral nucleus sampling")
    MISTRAL_TOP_K: int = Field(40, description="Mistral top-k sampling")
    MISTRAL_NUM_CTX: int = Field(4096, description="Mistral context window")
```

#### **Step 6: Create Test Script** (20 min)

**File:** `scripts/test_rag_query.py` (NEW)

```python
"""
Test RAG Query Pipeline End-to-End
"""
import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

async def test_query_non_streaming():
    """Test non-streaming query"""
    print("\n=== Test 1: Non-Streaming Query ===")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        start = time.time()
        
        response = await client.post(
            f"{BASE_URL}/api/query",
            json={
                "question": "Quels sont les prérequis pour le Niveau 4 GP?",
                "temperature": 0.3,
                "stream": False
            }
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success ({elapsed:.2f}s)")
            print(f"Sources used: {result['num_sources']}")
            print(f"Answer: {result['answer'][:200]}...")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)


async def test_query_streaming():
    """Test streaming query"""
    print("\n=== Test 2: Streaming Query ===")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        start = time.time()
        tokens_received = 0
        
        async with client.stream(
            "POST",
            f"{BASE_URL}/api/query/stream",
            json={
                "question": "Explique les paliers de décompression",
                "temperature": 0.5
            }
        ) as response:
            print("Streaming response:")
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    token = line[6:]  # Remove "data: "
                    if token == "[DONE]":
                        break
                    elif token.startswith("[ERROR"):
                        print(f"\n❌ Error: {token}")
                        return
                    else:
                        print(token, end="", flush=True)
                        tokens_received += 1
        
        elapsed = time.time() - start
        print(f"\n✅ Streaming complete ({elapsed:.2f}s, {tokens_received} tokens)")


async def test_health():
    """Test query health endpoint"""
    print("\n=== Test 3: Query Health Check ===")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/api/query/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query service healthy")
            print(f"Provider: {result['provider']}")
            print(f"Model: {result['model']}")
            print(f"Test response: {result['test_response']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("RAG Query Pipeline E2E Tests")
    print("=" * 60)
    
    # Test 1: Non-streaming
    try:
        await test_query_non_streaming()
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: Streaming
    try:
        await test_query_streaming()
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: Health
    try:
        await test_health()
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    print("\n" + "=" * 60)
    print("Tests complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

**Run:**
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
python scripts/test_rag_query.py
```

#### **Step 7: Monitor Ollama Performance** (15 min)

**File:** `scripts/monitor_ollama.sh` (NEW)

```bash
#!/bin/bash
# Monitor Ollama container performance

echo "=== Ollama Performance Monitor ==="
echo

# Container stats
echo "Container Stats:"
docker stats rag-ollama --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Model info
echo "Installed Models:"
docker exec rag-ollama ollama list
echo

# API status
echo "API Status:"
curl -s http://localhost:11434/api/version | jq .
echo

# Recent logs (last 20 lines)
echo "Recent Logs:"
docker logs rag-ollama --tail 20
echo

echo "=== Monitor Complete ==="
```

**Run:**
```bash
chmod +x scripts/monitor_ollama.sh
./scripts/monitor_ollama.sh
```

#### **Step 8: Update Documentation** (30 min)

**Files to Update:**
1. `docs/SETUP.md` - Add Phase 1.0 section
2. `docs/ARCHITECTURE.md` - Update RAG query flow
3. `CURRENT-CONTEXT.md` - Mark Phase 1.0 as in progress

**Create:** `docs/MISTRAL.md` (NEW)

```markdown
# Mistral 7B Configuration for DiveTeacher

## Model Selection

**Model:** `mistral:7b-instruct-q5_K_M`

**Why this model?**
- **French Support:** Native French training (FFESSM docs)
- **Instruction-Tuned:** Optimized for Q&A tasks
- **Quantized (Q5_K_M):** 5-bit, ~5GB RAM, 95% quality
- **Context Window:** 8,192 tokens (32k with extended)
- **Speed:** 2-3x faster than full precision

## Performance Tuning

**For Diving Education (Safety-Critical):**
```python
# Lower temperature = more factual
temperature: 0.3

# Nucleus sampling
top_p: 0.9
top_k: 40

# Large context for long procedures
num_ctx: 4096
```

## Memory Usage

| Model Variant | RAM | Quality | Speed |
|---------------|-----|---------|-------|
| Q4_K_S | 4.1GB | 90% | Fast |
| **Q5_K_M (Recommended)** | 5.0GB | 95% | Balanced |
| Q8_0 | 7.7GB | 98% | Slower |
| Full Precision | 14GB | 100% | Slowest |

## Troubleshooting

**Issue:** Slow responses (> 10s)
**Solution:** Use Q4_K_S or reduce num_ctx to 2048

**Issue:** Out of memory
**Solution:** Reduce OLLAMA_KEEP_ALIVE to 1m
```

---

## Testing Strategy

### Unit Tests

**Test Files:**
- `backend/tests/test_llm.py` - Test LLM provider abstraction
- `backend/tests/test_rag.py` - Test RAG chain logic
- `backend/tests/test_query_api.py` - Test API endpoints

**Coverage Targets:**
- LLM streaming: 90%
- RAG chain: 85%
- API endpoints: 80%

### Integration Tests

**Scenarios:**
1. Query with existing knowledge (should return grounded answer)
2. Query with no knowledge (should say "insufficient information")
3. Streaming query (should return tokens progressively)
4. Concurrent queries (should handle 4 parallel requests)
5. Long query (> 1000 chars)
6. Empty query (should return 400 error)

### Performance Tests

**Metrics:**
- **First Token Time:** < 2s (time to first response token)
- **Total Response Time:** < 15s (for 500-word answer)
- **Tokens/Second:** > 30 (throughput)
- **Memory Usage:** < 8GB (Ollama + backend)
- **Concurrent Requests:** 4 max (Mac M1 Max limit)

**Benchmark Script:**
```python
# scripts/benchmark_rag.py
import asyncio
import time

async def benchmark():
    questions = [
        "Quels sont les prérequis pour le Niveau 4?",
        "Explique les paliers de décompression",
        "Quelle est la profondeur maximale pour le Niveau 2?"
    ]
    
    for q in questions:
        start = time.time()
        # ... send query ...
        first_token_time = ...  # Time to first token
        total_time = time.time() - start
        
        print(f"Question: {q[:50]}...")
        print(f"  First token: {first_token_time:.2f}s")
        print(f"  Total: {total_time:.2f}s")
```

### End-to-End Tests

**Full Pipeline:**
1. Upload Nitrox.pdf (already done ✅)
2. Wait for ingestion (already done ✅)
3. **Query:** "Quels sont les mélanges Nitrox autorisés?"
4. **Verify:**
   - Answer cites exact facts from PDF
   - Uses [Fact 1], [Fact 2] citations
   - Response is in French
   - Streaming works without errors
   - Response time < 15s

**Test with Multiple Documents:**
1. Upload 3 diving manuals (FFESSM N4, SSI Open Water, PADI)
2. Query: "Compare FFESSM and SSI certification requirements"
3. Verify:
   - Answer references multiple documents
   - Cross-document relationships used
   - No hallucinations

---

## Success Criteria

### Phase 1.0 Complete When:

1. ✅ **Mistral 7B Installed**
   - `ollama list` shows `mistral:7b-instruct-q5_K_M`
   - Model loads successfully (< 10s)

2. ✅ **Ollama Container Healthy**
   - Docker health check passes
   - API responds to `/api/version`
   - Memory usage < 8GB

3. ✅ **Query API Functional**
   - `POST /api/query` returns 200
   - `POST /api/query/stream` streams tokens
   - `/api/query/health` shows "healthy"

4. ✅ **RAG Pipeline Working**
   - Query retrieves relevant facts from Neo4j
   - LLM generates grounded answers
   - Citations include [Fact X] references
   - No hallucinations detected

5. ✅ **Performance Acceptable**
   - First token < 2s
   - Total response < 15s
   - Tokens/sec > 30
   - Memory < 8GB

6. ✅ **Tests Passing**
   - Unit tests: 80%+ coverage
   - Integration tests: All pass
   - E2E test: Query Nitrox.pdf successfully

7. ✅ **Documentation Complete**
   - SETUP.md updated with Phase 1.0
   - MISTRAL.md created
   - API docs updated
   - CURRENT-CONTEXT.md reflects Phase 1.0

---

## Reference Architecture

### RAG Query Flow (Downstream)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUESTION                              │
│              "Quels sont les prérequis N4?"                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 QUERY API ENDPOINT                            │
│            POST /api/query or /stream                         │
│                                                               │
│  - Validates input (length, format)                          │
│  - Extracts parameters (temperature, max_tokens)             │
│  - Calls RAG chain                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  RETRIEVE CONTEXT                             │
│             (Graphiti Hybrid Search)                          │
│                                                               │
│  1. Query Graphiti: search_knowledge_graph()                 │
│  2. Returns: List[EntityEdge] (facts with relations)         │
│  3. Example: "Niveau 4 requires Niveau 3 + 40 dives"        │
│                                                               │
│  ➤ Uses: Semantic search + BM25 + RRF                       │
│  ➤ Returns: Top 5 facts (configurable)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  BUILD RAG PROMPT                             │
│                                                               │
│  System Prompt:                                              │
│  - "You are DiveTeacher..."                                  │
│  - "Answer ONLY from provided facts"                         │
│  - "Cite facts: [Fact 1], [Fact 2]"                        │
│                                                               │
│  User Prompt:                                                │
│  - "Knowledge from diving manuals:"                          │
│  - "[Fact 1] Niveau 4 requires..."                          │
│  - "[Fact 2] Prerequisites include..."                       │
│  - "Question: {user_question}"                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    OLLAMA + MISTRAL                           │
│                                                               │
│  Container: rag-ollama                                       │
│  Model: mistral:7b-instruct-q5_K_M                          │
│  Endpoint: http://ollama:11434/api/generate                 │
│                                                               │
│  Parameters:                                                 │
│  - temperature: 0.3 (factual)                               │
│  - num_predict: 2000 (max tokens)                           │
│  - stream: true (real-time)                                 │
│                                                               │
│  ➤ Generates: Token stream                                  │
│  ➤ Speed: ~30-50 tokens/sec                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  STREAM RESPONSE                              │
│                                                               │
│  - For each token from Mistral:                             │
│    ➤ Format as SSE: "data: {token}\n\n"                    │
│    ➤ Send to client (real-time)                            │
│  - On completion:                                            │
│    ➤ Send "data: [DONE]\n\n"                               │
│  - On error:                                                 │
│    ➤ Send "data: [ERROR: ...]\n\n"                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND DISPLAY                             │
│                                                               │
│  - Receives SSE stream                                       │
│  - Displays tokens progressively                             │
│  - Shows citations: [Fact 1], [Fact 2]                     │
│  - Highlights sources                                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**1. Graphiti Search:**
- Input: User question (text)
- Processing: Hybrid search (semantic + BM25 + RRF)
- Output: List of EntityEdges (facts with relations)
- Performance: < 500ms for search

**2. Prompt Builder:**
- Input: Question + Facts
- Processing: Format as RAG prompt with system instructions
- Output: (system_prompt, user_prompt)
- Special: DiveTeacher-specific rules for safety

**3. Ollama + Mistral:**
- Input: Prompt (system + user)
- Processing: LLM inference on Mistral 7B Q5_K_M
- Output: Token stream
- Performance: ~30-50 tokens/sec

**4. Streaming Response:**
- Input: Token stream from Mistral
- Processing: Format as Server-Sent Events (SSE)
- Output: HTTP stream to client
- Protocol: `data: {token}\n\n`

---

## Timeline & Effort

### Day 1: Setup & Configuration (4-5 hours)

- [ ] **Morning (2h):**
  - Step 1: Fix Ollama Docker config (30 min)
  - Step 2: Update .env variables (10 min)
  - Step 3: Pull Mistral model (5 min + 15 min download)
  - Step 5: Add config to settings.py (10 min)
  - **Validation:** Ollama healthy, model loaded

- [ ] **Afternoon (2-3h):**
  - Step 4: Create query API endpoint (45 min)
  - Update main.py to include router (5 min)
  - Restart backend, test endpoints (15 min)
  - **Validation:** API returns 200

### Day 2: Testing & Debugging (4-5 hours)

- [ ] **Morning (2h):**
  - Step 6: Create test script (20 min)
  - Run tests, fix issues (1h)
  - **Validation:** All 3 tests pass

- [ ] **Afternoon (2-3h):**
  - End-to-end test with Nitrox.pdf (30 min)
  - Performance benchmarking (30 min)
  - Fix any issues discovered (1-2h)
  - **Validation:** E2E test passes, performance acceptable

### Day 3: Monitoring & Documentation (3-4 hours)

- [ ] **Morning (1-2h):**
  - Step 7: Create monitoring script (15 min)
  - Monitor performance under load (30 min)
  - Optimize if needed (30 min)
  - **Validation:** Performance stable

- [ ] **Afternoon (2h):**
  - Step 8: Update documentation (30 min)
  - Create MISTRAL.md guide (20 min)
  - Update CURRENT-CONTEXT.md (10 min)
  - Final review and commit (30 min)
  - **Validation:** All docs updated

**Total Effort:** 11-14 hours over 3 days

---

## Risks & Mitigation

### Risk 1: Mistral Model Too Slow

**Probability:** Medium  
**Impact:** High (unusable if > 30s per query)

**Mitigation:**
1. Use Q4_K_S (faster quantization)
2. Reduce num_ctx to 2048
3. Lower max_tokens to 1000
4. Add timeout to prevent hanging

### Risk 2: Out of Memory

**Probability:** Low (Mac M1 Max has 32GB)  
**Impact:** High (service crash)

**Mitigation:**
1. Set Docker memory limit (16GB)
2. Set OLLAMA_KEEP_ALIVE=2m (unload quickly)
3. OLLAMA_MAX_LOADED_MODELS=1
4. Monitor with `docker stats`

### Risk 3: Hallucinations

**Probability:** Medium  
**Impact:** Critical (safety risk for diving)

**Mitigation:**
1. Use low temperature (0.3)
2. Strong system prompt ("ONLY from context")
3. Fact citation requirement ([Fact 1])
4. Manual review of answers

### Risk 4: Query Endpoint Crashes

**Probability:** Low  
**Impact:** High (no RAG)

**Mitigation:**
1. Comprehensive error handling
2. Try/except on all async calls
3. Timeout on LLM calls (60s)
4. Health check endpoint

---

## Next Steps (Phase 1.1+)

**After Phase 1.0 Complete:**

1. **Multi-User Auth** (Phase 1.1)
   - Supabase integration
   - User-specific queries
   - Group ID filtering

2. **Conversation History** (Phase 1.2)
   - Save queries to PostgreSQL
   - Multi-turn conversations
   - Context persistence

3. **Frontend Integration** (Phase 1.3)
   - Chat component
   - Streaming display
   - Citation highlights

4. **Advanced RAG** (Phase 1.4)
   - Re-ranking
   - Query expansion
   - Hybrid retrieval tuning

---

**Document Version:** 1.0  
**Created:** October 28, 2025  
**Status:** 🟡 IN PLANNING  
**Next:** Execute Step 1 (Fix Ollama Docker)

