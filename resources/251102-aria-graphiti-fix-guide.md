# 🚀 ARIA GRAPHITI - IMPLEMENTATION GUIDE
## For AI Developer Agent (Claude Sonnet 4.5)

**Target:** Fix ingestion pipeline to reduce costs from $80/night → $18-19/night (77% reduction)  
**Approach:** 4 sequential corrections with validation checkpoints  
**Estimated Implementation Time:** 2-3 hours  
**Expected Result:** 1,260 API calls → 60 API calls (95% reduction)

---

## 📋 EXECUTION CHECKLIST

Execute in this exact order:

- [ ] **PRIORITY 1:** Remove chunking logic (12× impact)
- [ ] **PRIORITY 2:** Implement bulk ingestion (40-60% additional gain)
- [ ] **PRIORITY 3:** Configure LLM parameters (50% output reduction)
- [ ] **PRIORITY 4:** Remove fixed delays (15 min faster)
- [ ] **VALIDATION:** Run test ingestion, verify metrics

---

## ⚠️ CRITICAL CONTEXT

### Current Architecture Problem

**What's happening now:**
```
For each report (BOB 64KB, CARO 88KB):
├─ IF size > 10KB → chunk into 6-7 pieces
├─ FOR each chunk:
│  └─ await add_episode(chunk)  ← 3-5 LLM calls each
└─ Result: 14 episodes × ~90 calls = 1,260 API calls/night

Cost: $63/night for ingestion alone
```

**What should happen:**
```
For each report:
├─ NO chunking (full document)
├─ Batch all reports
└─ await add_episode_bulk([all_reports])  ← Single bulk call

Result: 3 episodes × ~20 calls = 60 API calls/night
Cost: $1-2/night for ingestion
```

**Root Cause (From Production Guide):**
> "For static documents (PDFs, technical docs): Create ONE episode per document. Best for: Static content, technical documentation" (Guide Line 244)

Our reports = semi-static content → **MUST use document-level, NO chunking**

---

# 🔴 PRIORITY 1: REMOVE CHUNKING LOGIC
## Impact: 12× reduction in API calls (1,260 → 100)

### Target File: `ingest_to_graphiti.py`

### Change 1A: Remove chunk_threshold from __init__

**Lines to modify:** 56-63

**BEFORE:**
```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=12000,        # 3000 tokens × 4 chars/token
    chunk_overlap=800,       # 200 tokens overlap
    separators=["\n\n", "\n", ". ", " ", ""]
)
self.chunk_threshold = 10000  # Chunk if > 10KB
```

**AFTER:**
```python
# REMOVED: text_splitter and chunk_threshold
# Best Practice (Production Guide Line 244): 
# "For static content: ONE episode per document"
# Our reports are semi-static → no chunking needed
```

**Rationale:**
- Production Guide explicitly states: static content = document-level
- Our nightly reports don't change after creation = static
- Chunking adds 12× overhead with zero benefit

---

### Change 1B: Simplify add_episode() method

**Lines to modify:** 219-225

**BEFORE:**
```python
async def add_episode(
    self,
    report_data: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """Add episode to Graphiti with retry logic"""
    await self.initialize()
    
    content = report_data.get('content', '')
    content_size = len(content)
    
    # Check if we need to chunk this report
    if content_size > self.chunk_threshold:
        logger.info(f"📦 Large report ({content_size:,} chars), using chunking strategy")
        return await self._add_episode_chunked(report_data, max_retries)
    else:
        logger.info(f"📄 Standard report ({content_size:,} chars), single episode")
        return await self._add_episode_single(report_data, max_retries)
```

**AFTER:**
```python
async def add_episode(
    self,
    report_data: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Add episode to Graphiti with retry logic.
    
    SIMPLIFIED: Always use document-level for our semi-static reports.
    Best Practice (Production Guide Line 244): "For static content: ONE episode per document"
    
    No chunking needed - our reports are technical documentation that doesn't 
    change after creation, making them ideal candidates for document-level ingestion.
    """
    await self.initialize()
    
    content = report_data.get('content', '')
    content_size = len(content)
    
    logger.info(f"📄 Report ({content_size:,} chars) - document-level ingestion")
    return await self._add_episode_single(report_data, max_retries)
```

