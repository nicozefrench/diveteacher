# 📚 Scripts Usage Guide - DiveTeacher RAG System

> **Last Updated:** October 31, 2025  
> **Architecture:** ARIA v2.0.0 (Sequential + ARIA Chunking)

---

## ⚠️ CRITICAL: Two Different Workflows

### 🧪 E2E TESTING (Clean Slate)

**Purpose:** Test system with fresh database  
**Script:** `./scripts/init-e2e-test.sh`  
**Default Behavior:** ⚠️ **CLEANS DATABASE**

```bash
# Full E2E test preparation (DEFAULT)
./scripts/init-e2e-test.sh

What it does:
✅ Check containers running
⚠️  CLEAN Neo4j database (DELETE ALL DATA!)
✅ Warm up Docling models
✅ Warm up ARIA Chunker
✅ Verify all services
✅ Show monitoring commands

Result: 0 nodes, 0 relationships (fresh start)
Use for: E2E testing with clean environment
```

---

### 🏭 PRODUCTION INGESTION (Preserve Data)

**Purpose:** Add documents to existing knowledge graph  
**Method:** Just start containers (warmup runs automatically)  
**Behavior:** ✅ **PRESERVES DATABASE**

```bash
# Production ingestion workflow
docker-compose -f docker/docker-compose.dev.yml up -d

What happens:
✅ Containers start
✅ Warmup runs automatically (backend entrypoint)
   • Docling models warmed up
   • ARIA Chunker initialized
   • ⚠️  Database NOT touched!
✅ System ready for uploads
✅ DocumentQueue ready (FIFO)

Result: Database unchanged, models ready
Use for: Adding 100 PDFs to existing knowledge graph
```

**Alternative (if you want explicit warmup check):**
```bash
# Start containers
docker-compose up -d

# Verify warmup with --skip-cleanup flag
./scripts/init-e2e-test.sh --skip-cleanup

What it does:
✅ Check containers
✅ SKIP database cleanup (--skip-cleanup)
✅ Warm up models (if not already)
✅ Verify services
✅ Show current DB state (X nodes, Y relationships)

Result: Database preserved, verification complete
```

---

## 📊 Monitoring Tools

### 1. DocumentQueue Monitor (Real-Time)

**Purpose:** Monitor multi-document queue status  
**Script:** `./scripts/monitor-queue.sh [interval]`

```bash
# Monitor queue every 2 seconds (default)
./scripts/monitor-queue.sh

# Monitor queue every 5 seconds
./scripts/monitor-queue.sh 5

What it shows:
• Queue size (documents waiting)
• Current document processing (filename, progress)
• Completed/Failed counts
• Success rate
• Queued documents list (FIFO order)
• Ingestion progress (chunks completed/total)
• ARIA architecture info
```

**When to use:**
- Multi-document ingestion sessions
- Production batch uploads (100 PDFs)
- Monitoring queue health

---

### 2. Ingestion Monitor (Backend Logs)

**Purpose:** Monitor Graphiti ingestion logs in real-time  
**Script:** `./scripts/monitor_ingestion.sh [upload_id]`

```bash
# Monitor all ingestion activity
./scripts/monitor_ingestion.sh

# Monitor specific upload
./scripts/monitor_ingestion.sh c664bc97-87a4-4fc7-a846-8573de0c5a02

What it shows:
• ARIA Chunker logs (RecursiveCharacterTextSplitter)
• SafeIngestionQueue logs (token tracking)
• DocumentQueue logs (sequential processing)
• Graphiti logs (entity extraction)
• Claude API calls
• Chunk-by-chunk progress
• Color-coded output (green=success, red=error)
```

**When to use:**
- Debugging ingestion issues
- Watching real-time processing
- Verifying ARIA chunking (3 chunks vs 204)

---

### 3. Upload Monitor (Status Polling)

**Purpose:** Monitor specific upload to completion  
**Script:** `./scripts/monitor-upload.sh <upload_id>`

```bash
# Monitor upload until completion
./scripts/monitor-upload.sh c664bc97-87a4-4fc7-a846-8573de0c5a02

What it shows:
• Status updates every 5s
• Stage progression
• Progress percentage
• Final metrics (entities, relations, chunks)
• Total time
• Avg time per chunk
```

**When to use:**
- Tracking single document progress
- Getting final metrics
- Timing validation

---

### 4. Backend Queue Test (Integration Test)

**Purpose:** Full integration test with upload + monitoring  
**Script:** `./scripts/test-backend-queue.sh <file.pdf>`

```bash
# Test with test.pdf
./scripts/test-backend-queue.sh TestPDF/test.pdf

# Test with Niveau 1.pdf
./scripts/test-backend-queue.sh "TestPDF/Niveau 1.pdf"

What it does:
✅ Check backend health
✅ Check DocumentQueue status
✅ Upload file
✅ Monitor processing (auto-poll)
✅ Analyze backend logs
✅ Validate ARIA chunking
✅ Verify SafeIngestionQueue
✅ Report final verdict
```

**When to use:**
- Automated testing
- CI/CD pipelines
- Validating system changes

---

## 🎯 Common Scenarios

### Scenario 1: Daily E2E Test (Clean Slate)

```bash
# 1. Initialize for E2E test (cleans DB)
./scripts/init-e2e-test.sh

# 2. Upload test document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/test.pdf"

# 3. Monitor
./scripts/monitor-upload.sh <upload_id>

# 4. Verify
curl -s http://localhost:8000/api/neo4j/stats | jq

Result: Clean test with 0→X nodes
```

