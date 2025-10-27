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

### Phase 1: Multi-User Authentication (3-4 days)
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