**Impact:**
- BOB reports (64KB): 6 chunks → 1 document = 6× fewer episodes
- CARO reports (88KB): 7 chunks → 1 document = 7× fewer episodes
- K2000 reports (small): No change (already 1)
- **Total per night: 14 episodes → 3 episodes**

---

### Change 1C: Mark _add_episode_chunked as deprecated

**Lines to modify:** 227-367 (entire method)

**ACTION:** Add deprecation comment at the top of the method:

```python
async def _add_episode_chunked(
    self,
    report_data: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    DEPRECATED: This method is no longer used after Priority 1 implementation.
    
    Kept temporarily for rollback capability. Will be removed in next cleanup phase.
    
    Chunked ingestion violated Production Guide best practices for static content
    (Guide Line 244): "For static content: ONE episode per document"
    
    Original implementation created 6-7 episodes per large report, causing:
    - 12× more API calls than necessary
    - $58/night in wasted costs
    - Unnecessary fragmentation of report content
    """
    # ... (keep existing implementation for now)
```

**Rationale:** 
- Keep method temporarily for emergency rollback
- Document why it's deprecated
- Will remove in cleanup phase after validation

---

### Validation Checkpoint P1

After implementing Priority 1, verify:

```bash
# Run test ingestion on 1 report
python -m aria.scripts.test_single_report --agent CARO --date today

# Expected output:
✓ Report size: ~88,000 chars
✓ Episodes created: 1 (not 7!)
✓ API calls: ~15-20 (not ~100)
✓ Cost: ~$0.50 (not ~$6)
```

**If validation fails:**
- Revert changes
- Check that add_episode() is calling _add_episode_single
- Verify no chunking logic is executing

**If validation succeeds:**
- Document metrics in commit message
- Proceed to Priority 2

---

# 🔴 PRIORITY 2: IMPLEMENT BULK INGESTION
## Impact: Additional 40-60% reduction (100 → 60 API calls)

### Target File: `nightly_ingest.py`

### Change 2A: Refactor ingest_reports_since() to batch-first

**Lines to modify:** 80-158 (complete refactor)

**BEFORE:**
```python
async def ingest_reports_since(self, days: int = 1):
    """Ingest reports from the past N days."""
    since_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    total_ingested = 0
    failed_reports = []
    
    agents = ["CARO", "BOB", "K2000"]
    
    for agent in agents:
        print(f"\n{'='*60}")
        print(f"🤖 Processing {agent} Reports")
        print(f"{'='*60}")
        
        parser = self._get_parser(agent)
        reports = parser.list_reports(limit=10)
        
        for report_path in reports:
            try:
                # Extract date from filename
                report_date = parser.extract_date_from_path(report_path)
                
                if report_date < since_date:
                    continue
                
                # Parse report
                print(f"\n📄 Parsing: {report_path.name}")
                parsed = parser.parse_report(report_path)
                
                # Ingest via safe queue
                result = await self.safe_queue.safe_ingest(
                    self.graphiti,
                    parsed
                )
                
                if result.get('success'):
                    total_ingested += 1
                else:
                    failed_reports.append({
                        'path': str(report_path),
                        'error': result.get('error')
                    })
                
                # 5 minute delay between reports
                if report_path != reports[-1]:
                    await asyncio.sleep(300)
                    
            except Exception as e:
                logger.error(f"Failed to process {report_path}: {e}")
                failed_reports.append({
                    'path': str(report_path),
                    'error': str(e)
                })
    
    return {
        'total_ingested': total_ingested,
        'failed_reports': failed_reports
    }
```

