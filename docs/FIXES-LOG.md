# 🔧 Fixes Log - DiveTeacher RAG System

> **Purpose:** Track all bugs fixed, problems resolved, and system improvements  
> **Last Updated:** October 29, 2025, 08:25 CET  
> **Status:** Active - Updated after each fix

---

## 📋 Table of Contents

- [Active Fixes](#active-fixes)
- [Resolved Fixes](#resolved-fixes)
- [Pending Issues](#pending-issues)
- [Fix Statistics](#fix-statistics)

---

## Active Fixes

### 🔴 CRITICAL - Graphiti Search Returns 0 Results

**Status:** 🔴 OPEN - BLOCKING  
**Opened:** October 29, 2025, 08:00 CET  
**Priority:** P0 - CRITICAL  
**Impact:** RAG query unusable

**Problem:**
- Graphiti search returns 0 facts despite 221 nodes in Neo4j
- Error: `TypeError: Graphiti.search() got an unexpected keyword argument 'search_config'`
- RAG system cannot retrieve context for queries

**Investigation:**
- Removed `search_config` parameter from `graphiti.py` line 269
- Cleared Python cache (`__pycache__`)
- Restarted backend multiple times
- Issue persists after all attempts

**Root Cause:**
- Graphiti v0.17.0 API compatibility issue
- The `search()` method signature changed
- Need to check Graphiti documentation for correct parameters

**Next Steps:**
1. Review Graphiti v0.17.0 documentation
2. Test `client.search()` with minimal parameters
3. Verify Neo4j indices are built correctly
4. Consider downgrading Graphiti if API is broken

**Files Affected:**
- `backend/app/integrations/graphiti.py` (line 265-269)
- `backend/app/api/query.py` (RAG endpoint)

---

## Resolved Fixes

### ✅ FIX #1: Ollama Healthcheck Always Unhealthy

**Status:** ✅ RESOLVED  
**Opened:** October 28, 2025, 19:00 CET  
**Resolved:** October 29, 2025, 08:25 CET  
**Duration:** ~13 hours (spanned 2 sessions)  
**Priority:** P1 - HIGH  
**Category:** Infrastructure / Docker

#### Problem Description

**Symptom:**
```bash
docker ps
NAMES        STATUS
rag-ollama   Up X minutes (unhealthy)
```

**Impact:**
- Docker shows Ollama as "unhealthy" constantly
- Creates confusion about system state
- Makes monitoring difficult
- Not a blocker (Ollama works fine) but bad practice

**Root Cause:**
```bash
OCI runtime exec failed: exec: "curl": executable file not found in $PATH: unknown
```

The healthcheck in `docker-compose.dev.yml` was configured to use `curl`:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
```

But `curl` is **NOT installed** in the base `ollama/ollama:latest` image (minimal Debian image).

#### Investigation Steps

1. **Verified Ollama service works:**
   - API responds: `{"version":"0.12.6"}` ✅
   - Model loaded: `qwen2.5:7b-instruct-q8_0` ✅
   - Port accessible: `localhost:11434` ✅

2. **Tested healthcheck command:**
   ```bash
   docker exec rag-ollama curl -f http://localhost:11434/api/version
   # Error: curl: executable file not found
   ```

3. **Confirmed root cause:**
   - Base image is minimal (no curl, no wget)
   - Healthcheck can't execute, fails immediately
   - Docker marks container as "unhealthy"

#### Solution Implemented

**Approach:** Create custom Ollama image with `curl` installed

**Files Created:**
1. `docker/ollama/Dockerfile` - Custom Dockerfile extending `ollama/ollama:latest`
2. Updated `docker/docker-compose.dev.yml` to use custom image

**Implementation Details:**

**File: `docker/ollama/Dockerfile`**
```dockerfile
FROM ollama/ollama:latest

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify curl installation
RUN curl --version

LABEL maintainer="DiveTeacher"
LABEL description="Ollama with curl for healthcheck support"
LABEL version="1.0"
```

**File: `docker/docker-compose.dev.yml` (modified)**
```yaml
ollama:
  build:
    context: ./ollama
    dockerfile: Dockerfile
  image: diveteacher-ollama:latest  # Custom image
  container_name: rag-ollama
  # ... (rest unchanged)
  healthcheck:
    # FIXED: Using custom image with curl installed
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
    interval: 10s
    timeout: 5s
    retries: 10
    start_period: 60s
```

#### Validation

**Build Process:**
```bash
docker compose -f docker/docker-compose.dev.yml build ollama
# ✅ Built successfully in 7.2s
# ✅ curl 8.5.0 installed
# ✅ Image: diveteacher-ollama:latest
```

**Test Results:**
```bash
# Before fix:
docker ps | grep ollama
# rag-ollama   Up X minutes (unhealthy)

# After fix:
docker ps | grep ollama
# rag-ollama   Up 24 seconds (healthy)  ✅
```

**Healthcheck Verification:**
```bash
docker exec rag-ollama curl -f http://localhost:11434/api/version
# {"version":"0.12.6"}  ✅
```

#### Why This Solution is Robust

✅ **Production-Ready:**
- Proper Docker image extending base
- Clean apt-get installation
- Minimal additional size (~2MB for curl + deps)

✅ **Future-Proof:**
- Works with any Ollama version (extends :latest)
- Healthcheck uses standard curl command
- Easy to maintain and update

✅ **Best Practice:**
- Proper healthcheck monitoring
- No workarounds or hacks
- Follows Docker conventions

✅ **No Technical Debt:**
- Clean solution, not a patch
- Self-documenting (Dockerfile explains why)
- Reusable pattern for other services

#### Lessons Learned

1. **Always verify dependencies** in base images
2. **Test healthchecks** manually before deploying
3. **Don't accept "it works but shows unhealthy"** - fix properly
4. **Document the "why"** in Dockerfiles and configs
5. **Build for quality**, not quick fixes

#### Related Issues

- None (standalone fix)

#### Files Modified

- `docker/ollama/Dockerfile` - **CREATED**
- `docker/docker-compose.dev.yml` - Modified ollama service config
- `docs/FIXES-LOG.md` - This file (documentation)
- `docs/TESTING-LOG.md` - Updated with fix results

---

## Pending Issues

### 🟡 Status Endpoint Returns 404

**Status:** 🟡 OPEN - MEDIUM  
**Opened:** October 29, 2025, 08:00 CET  
**Priority:** P2 - MEDIUM  
**Impact:** Cannot track upload progress via API

**Problem:**
- `/api/upload/{upload_id}/status` returns 404 Not Found
- `processing_status` dict not accessible from endpoint
- UI cannot show real-time progress

**Workaround:**
- Monitor via Docker logs
- Use `monitor_ingestion.sh` script

**Next Steps:**
1. Check `processing_status` dict scope (module-level?)
2. Verify FastAPI route registration
3. Add proper status storage (Redis or database)

---

### 🟡 Docling Progress Bars Spam Logs

**Status:** 🟡 OPEN - LOW  
**Opened:** October 29, 2025, 08:00 CET  
**Priority:** P3 - LOW  
**Impact:** Makes log monitoring difficult

**Problem:**
- Docling outputs progress bars to logs
- Creates 180KB+ of log spam for 2-page PDF
- Hard to filter useful information

**Workaround:**
- Use `grep` to filter logs
- Use `monitor_ingestion.sh` which filters automatically

**Next Steps:**
1. Find Docling config to disable progress bars
2. Redirect progress output to /dev/null
3. Or keep for dev, disable for production

---

### 🟡 Backend Neo4j Health Error

**Status:** 🟡 OPEN - LOW  
**Opened:** October 29, 2025, 08:00 CET  
**Priority:** P3 - LOW (non-blocking)  
**Impact:** Healthcheck shows "degraded" but works fine

**Problem:**
```json
{
  "status": "degraded",
  "services": {
    "neo4j": "error: object bool can't be used in 'await' expression"
  }
}
```

**Analysis:**
- Neo4j connection works fine (verified with direct queries)
- Issue is in the healthcheck code itself
- Probably using `await` on a boolean instead of coroutine

**Next Steps:**
1. Fix healthcheck in `backend/app/api/health.py`
2. Make healthcheck async-safe
3. Test with proper Neo4j client calls

---

## Fix Statistics

### By Priority

| Priority | Open | Resolved | Total |
|----------|------|----------|-------|
| P0 (Critical) | 1 | 0 | 1 |
| P1 (High) | 0 | 1 | 1 |
| P2 (Medium) | 1 | 0 | 1 |
| P3 (Low) | 2 | 0 | 2 |
| **TOTAL** | **4** | **1** | **5** |

### By Category

| Category | Open | Resolved |
|----------|------|----------|
| Infrastructure | 0 | 1 |
| Backend API | 2 | 0 |
| Graphiti/Neo4j | 1 | 0 |
| Logging | 1 | 0 |

### Resolution Time

| Fix | Duration | Status |
|-----|----------|--------|
| Ollama Healthcheck | 13 hours | ✅ Resolved |
| Graphiti Search | Ongoing | 🔴 Open |

---

## Fix Process

### When to Create a Fix Entry

Create a fix entry when:
- ✅ A bug is reproducible and documented
- ✅ Impact is understood
- ✅ Investigation has begun
- ✅ Priority is assigned

### Fix Status Lifecycle

```
🔴 OPEN → 🟡 IN PROGRESS → ✅ RESOLVED → 🔒 CLOSED
```

- **🔴 OPEN:** Issue identified, not yet worked on
- **🟡 IN PROGRESS:** Actively being investigated/fixed
- **✅ RESOLVED:** Fix implemented and validated
- **🔒 CLOSED:** Deployed to production and monitored

### Required Information

For each fix:
- [ ] Clear problem description
- [ ] Impact assessment
- [ ] Root cause analysis
- [ ] Investigation steps
- [ ] Solution implemented
- [ ] Validation results
- [ ] Files modified
- [ ] Lessons learned

---

## Références

- **[TESTING-LOG.md](TESTING-LOG.md)** - Test execution history
- **[MONITORING.md](MONITORING.md)** - Monitoring scripts and tools
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

---

**🎯 Purpose:** Track every fix with full context so we never repeat the same mistakes  
**📅 Last Updated:** October 29, 2025, 08:25 CET  
**👤 Maintained By:** Claude Sonnet 4.5 AI Agent