---

### Scenario 2: Week 1 Ingestion (100 PDFs)

```bash
# 1. Start system (warmup auto, DB preserved)
docker-compose up -d

# Wait 60s for warmup
sleep 60

# 2. Verify system ready (no cleanup!)
./scripts/init-e2e-test.sh --skip-cleanup --quiet

# 3. Monitor queue in Terminal 1
./scripts/monitor-queue.sh

# 4. Monitor backend in Terminal 2
./scripts/monitor_ingestion.sh

# 5. Upload all PDFs
for pdf in PDFs/*.pdf; do
  curl -X POST http://localhost:8000/api/upload -F "file=@$pdf"
  echo "Queued: $pdf"
done

# 6. Watch queue process all documents
# → Sequential FIFO processing
# → 60s delay between documents
# → 100 PDFs in ~6.5 hours
# → Knowledge graph grows progressively

Result: DB grows from X to X+100 documents
```

---

### Scenario 3: Debug Single Document

```bash
# 1. Keep existing data
./scripts/init-e2e-test.sh --skip-cleanup

# 2. Upload and get ID
RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload \
  -F "file=@problem.pdf")
UPLOAD_ID=$(echo "$RESPONSE" | jq -r '.upload_id')

# 3. Monitor with all tools
# Terminal 1: Queue
./scripts/monitor-queue.sh

# Terminal 2: Backend logs
./scripts/monitor_ingestion.sh $UPLOAD_ID

# Terminal 3: Upload status
./scripts/monitor-upload.sh $UPLOAD_ID

# 4. Analyze results
curl -s http://localhost:8000/api/upload/$UPLOAD_ID/status | jq

Result: Detailed debugging info, DB preserved
```

---

## 🔧 System Architecture (ARIA v2.0.0)

### Processing Pipeline

```
User Upload
    ↓
DocumentQueue (FIFO)
    ↓
Sequential Processing (one at a time)
    ↓
├─ Docling Conversion (~40s)
├─ ARIA Chunking (~0.1s) → 3 chunks (3000 tokens each)
└─ Graphiti Ingestion (~3 min)
   ├─ SafeIngestionQueue (token-aware)
   ├─ Claude Haiku (entity extraction)
   ├─ OpenAI embeddings
   └─ Neo4j storage
    ↓
Knowledge Graph (grows progressively)
```

### Performance

```
Single Document (Niveau 1.pdf):
├─ Chunks: 3 (ARIA pattern)
├─ Time: ~3.9 min
├─ Cost: ~$0.02
└─ Quality: 325 entities, 617 relations

100 Documents Batch:
├─ Time: ~6.5 hours (overnight)
├─ Cost: ~$2 total
└─ Mode: Sequential FIFO + 60s inter-document delays
```

---

## 🚨 Common Mistakes to Avoid

### ❌ MISTAKE #1: Using init-e2e-test.sh for Production

```bash
# ❌ WRONG (for production ingestion):
./scripts/init-e2e-test.sh
# → DELETES ALL YOUR DATA!

# ✅ CORRECT (for production ingestion):
docker-compose up -d
# → Warmup runs auto, DB preserved
```

---

### ❌ MISTAKE #2: Skipping Warmup for E2E Tests

```bash
# ❌ WRONG (cold start, slow first upload):
./scripts/init-e2e-test.sh --skip-warmup

# ✅ CORRECT (warmed up, fast uploads):
./scripts/init-e2e-test.sh
# → Full warmup, ready for immediate testing
```

---

### ❌ MISTAKE #3: Not Monitoring Queue During Batch

```bash
# ❌ WRONG (upload 100 PDFs blindly):
for pdf in *.pdf; do curl ...; done
# → No visibility, can't debug issues

# ✅ CORRECT (monitor while uploading):
# Terminal 1: Monitor queue
./scripts/monitor-queue.sh

# Terminal 2: Upload PDFs
for pdf in *.pdf; do curl ...; done
# → See queue grow, processing status, success rate
```

---

## 📖 Quick Reference

| Task | Command | Cleans DB? |
|------|---------|------------|
| **E2E Test** | `./scripts/init-e2e-test.sh` | ✅ YES |
| **Production Warmup** | `docker-compose up -d` | ❌ NO |
| **Verify System (Production)** | `./scripts/init-e2e-test.sh --skip-cleanup` | ❌ NO |
| **Monitor Queue** | `./scripts/monitor-queue.sh` | ❌ NO |
| **Monitor Upload** | `./scripts/monitor-upload.sh <id>` | ❌ NO |
| **Monitor Ingestion** | `./scripts/monitor_ingestion.sh` | ❌ NO |
| **Test Backend** | `./scripts/test-backend-queue.sh file.pdf` | ❌ NO |

---

## 🎯 Summary

**For E2E Testing (Clean Start):**
```bash
./scripts/init-e2e-test.sh  # ⚠️  CLEANS DB!
```

**For Production Ingestion (Preserve DB):**
```bash
docker-compose up -d  # ✅ DB preserved, warmup automatic
```

**Remember:**
- ✅ `init-e2e-test.sh` = Testing tool (cleans by default)
- ✅ `docker-compose up` = Production tool (preserves DB)
- ✅ Use `--skip-cleanup` flag to preserve DB with init script
- ✅ Warmup runs automatically on backend start
- ✅ All monitoring tools preserve DB (read-only)

---

**Questions? Check logs:** `docker logs rag-backend`