**AFTER:**
```python
async def ingest_reports_since(self, days: int = 1):
    """
    Ingest reports from the past N days using bulk API.
    
    ARCHITECTURE CHANGE (Production Guide Lines 415-452):
    1. PREPARE: Parse all reports first into episodes list
    2. BATCH: Single add_episode_bulk() call with all episodes
    3. RESULT: 40-60% fewer LLM calls via shared schema context
    
    Old approach: Sequential per-report ingestion with 5min delays
    New approach: Batch preparation → bulk ingestion
    """
    since_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # STEP 1: PREPARE ALL EPISODES (no ingestion yet!)
    all_episodes = []
    failed_reports = []
    
    agents = ["CARO", "BOB", "K2000"]
    
    print(f"\n{'='*60}")
    print(f"📦 PHASE 1: Preparing Episodes (Batch)")
    print(f"{'='*60}\n")
    
    for agent in agents:
        print(f"🤖 Processing {agent} Reports...")
        
        parser = self._get_parser(agent)
        reports = parser.list_reports(limit=10)
        
        agent_count = 0
        for report_path in reports:
            try:
                # Extract date from filename
                report_date = parser.extract_date_from_path(report_path)
                
                # Filter by date
                if report_date < since_date:
                    continue
                
                # Parse report (local operation, no API calls)
                parsed = parser.parse_report(report_path)
                
                # Add to batch (NOT ingesting yet!)
                all_episodes.append({
                    "name": parsed["episode_id"],
                    "episode_body": parsed["content"],  # FULL DOCUMENT!
                    "source": EpisodeType.text,
                    "source_description": f"{parsed['agent']} {parsed['type']} report",
                    "reference_time": parsed["timestamp"]
                })
                
                agent_count += 1
                print(f"  ✓ Prepared: {report_path.name}")
                
            except Exception as e:
                logger.error(f"  ✗ Failed to parse {report_path}: {e}")
                failed_reports.append({
                    'path': str(report_path),
                    'error': str(e),
                    'phase': 'parsing'
                })
        
        print(f"  → {agent_count} reports prepared from {agent}\n")
    
    # STEP 2: BULK INGEST ALL EPISODES
    print(f"{'='*60}")
    print(f"📤 PHASE 2: Bulk Ingestion")
    print(f"{'='*60}\n")
    
    if not all_episodes:
        print("⚠️  No episodes to ingest")
        return {
            'total_ingested': 0,
            'failed_reports': failed_reports
        }
    
    print(f"📊 Total episodes prepared: {len(all_episodes)}")
    print(f"🚀 Initiating bulk ingestion...")
    
    try:
        # Initialize Graphiti
        await self.graphiti.initialize()
        
        # SINGLE BULK CALL - Production Guide Line 449: 
        # "single API call for entire batch"
        start_time = time.time()
        
        # Use the underlying graphiti client's bulk method
        await self.graphiti.graphiti.add_episode_bulk(all_episodes)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Bulk ingestion complete!")
        print(f"   ├─ Episodes: {len(all_episodes)}")
        print(f"   ├─ Time: {elapsed:.1f}s")
        print(f"   └─ Avg: {elapsed/len(all_episodes):.1f}s per episode")
        
        return {
            'total_ingested': len(all_episodes),
            'failed_reports': failed_reports,
            'elapsed_seconds': elapsed
        }
        
    except Exception as e:
        logger.error(f"❌ Bulk ingestion failed: {e}")
        
        # Log all episodes that failed
        for episode in all_episodes:
            failed_reports.append({
                'episode': episode['name'],
                'error': str(e),
                'phase': 'bulk_ingestion'
            })
        
        return {
            'total_ingested': 0,
            'failed_reports': failed_reports
        }
```

**Key Changes:**
1. **Two-phase approach:** Prepare → Ingest (not Parse+Ingest interleaved)
2. **Removed 5-min delays:** No longer needed with bulk API
3. **Single bulk call:** `add_episode_bulk(all_episodes)`
4. **Better error handling:** Distinguish parsing vs ingestion failures
5. **Performance tracking:** Measure bulk ingestion time

**Impact:**
- Production Guide Line 239: "40-60% reduction in LLM calls"
- Graphiti optimizes internally with shared schema context
- No per-report context resets
- No waiting between reports

---

### Change 2B: Update STEPH-KB ingestion to use same pattern

**Lines to modify:** 171-195

**BEFORE:**
```python
# 5 minute pause before STEPH-KB
await asyncio.sleep(300)

# Handle STEPH-KB separately
print(f"\n{'='*60}")
print(f"🧠 Processing STEPH-KB Snapshot")
print(f"{'='*60}\n")

snapshot = await self.kb_manager.get_current_snapshot()
if snapshot:
    result = await self.safe_queue.safe_ingest(
        self.graphiti,
        snapshot
    )
```

