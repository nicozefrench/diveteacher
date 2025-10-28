# Setup Guide - DiveTeacher RAG Knowledge Graph

> **🤖 AI Agent Notice:** This documentation is optimized for Claude Sonnet 4.5 agents.  
> **Purpose:** Complete, unambiguous setup instructions for local development and production deployment.  
> **Context:** DiveTeacher is a SaaS platform for scuba diving training using RAG + Knowledge Graph.

---

## 📋 Document Structure for AI Agents

This guide provides:
1. **Prerequisites** - Required software and accounts
2. **Local Development Setup** - Mac M1 Max optimized (Phases 0-8, 0€ cost)
3. **Production Deployment** - DigitalOcean GPU + Vercel (Phase 9, ~$120/month)
4. **Troubleshooting** - Common issues with exact solutions
5. **Testing Procedures** - Verification steps with expected outputs

---

## 🎯 Project Context (Critical for AI Understanding)

### Application Identity
- **Name:** DiveTeacher
- **Type:** Multi-user SaaS platform
- **Domain:** Scuba diving training (FFESSM, SSI certifications)
- **Repository:** https://github.com/nicozefrench/diveteacher (PRIVATE)
- **Domains:** diveteacher.io (primary), diveteacher.app (redirect)

### Technology Stack
- **Backend:** FastAPI (Python) + Neo4j (Graph DB) + Ollama (LLM server)
- **Frontend:** React 18 + Vite + TailwindCSS + shadcn/ui
- **LLM:** Mistral 7B-instruct-Q5_K_M (5.2GB quantized)
- **Auth:** Supabase Cloud (free tier, < 50k users)
- **Monitoring:** Sentry (free tier, < 5k events)
- **Deployment:** Vercel (frontend) + DigitalOcean GPU Droplet (backend)

### Development Strategy (CRITICAL)
- **Phases 0-8:** 100% local development on Mac M1 Max → **Cost: 0€**
- **Phase 9 ONLY:** Production deployment → **Cost: ~$120/month**
- **Rule:** No cloud services activated until local development is complete

---

## ✅ Prerequisites

### Local Development (Mac M1 Max)
- ✅ **Docker Desktop** (installed, running)
- ✅ **Docker Compose** (included with Docker Desktop)
- ✅ **Git** (installed)
- ✅ **Python 3.11+** (installed)
- ✅ **Node.js 18+** (installed)
- ✅ **Hardware:** Mac M1 Max, 32GB RAM (confirmed available)

### Cloud Services (Not Needed Until Phase 9)
- ⏸️ **Vercel Account** (paid tier, has API key) - Don't deploy yet
- ⏸️ **DigitalOcean Account** - Don't create droplet yet
- ⏸️ **Supabase Account** - Configure in Phase 1 (cloud, free)
- ⏸️ **Sentry Account** - Configure in Phase 0 (optional, free)

---

## 🚀 Local Development Setup (Phases 0-8)

### Phase 0.1: Configure Environment

#### Step 1: Navigate to Project
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
```

#### Step 2: Verify .env Exists
```bash
# File should exist (already created in Session 2)
cat .env | grep "LLM_PROVIDER"
# Expected output: LLM_PROVIDER=ollama
```

#### Step 3: Review Critical Settings
```bash
# Essential local dev settings (already configured):
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral:7b-instruct-q5_K_M
OLLAMA_BASE_URL=http://ollama:11434

NEO4J_URI=bolt://neo4j:7687  # Internal Docker network
NEO4J_PASSWORD=diveteacher_dev_2025

FRONTEND_URL=http://localhost:5173
API_HOST=0.0.0.0
API_PORT=8000

SENTRY_DSN_BACKEND=  # Empty for now
SENTRY_DSN_FRONTEND=  # Empty for now
```

**⚠️ IMPORTANT - Neo4j Ports:**
- **External (host machine):** 7475 (HTTP), 7688 (Bolt)
- **Internal (Docker network):** 7474, 7687
- **Reason:** Port 7474/7687 already used by `aria-neo4j` (another app)
- **Backend connects internally:** Uses `bolt://neo4j:7687` (inside Docker)

---

### Phase 0.2: Configure Sentry (Optional)

**AI Agent Decision Tree:**
- **IF** user wants monitoring from day 1 → Configure Sentry now
- **IF** user wants to test first → Skip, configure later
- **Recommendation:** Skip for now, test app first

#### Skip for Now (Recommended)
```bash
# Leave these empty in .env:
SENTRY_DSN_BACKEND=
SENTRY_DSN_FRONTEND=
SENTRY_ENVIRONMENT=development
```

