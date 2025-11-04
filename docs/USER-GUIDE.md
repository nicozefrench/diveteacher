# 👤 User Guide - Simple Commands for DiveTeacher

> **Last Updated:** October 31, 2025  
> **Purpose:** Simple prompts for AI agent to prepare system  
> **Architecture:** ARIA v2.0.0 (Sequential + ARIA Chunking)

---

## 🎯 Quick Commands

### For E2E Testing (Clean Database)

**What to say to AI agent:**

```
"prep e2e"
"init test"
"clean test"
"test propre"
"prepare for e2e test"
```

**What AI agent will do:**
```bash
./scripts/init-e2e-test.sh

Result:
⚠️  Database CLEANED (0 nodes, 0 relationships)
✅ Docling models warmed up
✅ ARIA Chunker ready
✅ DocumentQueue idle
✅ System ready for clean test
```

**When to use:**
- Before running E2E tests
- When you want fresh start
- When testing new features
- When validating fixes

---

### For Production Ingestion (Preserve Database)

**What to say to AI agent:**

```
"prep ingestion"
"warmup prod"
"ready for batch"
"prépare 100 pdfs"
"prepare for production"
"warmup without cleanup"
```

**What AI agent will do:**
```bash
docker-compose up -d
# OR
./scripts/init-e2e-test.sh --skip-cleanup

Result:
✅ Database PRESERVED (693 nodes kept)
✅ Docling models warmed up
✅ ARIA Chunker ready
✅ DocumentQueue ready
✅ System ready for uploads (additive)
```

**When to use:**
- Before ingesting 100 PDFs
- When adding to existing knowledge graph
- Production ingestion sessions
- Week 1 launch preparation

---

## 📊 Monitoring Commands

### Monitor DocumentQueue

**What to say:**

```
"monitor queue"
"show queue status"
"check queue"
```

**What AI agent will do:**
```bash
./scripts/monitor-queue.sh

Shows:
• Queue size (documents waiting)
• Current document processing
• Completed/Failed counts
• Success rate
• Real-time updates every 2s
```

---

### Monitor Backend Logs

**What to say:**

```
"monitor ingestion"
"watch backend"
"show logs"
```

**What AI agent will do:**
```bash
./scripts/monitor_ingestion.sh

Shows:
• ARIA Chunker logs
• SafeIngestionQueue (token tracking)
• DocumentQueue (sequential processing)
• Graphiti entity extraction
• Color-coded output
```

---

### Monitor Specific Upload

**What to say:**

```
"monitor upload <upload_id>"
"track <upload_id>"
"check upload <id>"
```

**What AI agent will do:**
```bash
./scripts/monitor-upload.sh <upload_id>

Shows:
• Stage progression
• Progress percentage
• Final metrics (entities, relations)
• Total time
```

---

## 🎯 Complete Workflows

### Workflow 1: Daily E2E Test

**User says:**
```
"prep e2e"
```

**AI agent does:**
```bash
./scripts/init-e2e-test.sh
```

**User says:**
```
"ok je fais le test, monitor backend"
```

**AI agent does:**
```bash
./scripts/monitor_ingestion.sh
# (Agent watches backend logs)
```

**User:** Uploads test.pdf via UI  
**AI agent:** Reports results after completion

---

### Workflow 2: Week 1 Ingestion (100 PDFs)

**User says:**
```
"prep ingestion"
```

**AI agent does:**
```bash
docker-compose up -d
sleep 60  # Wait for warmup
./scripts/init-e2e-test.sh --skip-cleanup --quiet  # Verify
```

**User says:**
```
"monitor queue"
```

**AI agent does:**
```bash
./scripts/monitor-queue.sh
# (Agent shows real-time queue status)
```

**User:** Uploads PDFs (manually or script)  
**AI agent:** Monitors and reports progress

---

### Workflow 3: Debug Single Document

**User says:**
```
"prep ingestion" 
(preserve data for debugging)
```

**AI agent does:**
```bash
./scripts/init-e2e-test.sh --skip-cleanup
```

**User:** Uploads problem.pdf, gets upload_id

**User says:**
```
"monitor upload abc123..."
```

**AI agent does:**
```bash
./scripts/monitor-upload.sh abc123...
# (Agent tracks to completion)
```

---

## 📖 Keyword Reference

### Preparation Keywords

| Keyword | Script | Cleans DB? | Use Case |
|---------|--------|------------|----------|
| **prep e2e** | `init-e2e-test.sh` | ✅ YES | E2E testing |
| **prep ingestion** | `docker-compose up -d` | ❌ NO | Production |
| **warmup** | `init --skip-cleanup` | ❌ NO | Verification |
| **init test** | `init-e2e-test.sh` | ✅ YES | Testing |
| **clean test** | `init-e2e-test.sh` | ✅ YES | Testing |

### Monitoring Keywords

| Keyword | Script | What It Shows |
|---------|--------|---------------|
| **monitor queue** | `monitor-queue.sh` | Queue status, FIFO order |
| **monitor ingestion** | `monitor_ingestion.sh` | Backend logs, ARIA logs |
| **monitor upload <id>** | `monitor-upload.sh` | Single upload tracking |
| **check queue** | `curl queue/status` | Queue API status |