**AFTER:**
```python
# STEP 3: Handle STEPH-KB (if changed)
print(f"\n{'='*60}")
print(f"🧠 PHASE 3: STEPH-KB Snapshot")
print(f"{'='*60}\n")

snapshot = await self.kb_manager.get_current_snapshot()

if snapshot and snapshot.get('has_changes'):
    print(f"📸 New STEPH-KB snapshot detected")
    
    # Add to bulk batch (could be combined with Step 2 in future optimization)
    kb_episode = {
        "name": snapshot["episode_id"],
        "episode_body": snapshot["content"],
        "source": EpisodeType.json,
        "source_description": "STEPH-KB Knowledge Base snapshot",
        "reference_time": snapshot["timestamp"]
    }
    
    print(f"📤 Ingesting STEPH-KB snapshot...")
    
    try:
        # Bulk call with single episode (consistent with batch approach)
        await self.graphiti.graphiti.add_episode_bulk([kb_episode])
        print(f"✅ STEPH-KB snapshot ingested")
        
    except Exception as e:
        logger.error(f"❌ STEPH-KB ingestion failed: {e}")
        failed_reports.append({
            'episode': 'STEPH-KB',
            'error': str(e),
            'phase': 'kb_ingestion'
        })
        
elif snapshot:
    print(f"ℹ️  STEPH-KB unchanged (hash match)")
else:
    print(f"⚠️  No STEPH-KB snapshot available")
```

**Optimization Note:**
In future, STEPH-KB could be added to the main `all_episodes` list in Step 1 for true single-batch ingestion. Current approach maintains separation for clarity.

---

### Change 2C: Simplify SafeIngestionQueue usage

**File:** `common/safe_queue.py`  
**ACTION:** Add deprecation notice

The `SafeIngestionQueue.safe_ingest()` method is no longer needed after bulk ingestion. Add this comment:

```python
async def safe_ingest(self, graphiti_client, report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    DEPRECATED after bulk ingestion implementation (Priority 2).
    
    This method enforced per-document rate limiting, which is no longer needed
    because bulk ingestion handles all documents in a single optimized call.
    
    The sliding window limiter is still useful for other API calls, but for
    ingestion specifically, we now use add_episode_bulk() directly.
    
    Kept temporarily for rollback capability.
    """
    # ... (keep existing implementation)
```

---

### Validation Checkpoint P2

After implementing Priority 2, verify:

```bash
# Run full nightly ingestion (dry run)
python -m aria.scripts.test_nightly_ingest --dry-run

# Expected output:
✓ Phase 1: Prepared X episodes (parsing only, no API)
✓ Phase 2: Bulk ingestion complete
  ├─ Episodes: 3 (CARO + BOB + K2000)
  ├─ Time: ~30s (not 15+ minutes)
  └─ API calls: ~60 (not ~100)
✓ Phase 3: STEPH-KB (if changed)
  └─ API calls: ~20

Total cost: ~$2 (not ~$5)
```

**If validation fails:**
- Check that `add_episode_bulk()` is being called
- Verify all_episodes list is populated correctly
- Ensure no fallback to old sequential logic

**If validation succeeds:**
- Update CURRENT-CONTEXT.md with new architecture
- Proceed to Priority 3

---

# 🟠 PRIORITY 3: CONFIGURE LLM PARAMETERS
## Impact: 50% reduction in output tokens

### Target File: `ingest_to_graphiti.py`

### Change 3A: Add max_tokens and temperature to LLMConfig

**Lines to modify:** 77-81

**BEFORE:**
```python
llm_config = LLMConfig(
    api_key=anthropic_key,
    model='claude-haiku-4-5-20251001'
)
```

**AFTER:**
```python
llm_config = LLMConfig(
    api_key=anthropic_key,
    model='claude-haiku-4-5-20251001',
    max_tokens=2048,     # Production Guide Line 351: "Extraction doesn't need long outputs"
    temperature=0.0      # Production Guide Line 352: "Deterministic extraction"
)
```

**Rationale (Production Guide Lines 343-368):**

