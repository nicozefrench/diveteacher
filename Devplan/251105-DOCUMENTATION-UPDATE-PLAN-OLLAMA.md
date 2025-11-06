# DOCUMENTATION UPDATE PLAN - Ollama Baremetal Migration

**Date:** November 5, 2025 09:20 CET  
**Context:** Update all documentation for Ollama baremetal migration  
**Found:** 58 obsolete references to Docker Ollama  
**Status:** 🔴 **CRITICAL - DOCUMENTATION OUTDATED**

---

## 📋 OBSOLETE REFERENCES FOUND

### Critical Files (Must Update)

| File | Obsolete Refs | Priority | Impact |
|------|---------------|----------|--------|
| `ARCHITECTURE.md` | 1 major section | 🔴 **CRITICAL** | Core architecture doc |
| `SETUP.md` | 12 references | 🔴 **CRITICAL** | Setup instructions wrong |
| `MONITORING.md` | 10 references | 🔴 **CRITICAL** | Monitoring instructions wrong |
| `DEPLOYMENT.md` | 5 references | 🟡 **MEDIUM** | Production setup (still Docker) |
| `INDEX.md` | 1 reference | 🟡 **MEDIUM** | Overview |

### Historical/Audit Files (OK to Keep)

| File | Obsolete Refs | Action | Reason |
|------|---------------|--------|--------|
| `FIXES-LOG.md` | 15 references | ✅ **KEEP** | Historical record (Fix #1) |
| `TESTING-LOG.md` | 3 references | ✅ **KEEP** | Historical test results |
| `GEMINI-AUDIT-REPORT.md` | 1 reference | ✅ **KEEP** | Historical audit |
| `DOCUMENTATION-UPDATE-PLAN.md` | 2 references | ✅ **KEEP** | Historical planning |
| `GRAPHITI.md.old` | 1 reference | ✅ **KEEP** | Archived file |

---

## 🎯 UPDATE STRATEGY

### Phase 1: Critical Architecture (ARCHITECTURE.md)

**Section to Update:**
- Lines 1213-1242: "Docker Configuration" section
- Currently shows Ollama in Docker
- **Must replace with:** Hybrid architecture (Native Ollama + Docker services)

**New Content:**
```markdown
### Development Environment (Mac M1 Max)

**Hybrid Architecture:**
- **Ollama:** Native baremetal (Metal GPU) - NOT in Docker
- **Backend/Frontend/Neo4j:** Docker containers
- **Connection:** Backend → `http://host.docker.internal:11434`

**Why Native Ollama?**
- Docker Desktop on macOS cannot access Metal GPU
- Native Ollama provides 30-60× performance gain
- See: `Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md`

**Docker Compose (docker/docker-compose.dev.yml):**
```yaml
# NOTE: Ollama runs NATIVELY on Mac host (Metal GPU)
# Backend connects via host.docker.internal:11434

backend:
  environment:
    - OLLAMA_BASE_URL=http://host.docker.internal:11434
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

**Daily Workflow:**
```bash
# Terminal 1: Start native Ollama (keep open)
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS="*"
ollama serve

# Terminal 2: Start Docker services
docker compose -f docker/docker-compose.dev.yml up -d
```

### Production Environment (DigitalOcean GPU)

**Standard Docker Architecture:**
- **All services in Docker:** Ollama, Backend, Frontend, Neo4j
- **Ollama:** Docker with NVIDIA GPU runtime
- **Connection:** Backend → `http://ollama:11434`
```

---

### Phase 2: Setup Instructions (SETUP.md)

**Sections to Update:**

1. **Line 142-169:** "Start Services" section
   - Remove `rag-ollama` from `docker stop` command
   - Add native Ollama startup instructions
   - Update container list expectations

2. **Line 188-205:** "Pull Model" section
   - Change from `docker exec rag-ollama ollama pull`
   - To: `ollama pull` (native command)

3. **Line 260:** "Test LLM" section
   - Change from `docker exec rag-ollama ollama run`
   - To: `ollama run` or test via backend API

4. **Line 835:** "Stop Services" section
   - Remove `rag-ollama` from stop command
   - Add instructions to stop native Ollama

5. **Line 867-873:** "Update Model" section
   - Update all `docker exec rag-ollama` commands
   - Use native `ollama` commands

6. **Line 944-976:** "Service: rag-ollama" section
   - **Remove entire section** or
   - **Replace with** "Native Ollama Setup" section

**New Section to Add:**

```markdown
### Native Ollama Setup (Mac M1 Max Development)

#### Prerequisites
```bash
# Install Ollama (if not already)
brew install ollama

# Pull model
ollama pull qwen2.5:7b-instruct-q8_0
```

#### Starting Ollama
```bash
# Terminal 1: Start Ollama (keep this terminal open)
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS="*"
ollama serve

# Verify it's running (Terminal 2)
curl http://localhost:11434/api/version
ollama ps
```

#### Expected Output
```bash
# Ollama API
{"version":"0.12.6"}

# Running models (after first query)
NAME                        ID              SIZE      PROCESSOR    UNTIL
qwen2.5:7b-instruct-q8_0    2d9500c94841    8.9 GB    100% GPU     4 min
```

#### Troubleshooting
- If GPU not active: Make sure Ollama runs NATIVELY (not in Docker)
- If connection fails: Check `OLLAMA_HOST=0.0.0.0:11434`
- If model not found: Run `ollama pull qwen2.5:7b-instruct-q8_0`
```

---

### Phase 3: Monitoring Instructions (MONITORING.md)

**Sections to Update:**

1. **Line 33:** "monitor_ollama.sh" description
   - Change: "Performance Ollama + Docker"
   - To: "Performance Ollama (Native Metal GPU)"

2. **Line 44:** Overview
   - Change: "Performance monitoring pour Ollama et Docker"
   - To: "Performance monitoring pour Ollama natif (Metal GPU)"

3. **Line 203-266:** "monitor_ollama.sh" detailed section
   - **Replace entire section** with updated instructions
   - Reflect native process monitoring (not Docker)

4. **Line 591-679:** "Quick Checks" section
   - Update all `docker logs rag-ollama` commands
   - Update all `docker exec rag-ollama` commands
   - Use native Ollama commands

**New Content:**

```markdown
### Native Ollama Monitoring

#### Quick Health Check
```bash
# Check Ollama process
pgrep -x ollama
ps aux | grep ollama | grep -v grep

# Check API
curl http://localhost:11434/api/version

# Check GPU status
ollama ps
# Expected: 100% GPU (Metal)
```

#### Performance Monitor
```bash
# Run comprehensive monitoring
./scripts/monitor_ollama.sh

# Output:
# ✅ Ollama process running (PID: XXXXX)
# ✅ Model loaded: qwen2.5:7b-instruct-q8_0 (8.9 GB)
# ✅ GPU: 100% Metal GPU
# ✅ Backend connectivity: OK
```

#### Log Monitoring
```bash
# Native Ollama logs
tail -f /tmp/ollama-serve.log

# Backend logs (Ollama API calls)
docker logs -f rag-backend | grep ollama
```
```

---

### Phase 4: Index & Overview (INDEX.md)

**Line 199:** Update table entry

**Current:**
```markdown
| **Ollama Docker Config** | ✅ Optimized | [Docker Compose](../docker/docker-compose.dev.yml) |
```

**New:**
```markdown
| **Ollama Setup** | ✅ **Dev:** Native (Metal GPU)<br>**Prod:** Docker (NVIDIA) | [Migration Guide](../Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md) |
```

---

### Phase 5: Deployment (DEPLOYMENT.md)

**Action:** Add clarification note at top

**New Section (after line 38):**

```markdown
### ⚠️ IMPORTANT: Development vs Production

**Development (Mac M1 Max):**
- Ollama runs **NATIVELY** on Mac host (Metal GPU)
- See: `Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md`
- Backend connects via `http://host.docker.internal:11434`

**Production (DigitalOcean GPU):**
- Ollama runs in **DOCKER** with NVIDIA GPU runtime
- All services containerized as described below
- Backend connects via `http://ollama:11434`

**This document describes PRODUCTION setup only.**
```

**Keep existing content** as it correctly describes production Docker deployment.

---

## 📊 UPDATE CHECKLIST

### Critical Updates (Must Do)

- [ ] **ARCHITECTURE.md** (lines 1213-1242)
  - [ ] Replace "Docker Configuration" section
  - [ ] Add "Hybrid Architecture" section
  - [ ] Add "Development vs Production" clarification
  - [ ] Add daily workflow instructions
  - [ ] Update performance metrics

- [ ] **SETUP.md** (12 locations)
  - [ ] Update "Start Services" (line 142-169)
  - [ ] Update "Pull Model" (line 188-205)
  - [ ] Update "Test LLM" (line 260)
  - [ ] Update "Stop Services" (line 835)
  - [ ] Update "Update Model" (line 867-873)
  - [ ] Replace "Service: rag-ollama" section (line 944-976)
  - [ ] Add "Native Ollama Setup" section

- [ ] **MONITORING.md** (10 locations)
  - [ ] Update tool description (line 33)
  - [ ] Update overview (line 44)
  - [ ] Replace monitor_ollama.sh section (line 203-266)
  - [ ] Update Quick Checks (line 591-679)
  - [ ] Add native monitoring instructions

- [ ] **INDEX.md** (1 location)
  - [ ] Update Ollama table entry (line 199)

### Medium Priority Updates

- [ ] **DEPLOYMENT.md** (5 locations)
  - [ ] Add Dev vs Prod clarification note
  - [ ] Keep existing production content

### No Updates Needed (Historical)

- [x] **FIXES-LOG.md** - Historical record ✅
- [x] **TESTING-LOG.md** - Historical tests ✅
- [x] **GEMINI-AUDIT-REPORT.md** - Historical audit ✅
- [x] **DOCUMENTATION-UPDATE-PLAN.md** - Historical ✅
- [x] **GRAPHITI.md.old** - Archived ✅

---

## 🎯 EXECUTION PLAN

### Step 1: ARCHITECTURE.md (30 min)
- Most critical document
- Core architecture understanding
- Impacts all other docs

### Step 2: SETUP.md (45 min)
- Most user-facing document
- Critical for new developers
- Multiple sections to update

### Step 3: MONITORING.md (30 min)
- Operational documentation
- Used daily by developers
- Multiple command updates

### Step 4: INDEX.md + DEPLOYMENT.md (15 min)
- Quick reference updates
- Clarification notes

### Step 5: Validation (15 min)
- Grep for remaining "rag-ollama"
- Test all commands
- Verify consistency

**Total Estimated Time:** 2h 15min

---

## ✅ SUCCESS CRITERIA

1. **Zero obsolete references** in critical docs
2. **Clear Dev vs Prod distinction** everywhere
3. **All commands work** as documented
4. **Consistent terminology** across all docs
5. **Migration guide referenced** where appropriate

---

## 📚 REFERENCE DOCUMENTS

- ✅ `Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md` - Complete migration guide
- ✅ `Devplan/251105-MONITORING-TOOLS-AUDIT.md` - Tools compatibility
- ✅ `docker/docker-compose.dev.yml` - Current hybrid config
- ✅ `.env` - Current environment variables

---

**Plan Created:** November 5, 2025 09:25 CET  
**Estimated Duration:** 2h 15min  
**Priority:** 🔴 **CRITICAL**  
**Blocker:** Gap #2 Days 5-7 (need correct docs)

---

## 🚀 NEXT STEPS

1. Execute Phase 1-5 updates
2. Validate all changes
3. Commit to Git
4. Update CURRENT-CONTEXT.md
5. Resume Gap #2 implementation