#### Configure Now (If Requested)
1. Go to https://sentry.io (create account if needed)
2. Create TWO projects:
   - Project 1: "diveteacher-backend" (Platform: Python/FastAPI)
   - Project 2: "diveteacher-frontend" (Platform: React)
3. Copy DSNs to `.env`:
```bash
SENTRY_DSN_BACKEND=https://xxxxx@o000000.ingest.us.sentry.io/0000000
SENTRY_DSN_FRONTEND=https://yyyyy@o000000.ingest.us.sentry.io/1111111
SENTRY_ENVIRONMENT=development
```

---

### Phase 0.3: Start Docker Services

#### Step 1: Check for Port Conflicts
```bash
# Verify aria-neo4j is running (should be on 7474/7687)
docker ps --filter "name=aria-neo4j"
# Expected: aria-neo4j running on 0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp

# If rag-neo4j already running, stop it first
docker stop rag-neo4j rag-backend rag-frontend rag-ollama 2>/dev/null || true
```

#### Step 2: Start All Services
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker-compose -f docker/docker-compose.dev.yml up -d
```

**Expected Output:**
```
✔ Container rag-neo4j     Started
✔ Container rag-ollama    Started
✔ Container rag-backend   Started
✔ Container rag-frontend  Started
```

#### Step 3: Wait for Services to Be Healthy
```bash
# Wait 30-60 seconds, then check
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected Status (after ~60 seconds):**
```
NAMES          STATUS                 PORTS
rag-neo4j      Up 60s (healthy)       0.0.0.0:7475->7474/tcp, 0.0.0.0:7688->7687/tcp
rag-ollama     Up 60s                 0.0.0.0:11434->11434/tcp
rag-backend    Up 60s (healthy)       0.0.0.0:8000->8000/tcp
rag-frontend   Up 60s                 0.0.0.0:5173->5173/tcp
aria-neo4j     Up (from before)       0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
```

**⚠️ Troubleshooting - If unhealthy after 2 minutes:**
```bash
# Check logs
docker logs rag-backend --tail 50
docker logs rag-neo4j --tail 50
```

---

### Phase 0.4: Pull Mistral Model

#### Step 1: Pull Model (5.2GB download)
```bash
docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M
```

**Expected Output:**
```
pulling manifest
pulling xxxxx... 100%
pulling yyyyy... 100%
verifying sha256 digest
writing manifest
success
```

**⏱️ Duration:** ~5-10 minutes (depending on internet speed)

#### Step 2: Verify Model Installed
```bash
docker exec rag-ollama ollama list
```

**Expected Output:**
```
NAME                          ID              SIZE    MODIFIED
mistral:7b-instruct-q5_K_M    xxxxxxxxxxxxx   5.2GB   X seconds ago
```

---

### Phase 0.5: Test All Services

#### Test 1: Neo4j Browser
```bash
# Test HTTP interface
curl -s http://localhost:7475 | grep -o '"neo4j_version":"[^"]*"'
# Expected: "neo4j_version":"5.25.1"

# Access in browser:
open http://localhost:7475
# Login: neo4j / diveteacher_dev_2025
```

**AI Agent Note:** Neo4j browser on **port 7475** (not 7474, which is aria-neo4j)

#### Test 2: Backend API Health
```bash
curl -s http://localhost:8000/api/health | jq '.'
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T...",
  "services": {
    "neo4j": "connected",
    "ollama": "available"
  }
}
```

#### Test 3: Frontend
```bash
# Test HTTP response
curl -s -I http://localhost:5173 | head -1
# Expected: HTTP/1.1 200 OK

# Access in browser:
open http://localhost:5173
```

#### Test 4: Ollama + Mistral Inference
```bash
docker exec rag-ollama ollama run mistral:7b-instruct-q5_K_M "Say 'DiveTeacher is ready!' in one sentence." --verbose 2>/dev/null
```

**Expected Output:**
```
DiveTeacher is ready to help you master scuba diving!
```

**AI Agent Success Criteria:**
- ✅ All 4 tests return expected outputs
- ✅ No errors in docker logs
- ✅ All containers status = "healthy" or "Up"

---

## 🌐 Access Points (Local Development)

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Frontend** | http://localhost:5173 | N/A | Upload docs, chat interface |
| **Backend API** | http://localhost:8000/docs | N/A | FastAPI Swagger docs |
| **Neo4j Browser** | http://localhost:7475 | neo4j / diveteacher_dev_2025 | Graph visualization |
| **Ollama API** | http://localhost:11434 | N/A | LLM inference endpoint |