1. **max_tokens=2048 (not 4096)**
   - Entity extraction doesn't need long outputs
   - Default 4096 wastes tokens on verbose responses
   - 2048 is sufficient for structured extraction
   - Saves 50% on output tokens = ~$0.40/night

2. **temperature=0.0 (not default ~0.7)**
   - Makes extraction deterministic (same input → same output)
   - Reduces hallucination risk
   - Better for structured data extraction
   - No cost impact, but improves reliability

---

### Validation Checkpoint P3

After implementing Priority 3, verify:

```bash
# Check LLM config
python -m aria.scripts.inspect_config

# Expected output:
✓ LLM Model: claude-haiku-4-5-20251001
✓ Max Tokens: 2048 (was: 4096)
✓ Temperature: 0.0 (was: default)
```

**Monitor in next run:**
- Output tokens should be ~50% lower per episode
- Extraction quality should remain the same or improve
- Cost per episode should decrease by ~$0.15

---

# 🟡 PRIORITY 4: REMOVE FIXED DELAYS
## Impact: 15 minutes faster runtime

### Target File: `nightly_ingest.py`

### Change 4A: Remove inter-report delays (already done in P2)

**Status:** ✅ Already removed in Priority 2 refactor

The 5-minute delays between reports (lines 141-148) were removed when we implemented bulk ingestion. The new architecture processes all reports in a batch, eliminating the need for artificial delays.

### Change 4B: Update SEMAPHORE_LIMIT

**Target File:** `ingest_to_graphiti.py`  
**Lines to modify:** 91-99

**BEFORE:**
```python
# Force SEMAPHORE_LIMIT to 1 for safety during testing
os.environ['SEMAPHORE_LIMIT'] = '1'
```

**AFTER:**
```python
# Set SEMAPHORE_LIMIT based on production guide recommendations
# Production Guide Line 337-341:
# - Default: 10 (safe for most providers)
# - Anthropic Claude: 15-20 (higher rate limits)
# - Lower to 5-8 only if hitting 429 errors

# Start conservative after bulk migration, can increase later
os.environ.setdefault('SEMAPHORE_LIMIT', '8')

# Allow override via environment variable for testing
# Example: SEMAPHORE_LIMIT=15 python nightly_ingest.py
```

**Rationale:**
- SEMAPHORE_LIMIT=1 was overly conservative during development
- With bulk ingestion, we can safely increase to 8-10
- Anthropic supports higher concurrency than we're using
- Can tune upward to 15-20 if monitoring shows headroom

---

### Change 4C: Remove STEPH-KB pause (already done in P2)

**Status:** ✅ Already removed in Priority 2 refactor

The 5-minute pause before STEPH-KB (lines 171-178) was removed in Priority 2. STEPH-KB now processes immediately after report ingestion with no artificial delay.

---

### Validation Checkpoint P4

After implementing Priority 4, verify:

```bash
# Time a full nightly run
time python -m aria.scripts.nightly_ingest --days 1

# Expected output:
✓ Total runtime: ~2-3 minutes (was: 15-20 minutes)
✓ No artificial delays
✓ SEMAPHORE_LIMIT: 8 (not 1)
```

**Monitor:**
- Should complete in ~2-3 minutes (not 15-20)
- No 429 rate limit errors (if errors occur, lower SEMAPHORE_LIMIT)
- Smooth processing without pauses

---

# ✅ FINAL VALIDATION

After implementing ALL priorities, run full validation:

## Test Suite

```bash
# 1. Single report test
python -m aria.scripts.test_single_report --agent CARO

# Expected:
✓ 1 episode (not 7)
✓ ~15 API calls (not ~100)
✓ ~$0.40 cost (not ~$6)

# 2. Full nightly ingestion
python -m aria.scripts.nightly_ingest --days 1

# Expected:
✓ 3 episodes (CARO + BOB + K2000)
✓ ~60 API calls (not ~1,260)
✓ ~$1-2 cost (not ~$63)
✓ ~2-3 min runtime (not 15-20 min)

# 3. Cost monitoring
python -m aria.scripts.analyze_costs --days 1

# Expected:
✓ Ingestion: $1-2/night (was $63)
✓ Total: $18-19/night (was $80)
✓ Savings: 77% reduction
```