---

## 🚨 Common Mistakes to Avoid

### ❌ MISTAKE #1: Using "prep e2e" for Production

```
User: "prep e2e" (before uploading 100 PDFs)
Result: ⚠️  ALL DATA DELETED!

✅ CORRECT:
User: "prep ingestion"
Result: ✅ Data preserved, ready for uploads
```

---

### ❌ MISTAKE #2: Not Monitoring During Batch

```
User: (uploads 100 PDFs without monitoring)
Result: ⚠️  No visibility, can't debug issues

✅ CORRECT:
User: "monitor queue" (in separate terminal)
Result: ✅ Real-time status, see progress
```

---

### ❌ MISTAKE #3: Forgetting Database State

```
User: "prep e2e" then "monitor queue"
Agent: Queue shows 0 completed (DB was cleaned)
User: Confused why old data is gone

✅ REMEMBER:
"prep e2e" = Clean slate (0 nodes)
"prep ingestion" = Keep data (693 nodes)
```

---

## 💡 Tips & Best Practices

### Tip #1: Check Database Before Cleanup

```
User: "show me neo4j stats"
Agent: 693 nodes, 1960 relationships

User: "prep e2e" ← Now you know you'll lose 693 nodes
```

---

### Tip #2: Use Quiet Mode for Scripts

```
User: "prep ingestion quiet"
Agent: ./scripts/init-e2e-test.sh --skip-cleanup --quiet
# → Minimal output, just status checks
```

---

### Tip #3: Monitor Queue During Large Batches

```
User: "prep ingestion"
User: "monitor queue"
# → Open in separate terminal
# → Upload 100 PDFs
# → Watch queue process them one by one
```

---

## 🎯 Command Cheat Sheet

### I want to... | I say...
- **Test with clean DB** → "prep e2e"
- **Add 100 PDFs to existing graph** → "prep ingestion"
- **See what's in queue** → "monitor queue"
- **Watch backend processing** → "monitor ingestion"
- **Track specific upload** → "monitor upload <id>"
- **Check system status** → "check health"
- **See Neo4j stats** → "show neo4j stats"

---

## 📚 Advanced Usage

### Custom Scenarios

**Scenario: Test without cleanup, with warmup**
```
User: "init test but keep data"
Agent: ./scripts/init-e2e-test.sh --skip-cleanup
```

**Scenario: Cleanup without warmup**
```
User: "clean db no warmup"
Agent: ./scripts/init-e2e-test.sh --skip-warmup
```

**Scenario: Silent verification**
```
User: "verify system quiet"
Agent: ./scripts/init-e2e-test.sh --skip-cleanup --quiet
```

---

## 🔄 State Management

### Database States

**State A: Empty (After "prep e2e")**
```
Nodes: 0
Relationships: 0
Use: E2E testing, clean validation
```

**State B: Populated (After "prep ingestion")**
```
Nodes: 693+ (preserved)
Relationships: 1960+ (preserved)
Use: Production ingestion, additive sessions
```

**State C: Growing (During 100 PDF batch)**
```
Nodes: 693 → 1500+ (growing)
Relationships: 1960 → 5000+ (growing)
Use: Knowledge graph expansion
```

---

## ✅ Validation

### How to Verify System is Ready

**After "prep e2e":**
```
Check output shows:
✅ Database: 0 nodes, 0 relationships
✅ ARIA Chunker: RecursiveCharacterTextSplitter ready
✅ DocumentQueue: Ready (empty, idle)
✅ Mode: E2E TESTING
```

**After "prep ingestion":**
```
Check output shows:
✅ Database: 693 nodes, 1960 relationships (preserved)
✅ ARIA Chunker: RecursiveCharacterTextSplitter ready
✅ DocumentQueue: Ready (empty, idle)
✅ Mode: PRODUCTION INGESTION (additive)
```

---

## 🚀 Production Ingestion Checklist

**Before starting 100 PDF batch:**

- [ ] Say: "prep ingestion"
- [ ] Verify: Database preserved (693+ nodes shown)
- [ ] Verify: ARIA Chunker ready (3000 tokens/chunk)
- [ ] Verify: DocumentQueue idle (0 queued)
- [ ] Open: `./scripts/monitor-queue.sh` in Terminal 1
- [ ] Open: `./scripts/monitor_ingestion.sh` in Terminal 2
- [ ] Upload: All 100 PDFs (queue will process sequentially)
- [ ] Wait: ~6.5 hours (queue finishes automatically)
- [ ] Verify: 100% success rate in queue monitor

---

## 📞 Quick Help

**Confused about which command to use?**

Ask yourself:
- Do I want to DELETE existing data? 
  - YES → "prep e2e"
  - NO → "prep ingestion"

- Am I testing or producing?
  - Testing → "prep e2e"
  - Producing → "prep ingestion"

- Is this for a clean test or adding data?
  - Clean test → "prep e2e"
  - Adding data → "prep ingestion"

---

**When in doubt:** "prep ingestion" (preserves data, safer!)

---

**Document Version:** 1.0  
**Date:** 2025-10-31  
**Architecture:** ARIA v2.0.0  
**Status:** Production-Ready ✅