**⚠️ AI Agent Warning:** Do NOT use port 7474 (that's aria-neo4j). Use **7475** for DiveTeacher.

---

## 🧪 Manual Testing Workflow

### Test 1: Upload Document
1. Open http://localhost:5173
2. Click "Choose File" → Select a test PDF (any PDF < 10MB)
3. Click "Upload"
4. **Expected:** Progress bar → "Processing complete"
5. **AI Agent Check:** Monitor backend logs for processing:
```bash
docker logs rag-backend -f
# Look for: "Document processed successfully"
```

### Test 2: Query Knowledge Graph
1. In chat interface, type: "What is in the uploaded document?"
2. **Expected:** Streaming response (tokens appear one by one)
3. **Expected:** Response cites content from uploaded PDF
4. **AI Agent Check:** Response should NOT hallucinate (only use doc content)

### Test 3: Verify Knowledge Graph
1. Open http://localhost:7475
2. Login: neo4j / diveteacher_dev_2025
3. Run query:
```cypher
MATCH (n) RETURN count(n) as total_nodes
```
4. **Expected:** total_nodes > 0 (if document uploaded)

---

## 🔧 Phase 0.7: Advanced Document Processing (IMPLEMENTED)

> **Status:** ✅ Implemented on October 27, 2025  
> **Purpose:** Production-ready RAG pipeline with Docling + HybridChunker + Graphiti  
> **Reference:** `Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md`

### What Changed in Phase 0.7

#### 1. Advanced Docling Integration ✅
**Before Phase 0.7:**
- Basic PDF to Markdown conversion
- No table structure recognition
- No OCR for scanned documents
- Generic error handling

**After Phase 0.7:**
- ✅ `PdfPipelineOptions` configured with OCR + TableFormer ACCURATE mode
- ✅ Singleton pattern for DocumentConverter (performance)
- ✅ Robust validation (file type, size, corruption detection)
- ✅ Timeout management (300s default, configurable)
- ✅ Detailed logging with metrics (pages, tables, images, duration)
- ✅ Specific error types: `ValueError`, `ConversionError`, `TimeoutError`

#### 2. HybridChunker for Semantic Chunking ✅
**New Feature:**
- Docling's `HybridChunker` creates semantically coherent chunks
- Respects document structure (sections, paragraphs, lists, tables)
- Token-aware chunking (max 512 tokens for embedding models)
- Preserves context (includes headers in chunks)
- Metadata-rich: headings, doc_items, origin, provenance (page, bbox)

**Implementation:**
- Module: `backend/app/services/document_chunker.py`
- Tokenizer: `BAAI/bge-small-en-v1.5`
- Config: `max_tokens=512`, `min_tokens=64`, `merge_peers=True`

#### 3. Complete Pipeline Refactor ✅
**New 4-Step Pipeline:**
```
1. Validation      → DocumentValidator (file exists, format, size, readability)
2. Conversion      → Docling (PDF → DoclingDocument with OCR + tables)
3. Chunking        → HybridChunker (semantic boundaries, token limits)
4. Graph Ingestion → Graphiti + Neo4j (chunks → episodes → entities + facts)
```

**Module:** `backend/app/core/processor.py`

#### 4. Graphiti API Corrections ✅
**5 Critical Fixes:**
1. ✅ Parameter rename: `episode_type` → `source`
2. ✅ Timezone-aware datetime: `datetime.now(timezone.utc)`
3. ✅ Call `build_indices_and_constraints()` on first init
4. ✅ Proper connection cleanup: `close_graphiti_client()`
5. ✅ Import `timezone` from `datetime`

**Module:** `backend/app/integrations/graphiti.py`

#### 5. Bug Fixes ✅
- **tqdm threading issue:** Force-reinstall `tqdm==4.66.0` in Dockerfile
- **Async file reading:** Fixed `SpooledTemporaryFile` iteration in upload.py
- **Graphiti singleton:** Proper pattern with `_indices_built` flag

### Files Created (3)
1. `backend/app/services/document_validator.py` - Robust file validation
2. `backend/app/services/document_chunker.py` - HybridChunker wrapper
3. `backend/tests/test_docling_pipeline.py` - Unit tests

### Files Modified (6)
1. `backend/app/integrations/dockling.py` - Complete refactor
2. `backend/app/integrations/graphiti.py` - API corrections + cleanup
3. `backend/app/core/processor.py` - 4-step pipeline
4. `backend/app/main.py` - Shutdown event cleanup
5. `backend/requirements.txt` - +sentence-transformers, +transformers
6. `backend/Dockerfile` - Force-reinstall tqdm fix

### Testing Phase 0.7 Implementation

#### Quick Validation (After Phase 0.7)
```bash
# 1. Rebuild backend with new code
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker-compose -f docker/docker-compose.dev.yml build backend
docker-compose -f docker/docker-compose.dev.yml restart backend

# 2. Check logs for new features
docker logs rag-backend | grep -E "(Initializing|HybridChunker|DocumentConverter)"
# Expected: "Initializing Docling DocumentConverter"
# Expected: "DocumentConverter initialized (ACCURATE mode + OCR)"
# Expected: "Initializing HybridChunker"

# 3. Test upload with curl
curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/Niveau 4 GP.pdf" \
  -w "\nHTTP Status: %{http_code}\n"

# Expected:
# {
#   "upload_id": "uuid...",
#   "filename": "Niveau 4 GP.pdf",
#   "status": "processing",
#   "message": "Document uploaded successfully and processing started"
# }
# HTTP Status: 200

# 4. Monitor processing (replace {upload_id})
docker logs -f rag-backend | grep "\[{upload_id}\]"

# Expected logs:
# [upload_id] Starting document processing
# [upload_id] Step 1/4: Docling conversion
# [upload_id] ✅ Conversion completed in X.XXs
# [upload_id] Step 2/4: Semantic chunking
# [upload_id] ✅ Created N semantic chunks
# [upload_id] Step 3/4: Neo4j ingestion
# [upload_id] ✅ Ingestion completed in X.XXs
# [upload_id] ✅ Processing COMPLETE (X.XXs)

# 5. Check status via API
curl http://localhost:8000/api/upload/status/{upload_id} | python3 -m json.tool

# Expected response:
# {
#   "status": "completed",
#   "stage": "completed",
#   "progress": 100,
#   "num_chunks": 42,    # ← NEW in Phase 0.7
#   "metadata": {
#     "num_pages": 10,
#     "num_tables": 3,
#     ...
#   },
#   "durations": {       # ← NEW in Phase 0.7
#     "conversion": 15.3,
#     "chunking": 3.2,
#     "ingestion": 8.7,
#     "total": 27.2
#   }
# }
```

#### Neo4j Verification (Phase 0.7 Results)
```cypher
# Open http://localhost:7475
# Login: neo4j / diveteacher_dev_2025

# Query 1: Count nodes after Phase 0.7
MATCH (n) RETURN count(n) as total_nodes

# Query 2: View entities with summaries
MATCH (n:Entity)
RETURN n.name, n.summary, n.created_at
LIMIT 10

# Query 3: View facts/edges with temporal info
MATCH (n)-[r:RELATES_TO]->(m)
RETURN n.name, r.fact, m.name, r.valid_at, r.invalid_at
LIMIT 10

# Expected: Nodes and relationships from uploaded PDF chunks
```

### Troubleshooting Phase 0.7

#### Issue: tqdm._lock AttributeError
**Symptom:** Backend crashes with `'tqdm' object has no attribute '_lock'`

**Root Cause:** tqdm 4.67.1+ removed `_lock` attribute, breaking Docling threading

**Solution:**
```bash
# Already fixed in Dockerfile (force-reinstall tqdm==4.66.0)
# If you see this error, rebuild:
docker-compose -f docker/docker-compose.dev.yml build backend --no-cache
docker-compose -f docker/docker-compose.dev.yml restart backend
```

#### Issue: Graphiti add_episode fails
**Symptom:** Error "unexpected keyword argument 'episode_type'"

**Root Cause:** Graphiti API changed parameter names

**Solution:**
Already fixed in `backend/app/integrations/graphiti.py`:
- Use `source=EpisodeType.text` (not `episode_type=`)
- Use `datetime.now(timezone.utc)` for `reference_time`

#### Issue: HybridChunker ModuleNotFoundError
**Symptom:** "No module named 'sentence_transformers'"

**Solution:**
```bash
# Already in requirements.txt, but if missing:
docker exec rag-backend pip install sentence-transformers==3.3.1 transformers==4.48.3
# Then restart:
docker restart rag-backend
```

#### Issue: Docling conversion timeout
**Symptom:** Processing stuck at "Step 1/4: Docling conversion"

**Solutions:**
1. **Increase timeout** in `.env`:
```bash
DOCLING_TIMEOUT=600  # 10 minutes for very large PDFs
```

2. **Check PDF is valid:**
```bash
# Validate before upload
file TestPDF/your-document.pdf
# Expected: PDF document, version X.X
```

3. **Monitor memory:**
```bash
docker stats rag-backend
# If MEM USAGE > 90%, increase Docker memory in Docker Desktop settings
```

### Phase 0.7 Success Criteria

**✅ All Validated:**
- PDF processing completes without crashes
- HybridChunker creates semantic chunks (visible in logs)
- Status API returns `num_chunks` and `durations`
- Neo4j contains entities and facts from uploaded document
- No tqdm threading errors
- Docling models load successfully
- Logs show detailed metrics (pages, tables, conversion time)

**⏳ Pending Full Validation:**
- Table extraction accuracy (needs manual verification with complex tables)
- Neo4j community building (run `build_communities()` after multiple docs)

---

## 🔧 Phase 0.8: Neo4j RAG Optimization (IMPLEMENTED)

> **Status:** ✅ Implemented on October 27, 2025  
> **Purpose:** Production-ready RAG queries with full-text search + hybrid search  
> **Reference:** `Devplan/PHASE-0.8-NEO4J-IMPLEMENTATION.md`

### What Changed in Phase 0.8

#### 1. Neo4jClient Refactored ✅
**Before Phase 0.8:**
- Used `AsyncGraphDatabase` (deprecated pattern)
- Keyword matching naïve (pas compatible Graphiti schema)
- Pas d'indexes optimisés pour RAG
- 2 drivers Neo4j (conflit potentiel)

**After Phase 0.8:**
- ✅ `GraphDatabase.driver()` + `execute_query()` (Neo4j 2025 best practices)
- ✅ Connection pool optimized (max 50 connections)
- ✅ Full-text search sur `Episode.content`
- ✅ Entity + graph traversal queries
- ✅ Hybrid search (Episodes + Entities combinés)
- ✅ Error handling spécifique (ServiceUnavailable, CypherSyntaxError, etc.)

#### 2. RAG Indexes Créés ✅
Trois nouveaux indexes pour optimiser queries RAG:
- `episode_content` (FULLTEXT) - Search dans chunks de documents
- `entity_name_idx` (RANGE) - Lookup rapide d'entités
- `episode_date_idx` (RANGE) - Filter par date

#### 3. RAG Queries Améliorées ✅
Trois méthodes de search disponibles:

**Full-Text Search:**
```python
# Search dans Episode.content (chunks de documents)
results = neo4j_client.query_context_fulltext("plongée niveau 4", top_k=5)
# Returns: [{"text": "...", "score": 0.85, "source": "..."}]
```

**Entity Search:**
```python
# Search entités + relationships (graph traversal)
entities = neo4j_client.query_entities_related("niveau", depth=2)
# Returns: [{"entity": "Niveau 4", "related": [...]}]
```

**Hybrid Search (BEST):**
```python
# Combine full-text + entity search
context = neo4j_client.query_context_hybrid("niveau 4 prérequis", top_k=5)
# Returns: {"episodes": [...], "entities": [...], "total": 10}
```

#### 4. RAG Chain Updated ✅
Prompt construction améliorer pour utiliser hybrid context:
- Section "DOCUMENT EXCERPTS" pour chunks
- Section "RELATED CONCEPTS & ENTITIES" pour graph
- Citations avec scores et relations
- System prompt DiveTeacher-specific

### Files Modified in Phase 0.8

**Created:**
1. `backend/app/integrations/neo4j_indexes.py` (189 lignes)
2. `backend/scripts/test_neo4j_rag.py` (200+ lignes)

**Modified:**
3. `backend/app/integrations/neo4j.py` - Refactor complet (300 lignes)
4. `backend/app/core/rag.py` - Hybrid context support
5. `backend/app/main.py` - Index creation au startup
6. `backend/app/api/graph.py` - Synchronous queries

### Testing Phase 0.8 Implementation

#### Quick Validation (After Phase 0.8)
```bash
# 1. Rebuild backend avec nouveau code
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml build backend
docker compose -f docker/docker-compose.dev.yml up -d backend

# 2. Check backend logs pour indexes
docker logs backend 2>&1 | grep -i "index"
# Expected:
# ✅ Created 3 RAG indexes: episode_content, entity_name_idx, episode_date_idx
# 📊 Total indexes: 8 (RAG: 3, Graphiti: 5)

# 3. Run E2E test script
docker exec -it backend python scripts/test_neo4j_rag.py
```

**Expected Output:**
```
🧪 PHASE 0.8 - NEO4J RAG IMPLEMENTATION - E2E TESTS
==========================================================

🧪 Test 1: Neo4j Connection
✅ Neo4j connected successfully

🧪 Test 2: RAG Indexes Verification
✅ Total indexes: 8
   RAG indexes: 3
   Graphiti indexes: 5
   
   RAG Indexes Details:
     - episode_content (FULLTEXT, ONLINE)
     - entity_name_idx (RANGE, ONLINE)
     - episode_date_idx (RANGE, ONLINE)

🧪 Test 3: Full-Text Search (Episode.content)
✅ Full-text search returned 3 results
   [1] Score: 0.850
       Source: Niveau 4 GP.pdf - Chunk 12
       Text: Le niveau 4 FFESSM permet de plonger jusqu'à 60 mètres...
   [2] Score: 0.742
       ...

🧪 Test 4: Entity Search (Entity.name + RELATES_TO)
✅ Entity search found 5 entities
   [1] Niveau 4 (CERTIFICATION)
       Description: Certification FFESSM permettant...
       Related entities: 3
   [2] Niveau 3 (CERTIFICATION)
       ...

🧪 Test 5: Hybrid Search (Episodes + Entities)
✅ Hybrid search completed
   Episodes: 3
   Entities: 2
   Total: 5

🧪 Test 6: RAG Query (retrieve_context + LLM)
✅ RAG context retrieval completed
   Episodes: 3
   Entities: 2
   
   ✅ RAG pipeline is functional!

📊 TEST SUMMARY
==========================================================
✅ Phase 0.8 Implementation Tests COMPLETE
```

#### Neo4j Browser Verification (Phase 0.8)
```cypher
# Open http://localhost:7475
# Login: neo4j / diveteacher_dev_2025

# Query 1: List all indexes
CALL db.indexes()
YIELD name, type, state, labelsOrTypes, properties
WHERE name CONTAINS 'episode' OR name CONTAINS 'entity'
RETURN name, type, state, labelsOrTypes, properties

# Expected:
# episode_content | FULLTEXT | ONLINE | [Episode] | [content]
# entity_name_idx | RANGE | ONLINE | [Entity] | [name]
# episode_date_idx | RANGE | ONLINE | [Episode] | [valid_at]

# Query 2: Test full-text search
CALL db.index.fulltext.queryNodes('episode_content', 'plongée') 
YIELD node, score
RETURN node.content AS text, score
ORDER BY score DESC
LIMIT 5

# Query 3: Test entity + relationships
MATCH (e:Entity)-[r:RELATES_TO]-(related:Entity)
WHERE toLower(e.name) CONTAINS 'niveau'
RETURN e.name, type(r), r.fact, related.name
LIMIT 10
```

#### API Test (Phase 0.8)
```bash
# Test RAG query avec hybrid search
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quels sont les prérequis pour le niveau 4 FFESSM?",
    "stream": false
  }'
```

**Expected Response:**
```json
{
  "question": "Quels sont les prérequis pour le niveau 4 FFESSM?",
  "answer": "Selon les documents FFESSM [Chunk 1, Chunk 3], les prérequis pour le niveau 4 sont...\n\nLes entités liées montrent que **Niveau 3** est un prérequis...",
  "context": {
    "episodes": [...],  // Chunks with scores
    "entities": [...]   // Entities with relationships
  },
  "num_sources": 5
}
```

### Troubleshooting Phase 0.8

#### Issue: Index 'episode_content' Not Found
**Symptom:** `CALL db.index.fulltext.queryNodes('episode_content', ...)` → "Index not found"

**Solution:**
```bash
# 1. Check if indexes were created
docker logs backend 2>&1 | grep "Created.*RAG indexes"

# 2. Manually create index in Neo4j Browser
# http://localhost:7475
CREATE FULLTEXT INDEX episode_content IF NOT EXISTS
FOR (e:Episode) ON EACH [e.content]

# 3. Verify
CALL db.indexes()
YIELD name, state
WHERE name = 'episode_content'
RETURN name, state
# Expected: episode_content | ONLINE
```

#### Issue: Full-Text Search Returns Empty
**Symptom:** `query_context_fulltext()` → `[]`

**Causes & Solutions:**
```bash
# Cause 1: Pas de documents ingérés
# Solution: Upload un PDF test
curl -F 'file=@test.pdf' http://localhost:8000/api/upload

# Cause 2: Graphiti processing pas fini
# Solution: Wait 1-2 min, check backend logs
docker logs backend -f | grep "ingested\|communities"

# Cause 3: Episodes n'ont pas de content
# Solution: Check Neo4j
# Neo4j Browser: MATCH (e:Episode) RETURN e.content LIMIT 5
```

#### Issue: Entity Search No Results
**Symptom:** `query_entities_related()` → `[]`

**Solution:**
```bash
# Check if Graphiti extracted entities
# Neo4j Browser:
MATCH (e:Entity) RETURN count(e) as total_entities

# If 0, Graphiti needs more time or documents
# Wait and check backend logs:
docker logs backend 2>&1 | grep "Building communities"
```

### Phase 0.8 Success Criteria

**✅ All Validated:**
- Neo4j connection uses `GraphDatabase.driver()` (not Async)
- 3 RAG indexes created and ONLINE
- Full-text search returns scored results
- Entity search traverses relationships
- Hybrid search combines both
- RAG prompt uses hybrid context
- E2E test script passes all 6 tests

---

## 🛑 Common Issues & Solutions

### Issue 1: Port Already Allocated (7474 or 8000)
**Symptom:**
```
Bind for 0.0.0.0:7474 failed: port is already allocated
```

**Root Cause:** Old containers or aria-neo4j using ports

**Solution:**
```bash
# Check what's using ports
docker ps --filter "publish=7474" --filter "publish=8000"

# If DiveTeacher containers need restart:
docker stop rag-neo4j rag-backend rag-frontend rag-ollama
docker-compose -f docker/docker-compose.dev.yml up -d

# NEVER stop aria-neo4j (it's for another app)
```

**AI Agent Rule:** If aria-neo4j is on 7474/7687, DiveTeacher MUST use 7475/7688

### Issue 2: Backend Can't Connect to Neo4j
**Symptom:** Backend logs show "Failed to connect to Neo4j"

**Solution:**
```bash
# 1. Verify Neo4j is healthy
docker ps --filter "name=rag-neo4j"

# 2. Check password matches
cat .env | grep NEO4J_PASSWORD

# 3. Restart backend
docker restart rag-backend

# 4. Check backend logs
docker logs rag-backend --tail 50
```

### Issue 3: Ollama Model Not Found
**Symptom:** Chat returns error "model not found"

**Solution:**
```bash
# 1. Check if model exists
docker exec rag-ollama ollama list

# 2. If not, pull it
docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M

# 3. Verify (should show 5.2GB)
docker exec rag-ollama ollama list
```

### Issue 4: Frontend Shows "Network Error"
**Symptom:** Frontend can't reach backend API

**Solution:**
```bash
# 1. Check backend is running
curl http://localhost:8000/api/health

# 2. Check VITE_API_URL in frontend container
docker exec rag-frontend env | grep VITE_API_URL
# Expected: VITE_API_URL=http://localhost:8000

# 3. Restart frontend
docker restart rag-frontend
```

### Issue 5: Docker Daemon Not Running
**Symptom:** "Cannot connect to the Docker daemon"

**Solution:**
```bash
# Open Docker Desktop manually
open -a Docker

# Wait 30 seconds, then verify
docker ps
```

---

## 🔄 Daily Development Workflow

### Starting Work
```bash
# 1. Start Docker Desktop (if not running)
open -a Docker

# 2. Start DiveTeacher services
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker-compose -f docker/docker-compose.dev.yml up -d

# 3. Check all healthy
docker ps

# 4. Open frontend
open http://localhost:5173
```

### Stopping Work
```bash
# Stop services (preserves data)
docker-compose -f docker/docker-compose.dev.yml stop

# OR completely remove (clears data)
docker-compose -f docker/docker-compose.dev.yml down -v
```

---

## 📦 Docker Services Explanation (For AI Understanding)

### Service: rag-neo4j
- **Image:** neo4j:5.25.1
- **Purpose:** Graph database for knowledge graph (entities, relationships)
- **Ports:** 7475 (HTTP), 7688 (Bolt)
- **Data:** Persisted in named volume `neo4j-data`
- **Health:** Checked via `cypher-shell` every 10s

### Service: rag-ollama
- **Image:** ollama/ollama:latest
- **Purpose:** LLM inference server (runs Mistral 7B)
- **Port:** 11434 (API)
- **Data:** Models stored in volume `ollama-models`
- **GPU:** Uses Mac M1 Metal via Docker

### Service: rag-backend
- **Build:** backend/Dockerfile
- **Purpose:** FastAPI server (RAG, upload, processing)
- **Port:** 8000 (API)
- **Dependencies:** neo4j, ollama
- **Health:** Checked via `/api/health` every 10s

### Service: rag-frontend
- **Build:** frontend/Dockerfile
- **Purpose:** React dev server (Vite)
- **Port:** 5173 (HTTP)
- **Dependencies:** backend

---

## ⏭️ Next Steps After Phase 0

Once Phase 0 is complete (all tests pass):

### Phase 1.0: RAG Query Implementation ✅ COMPLETE (October 28, 2025)

**Objective:** Implement downstream RAG query pipeline with Qwen 2.5 7B Q8_0 for optimal quality.

**Status:** ✅ FULLY OPERATIONAL

**What was implemented:**
1. ✅ **Ollama Docker Configuration**
   - Environment variables for optimal performance
   - Memory limit: 16GB
   - Healthcheck fixed (`/api/version`)
   - Model: Qwen 2.5 7B Q8_0 (8.1GB)

2. ✅ **Backend RAG API** (`backend/app/api/query.py`)
   - `POST /api/query/` - Non-streaming query
   - `POST /api/query/stream` - Streaming query (SSE)
   - `GET /api/query/health` - Health check
   
3. ✅ **Configuration Updates**
   - `backend/app/core/config.py` - RAG + Qwen settings
   - `.env` - Model configuration
   - Docker Compose - Ollama optimization

4. ✅ **Testing & Monitoring**
   - `scripts/test_rag_query.sh` - 4 automated tests
   - `scripts/monitor_ollama.sh` - Performance monitoring
   - All tests passing (health, query, streaming, errors)

5. ✅ **Documentation**
   - `ENV_CONFIGURATION_QWEN.md` - Environment variables
   - `docs/SECRETS-MANAGEMENT.md` - Production secrets
   - `Devplan/STATUS-PHASE-1.0-COMPLETION-REPORT.md` - Complete report

**Quick Validation:**
```bash
# Health check
curl http://localhost:8000/api/query/health | jq

# Expected output:
# {
#   "status": "healthy",
#   "provider": "ollama",
#   "model": "qwen2.5:7b-instruct-q8_0"
# }

# Run full test suite
./scripts/test_rag_query.sh

# Expected: 4/4 tests passing
```

**Performance Metrics (Local Dev - Mac M1 Max CPU):**
- Model: Qwen 2.5 7B Q8_0 (8.1GB)
- Memory usage: 8.7GB / 16GB Docker limit
- Inference speed: 10-15 tok/s (CPU-only, expected)
- Production target: 40-60 tok/s (GPU on DigitalOcean RTX 4000 Ada)

**Key Files:**
- API Implementation: `backend/app/api/query.py`
- RAG Logic: `backend/app/core/rag.py`
- LLM Client: `backend/app/core/llm.py`
- Configuration: `backend/app/core/config.py`
- Docker Compose: `docker/docker-compose.dev.yml`

**References:**
- Implementation Plan: `Devplan/PHASE-1.0-RAG-QUERY-IMPLEMENTATION.md`
- Completion Report: `Devplan/STATUS-PHASE-1.0-COMPLETION-REPORT.md`
- GPU Deployment Guide: `resources/251028-rag-gpu-deployment-guide.md`

---

### Phase 1.1: Multi-User Authentication (3-4 days)
1. Create Supabase project (cloud, free tier)
2. Generate Supabase API keys
3. Add keys to `.env`
4. Implement auth UI (login, signup)
5. Protect admin routes

**AI Agent Note:** Supabase configuration will be documented in Phase 1 setup guide.

### Production Deployment (Phase 9 ONLY)
**⚠️ DO NOT DO THIS YET - Wait until Phases 0-8 are complete**

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

---

## 📚 Related Documentation

For AI agents working on DiveTeacher:
1. **CURRENT-CONTEXT.md** - Persistent session memory (READ FIRST)
2. **GOAL.md** - Project objectives and architecture
3. **DIVETEACHER-V1-PLAN.md** - Complete 9-phase development plan
4. **docs/DEPLOYMENT.md** - Production deployment (Phase 9)
5. **docs/API.md** - Backend API reference
6. **docs/ARCHITECTURE.md** - System design deep-dive

---

## 🤖 AI Agent Checklist

Before declaring Phase 0 complete:

- [ ] `.env` file exists with correct settings
- [ ] Docker Desktop running
- [ ] All 4 containers healthy (neo4j, ollama, backend, frontend)
- [ ] Mistral model pulled (5.2GB)
- [ ] Neo4j accessible on port 7475
- [ ] Backend health check returns "connected"
- [ ] Frontend loads in browser
- [ ] Mistral inference test successful
- [ ] No errors in any container logs
- [ ] Test PDF upload works
- [ ] Test chat query returns response
- [ ] Test Neo4j has nodes after upload

**Success Criteria:** All boxes checked = Phase 0 complete ✅

---

**Last Updated:** October 27, 2025  
**Version:** DiveTeacher V1 - Phase 0  
**AI Agent:** Claude Sonnet 4.5 optimized