## Metrics to Track

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Episodes/night | 14 | 3 | ✅ 3 |
| API calls/night | 1,260 | 60 | ✅ 60 |
| Ingestion cost | $63 | $1-2 | ✅ $1-2 |
| Runtime | 15-20 min | 2-3 min | ✅ 2-3 min |
| Total cost/night | $80 | $18-19 | ✅ $18-19 |

## Success Criteria

All of the following must be true:

- [ ] No chunking logic executes (document-level only)
- [ ] Single `add_episode_bulk()` call per run
- [ ] LLMConfig has `max_tokens=2048, temperature=0.0`
- [ ] No artificial delays between reports
- [ ] SEMAPHORE_LIMIT ≥ 8
- [ ] Cost reduced by ≥75%
- [ ] Runtime reduced by ≥80%
- [ ] All reports successfully ingested
- [ ] No 429 rate limit errors

---

# 📚 REFERENCE ARCHITECTURE

## Before (Current - Inefficient)

```
nightly_ingest.py
  └─ for each agent (CARO, BOB, K2000):
      └─ for each report:
          ├─ parse_report()
          ├─ IF size > 10KB:
          │   └─ chunk into 6-7 pieces
          ├─ FOR each chunk/report:
          │   └─ await add_episode(chunk)  ← 3-5 LLM calls
          └─ await asyncio.sleep(300)      ← 5 min delay

Result: 14 episodes × ~90 calls = 1,260 API calls
Cost: $63/night
Runtime: 15-20 minutes
```

## After (Target - Optimized)

```
nightly_ingest.py
  ├─ PHASE 1: Prepare all episodes
  │   └─ for each agent:
  │       └─ for each report:
  │           └─ parse_report() → add to batch (NO API calls)
  │
  ├─ PHASE 2: Bulk ingest
  │   └─ await add_episode_bulk(all_episodes)  ← Single optimized call
  │
  └─ PHASE 3: STEPH-KB (if changed)
      └─ await add_episode_bulk([kb_snapshot])

Result: 3 episodes × ~20 calls = 60 API calls
Cost: $1-2/night
Runtime: 2-3 minutes
```

---

# 🚨 ROLLBACK PLAN

If any issues occur after deployment:

## Immediate Rollback (< 5 minutes)

```bash
# Revert to previous commit
git revert HEAD
git push

# OR restore backup files
cp backups/ingest_to_graphiti.py.bak aria/agents/ingest_to_graphiti.py
cp backups/nightly_ingest.py.bak aria/scripts/nightly_ingest.py

# Restart services
systemctl restart aria-nightly-ingest
```

## Partial Rollback Options

### Rollback Priority 1 only (restore chunking)
```python
# In add_episode(), restore:
if content_size > self.chunk_threshold:
    return await self._add_episode_chunked(...)
```

### Rollback Priority 2 only (restore sequential)
```python
# In ingest_reports_since(), restore:
for report in reports:
    await self.safe_queue.safe_ingest(self.graphiti, parsed)
    await asyncio.sleep(300)
```

### Rollback Priority 3 only (restore defaults)
```python
# In LLMConfig, remove:
llm_config = LLMConfig(
    api_key=anthropic_key,
    model='claude-haiku-4-5-20251001'
    # Remove max_tokens and temperature
)
```

---

# 📊 COST BREAKDOWN

## Current Costs (Before Implementation)

```
Nightly Ingestion:
├─ CARO: 7 episodes × ~90 calls = ~630 calls → $31.50
├─ BOB: 6 episodes × ~90 calls = ~540 calls → $27.00
├─ K2000: 1 episode × ~90 calls = ~90 calls → $4.50
└─ Total: 14 episodes, 1,260 calls → $63/night

Other Costs:
├─ Agents (CARO, BOB, K2000): ~$17/night
└─ Total System: ~$80/night

Annual: $29,200/year
```

## Target Costs (After Full Implementation)

```
Nightly Ingestion:
├─ ALL REPORTS: 3 episodes × ~20 calls = ~60 calls → $1-2/night
├─ (Bulk API provides 40-60% efficiency gain)
└─ (Document-level eliminates 12× chunking overhead)

Other Costs:
├─ Agents (CARO, BOB, K2000): ~$17/night
└─ Total System: ~$18-19/night

Annual: $6,570-6,935/year

SAVINGS: $22,265-22,630/year (77% reduction)
```

## Per-Priority Savings

| After This Priority | Ingestion Cost | Total Cost | Savings |
|---------------------|----------------|------------|---------|
| Current | $63/night | $80/night | baseline |
| Priority 1 (Document-level) | $5/night | $22/night | $58/night (72%) |
| Priority 2 (Bulk) | $3/night | $20/night | $60/night (75%) |
| Priority 3 (LLM config) | $2/night | $19/night | $61/night (76%) |
| **All Priorities** | **$1-2/night** | **$18-19/night** | **$61-62/night (77%)** |

---

# 🎯 IMPLEMENTATION TIMELINE

## Phase 1: Priority 1 (Day 1)
- [ ] Morning: Implement Change 1A, 1B, 1C
- [ ] Afternoon: Test single report
- [ ] Evening: Validate metrics
- **Go/No-Go Decision:** If validation passes, proceed to Phase 2

## Phase 2: Priority 2 (Day 2)
- [ ] Morning: Implement Change 2A, 2B, 2C
- [ ] Afternoon: Test full nightly run (dry-run)
- [ ] Evening: Validate bulk ingestion
- **Go/No-Go Decision:** If validation passes, proceed to Phase 3

## Phase 3: Priority 3 + 4 (Day 3)
- [ ] Morning: Implement Change 3A, 4B
- [ ] Afternoon: Final validation suite
- [ ] Evening: Production deployment
- **Go/No-Go Decision:** Monitor first real run

## Post-Implementation (Day 4+)
- [ ] Monitor costs daily for 1 week
- [ ] Remove deprecated methods after stability confirmed
- [ ] Update documentation
- [ ] Close tracking tickets

---

# 📝 COMMIT MESSAGES

Use these standardized commit messages:

```bash
# Priority 1
git commit -m "fix(ingestion): Remove chunking for document-level ingestion

- Remove text_splitter and chunk_threshold from __init__
- Simplify add_episode() to always use document-level
- Mark _add_episode_chunked as deprecated
- Reduces API calls from 1,260 to 100 per night (12x improvement)
- Aligns with Production Guide best practices (Line 244)

Expected impact: $58/night savings (72% reduction)

Refs: #ARIA-123"

# Priority 2
git commit -m "feat(ingestion): Implement bulk ingestion pipeline

- Refactor ingest_reports_since() to batch-first architecture
- Replace sequential ingestion with single add_episode_bulk() call
- Remove 5-minute delays between reports
- Update STEPH-KB to use bulk API
- Reduces API calls from 100 to 60 per night (40% improvement)
- Runtime reduced from 15-20min to 2-3min

Expected impact: Additional $2/night savings

Refs: #ARIA-123"

# Priority 3
git commit -m "config(llm): Optimize LLM parameters for extraction

- Set max_tokens=2048 (was 4096)
- Set temperature=0.0 for deterministic extraction
- Reduces output tokens by 50%
- Improves extraction consistency

Expected impact: $0.50/night savings

Refs: #ARIA-123"

# Priority 4
git commit -m "perf(ingestion): Increase SEMAPHORE_LIMIT for throughput

- Increase SEMAPHORE_LIMIT from 1 to 8
- Remove artificial delays (already done in Priority 2)
- Safe to increase after bulk ingestion implementation
- Can tune to 15-20 if monitoring shows headroom

Expected impact: Better throughput, no cost impact

Refs: #ARIA-123"
```

---

# 🔍 TROUBLESHOOTING

## Issue 1: Still seeing chunked episodes

**Symptoms:**
- Logs show "using chunking strategy"
- Episodes > 3 per night
- API calls > 100

**Diagnosis:**
```python
# Check if add_episode is still branching
grep -n "chunk_threshold" aria/agents/ingest_to_graphiti.py

# Should return NO results after Priority 1
```

**Fix:**
- Verify Change 1B was applied correctly
- Ensure no conditional logic remains for chunking
- Check for cached/old code being executed

## Issue 2: Bulk ingestion not called

**Symptoms:**
- Logs don't show "PHASE 2: Bulk Ingestion"
- Still seeing sequential "Adding episode" messages
- Runtime still 15-20 minutes

**Diagnosis:**
```python
# Check if refactor was applied
grep -n "add_episode_bulk" aria/scripts/nightly_ingest.py

# Should return results showing bulk call
```

**Fix:**
- Verify Change 2A was applied completely
- Check that code is calling graphiti.add_episode_bulk()
- Ensure not falling back to safe_queue.safe_ingest()

## Issue 3: 429 Rate Limit Errors

**Symptoms:**
- Errors mentioning "rate_limit_error"
- Status code 429 in logs
- Ingestion fails mid-batch

**Diagnosis:**
```bash
# Check current SEMAPHORE_LIMIT
echo $SEMAPHORE_LIMIT

# Check Anthropic dashboard for rate limit hits
```

**Fix:**
```python
# Lower SEMAPHORE_LIMIT temporarily
os.environ['SEMAPHORE_LIMIT'] = '5'

# Add retry logic if not present (already in code)
# Monitor and gradually increase if stable
```

## Issue 4: LLM Config Not Applied

**Symptoms:**
- Output tokens still high (~4000 per episode)
- Extraction seems non-deterministic

**Diagnosis:**
```python
# Verify config in logs at startup
grep "max_tokens" logs/aria-nightly.log

# Should show: max_tokens=2048
```

**Fix:**
- Verify Change 3A was applied
- Check LLMConfig initialization
- Restart service to ensure new config loaded

## Issue 5: Cost Not Reduced as Expected

**Symptoms:**
- Cost still high after implementation
- Metrics don't match targets

**Diagnosis:**
```bash
# Check actual API call counts
python -m aria.scripts.analyze_costs --days 1 --verbose

# Should show:
# - Episodes: 3 (not 14)
# - Calls: ~60 (not ~1,260)
# - Cost: ~$2 (not ~$63)
```

**Fix:**
- Verify ALL priorities were implemented
- Check for API calls from other sources (agents, etc)
- Review Anthropic usage dashboard for actual breakdown

---

# 📞 SUPPORT

## Before Making Changes

1. ✅ Backup current code
2. ✅ Document current metrics (baseline)
3. ✅ Ensure dev environment has test credits
4. ✅ Review Production Guide (reference document)

## During Implementation

1. 📊 Track metrics after each priority
2. 🧪 Test each change before proceeding
3. 💾 Commit after each successful validation
4. 📝 Document any deviations from plan

## After Deployment

1. 📈 Monitor costs daily for 1 week
2. 🚨 Set up alerts for cost spikes
3. 📋 Update CURRENT-CONTEXT.md with results
4. 🎉 Celebrate when targets achieved!

## Emergency Contacts

If critical issues arise:
- Immediate rollback using commands above
- Check logs: `tail -f logs/aria-nightly.log`
- Review Anthropic dashboard for API errors
- Reference Production Guide sections for specific issues

---

# ✅ FINAL CHECKLIST

Before marking implementation complete:

## Code Changes
- [ ] Priority 1: Chunking removed
- [ ] Priority 2: Bulk ingestion implemented
- [ ] Priority 3: LLM config optimized
- [ ] Priority 4: Delays removed, SEMAPHORE_LIMIT increased

## Validation
- [ ] Single report test passes
- [ ] Full nightly test passes
- [ ] Cost reduced by ≥75%
- [ ] Runtime reduced by ≥80%
- [ ] No rate limit errors

## Documentation
- [ ] CURRENT-CONTEXT.md updated
- [ ] Commit messages standardized
- [ ] Rollback plan documented
- [ ] Team notified of changes

## Monitoring
- [ ] Cost alerts configured
- [ ] Metrics dashboard updated
- [ ] Daily monitoring scheduled
- [ ] Weekly review planned

---

**Implementation Guide Version:** 1.0  
**Created:** 2025-11-01  
**Based on:** Codex Audit + Claude Audit + Production Guide  
**Target Agent:** Claude Sonnet 4.5 (AI Developer)

**READY FOR IMPLEMENTATION** ✅

