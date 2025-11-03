# 🔒 SafeIngestionQueue - Bulk Ingestion Adaptation Guide
## For AI Developer Agent (Claude Sonnet 4.5)

**Context:** Post-implementation of ARIA GRAPHITI - IMPLEMENTATION GUIDE  
**Target:** Adapt existing SafeIngestionQueue to handle bulk ingestion with intelligent rate limiting  
**Tier:** Anthropic Tier 4 (4M tokens/min, ~400 req/min)  
**Goal:** Eliminate manual 5-minute delays while respecting rate limits

---

## 📋 PREREQUISITES

Before starting this implementation, verify that these are complete:

- [x] Priority 1: Document-level ingestion implemented (no chunking)
- [x] Priority 2: Bulk ingestion pipeline implemented (`add_episode_bulk`)
- [x] Priority 3: LLM config optimized (max_tokens=2048, temperature=0.0)
- [x] Priority 4: Fixed delays removed, SEMAPHORE_LIMIT configured

**Current State:** 
- Bulk ingestion works but may hit rate limits
- SafeIngestionQueue exists but only handles single-document ingestion
- Need intelligent rate limiting for bulk operations

---

## 🎯 OBJECTIVE

Transform SafeIngestionQueue from:
```python
# Current: Per-document ingestion
await safe_queue.safe_ingest(graphiti, single_report)
```

To:
```python
# Target: Bulk ingestion with rate limiting
await safe_queue.safe_ingest_bulk(graphiti, all_episodes)
```

**Benefits:**
- ✅ Intelligent token-based rate limiting
- ✅ Automatic sub-batching when needed
- ✅ No manual delays (adaptive pacing)
- ✅ Respects Tier 4 limits (4M tokens/min)
- ✅ Maintains existing sliding window logic

---

## 📊 RATE LIMIT ANALYSIS

### Your Anthropic Tier 4 Limits

```
Tokens Per Minute (TPM): 4,000,000
Requests Per Minute (RPM): ~400

For bulk ingestion:
- 3 reports/night = 3 episodes
- Each episode: ~5,000-10,000 tokens input + ~2,000 output = ~12,000 tokens
- Total per bulk call: ~36,000 tokens (0.9% of limit)

CONCLUSION: Single bulk call is SAFE for nightly ingestion
```

### Why We Still Need Rate Limiting

1. **Burst Protection:** Multiple bulk calls in succession (manual runs, tests)
2. **Safety Margin:** Don't use 100% of limit (leave headroom)
3. **Sub-batching:** Large imports (>50 episodes) need splitting
4. **Graceful Degradation:** Handle rate limit errors automatically

---

## 🔧 IMPLEMENTATION

### File: `aria/common/safe_queue.py`

### Change 1: Add Bulk Ingestion Method

**Location:** After the existing `safe_ingest()` method (~line 227)

**ADD THIS NEW METHOD:**

```python
async def safe_ingest_bulk(
    self,
    graphiti_client,
    episodes: List[Dict[str, Any]],
    max_tokens_per_min: int = 3_200_000,  # 80% of Tier 4 limit (safety margin)
    max_episodes_per_batch: int = 20,      # Max episodes per sub-batch
    delay_between_batches: float = 10.0    # Seconds between sub-batches
) -> Dict[str, Any]:
    """
    Safely ingest multiple episodes using bulk API with rate limiting.
    
    This method adapts the existing sliding window rate limiter to handle
    bulk ingestion by:
    1. Estimating token usage for the bulk batch
    2. Splitting into sub-batches if needed to respect rate limits
    3. Using existing _wait_for_capacity() logic
    4. Automatic retry with exponential backoff on rate limit errors
    
    Args:
        graphiti_client: GraphitiIngestionClient instance
        episodes: List of episode dicts to ingest
        max_tokens_per_min: Target TPM (default: 3.2M = 80% of 4M Tier 4 limit)
        max_episodes_per_batch: Max episodes per sub-batch
        delay_between_batches: Seconds to wait between sub-batches
    
    Returns:
        Dict with results:
        {
            'total_success': int,
            'total_failed': int,
            'sub_batches': int,
            'total_tokens_estimated': int,
            'elapsed_seconds': float,
            'results': List[Dict]
        }
    
    Example:
        >>> episodes = [
        ...     {"name": "report1", "episode_body": "...", ...},
        ...     {"name": "report2", "episode_body": "...", ...},
        ... ]
        >>> result = await queue.safe_ingest_bulk(graphiti, episodes)
        >>> print(f"Ingested {result['total_success']} episodes")
    """
    import time
    import math
    
    start_time = time.time()
    
    if not episodes:
        logger.warning("⚠️  safe_ingest_bulk called with empty episodes list")
        return {
            'total_success': 0,
            'total_failed': 0,
            'sub_batches': 0,
            'total_tokens_estimated': 0,
            'elapsed_seconds': 0.0,
            'results': []
        }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🔒 SafeIngestionQueue: Bulk Ingestion")
    logger.info(f"{'='*60}")
    logger.info(f"📊 Total episodes: {len(episodes)}")
    logger.info(f"🎯 Rate limit: {max_tokens_per_min:,} tokens/min")
    logger.info(f"📦 Max per batch: {max_episodes_per_batch}")
    
    # STEP 1: Estimate tokens per episode (conservative)
    def estimate_tokens(episode: Dict[str, Any]) -> int:
        """
        Estimate token count for an episode.
        
        Formula:
        - Input tokens: len(episode_body) / 4 (chars to tokens ratio)
        - Output tokens: 2048 (max_tokens from LLM config)
        - Safety margin: 1.2× multiplier
        """
        content = episode.get('episode_body', '')
        input_tokens = len(content) // 4
        output_tokens = 2048  # From Priority 3 LLM config
        total = int((input_tokens + output_tokens) * 1.2)  # 20% safety margin
        return total
    
    total_estimated_tokens = sum(estimate_tokens(ep) for ep in episodes)
    avg_tokens_per_episode = total_estimated_tokens // len(episodes)
    
    logger.info(f"💭 Estimated tokens:")
    logger.info(f"   ├─ Total: {total_estimated_tokens:,}")
    logger.info(f"   ├─ Avg per episode: {avg_tokens_per_episode:,}")
    logger.info(f"   └─ % of rate limit: {(total_estimated_tokens / max_tokens_per_min) * 100:.1f}%")
    
    # STEP 2: Determine sub-batching strategy
    # Calculate how many episodes we can safely process per batch
    tokens_per_batch_safe = max_tokens_per_min // 4  # Use 25% of limit per batch
    episodes_per_batch = min(
        max_episodes_per_batch,
        max(1, tokens_per_batch_safe // avg_tokens_per_episode)
    )
    
    num_sub_batches = math.ceil(len(episodes) / episodes_per_batch)
    
    logger.info(f"\n📋 Batching strategy:")
    logger.info(f"   ├─ Episodes per sub-batch: {episodes_per_batch}")
    logger.info(f"   ├─ Total sub-batches: {num_sub_batches}")
    logger.info(f"   └─ Delay between batches: {delay_between_batches}s")
    
    # STEP 3: Process sub-batches
    results = []
    total_success = 0
    total_failed = 0
    
    for batch_idx in range(num_sub_batches):
        start_idx = batch_idx * episodes_per_batch
        end_idx = min(start_idx + episodes_per_batch, len(episodes))
        sub_batch = episodes[start_idx:end_idx]
        
        batch_tokens = sum(estimate_tokens(ep) for ep in sub_batch)
        
        logger.info(f"\n📤 Sub-batch {batch_idx + 1}/{num_sub_batches}:")
        logger.info(f"   ├─ Episodes: {len(sub_batch)}")
        logger.info(f"   └─ Estimated tokens: {batch_tokens:,}")
        
        # STEP 3A: Wait for rate limit capacity using existing logic
        logger.debug(f"⏳ Checking rate limit capacity...")
        await self._wait_for_capacity(batch_tokens)
        
        # STEP 3B: Execute bulk ingestion with retry logic
        retry_count = 0
        max_retries = 3
        retry_delay = 5  # Start with 5 seconds
        
        while retry_count <= max_retries:
            try:
                logger.info(f"   🚀 Executing bulk ingestion...")
                
                # Call Graphiti's bulk API
                result = await graphiti_client.graphiti.add_episode_bulk(sub_batch)
                
                # Record token usage in sliding window
                self._record_usage(batch_tokens)
                
                logger.info(f"   ✅ Success!")
                
                results.append({
                    'batch_index': batch_idx,
                    'success': True,
                    'count': len(sub_batch),
                    'tokens_estimated': batch_tokens,
                    'result': result
                })
                
                total_success += len(sub_batch)
                break  # Success, exit retry loop
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                is_rate_limit = any(keyword in error_str for keyword in [
                    'rate_limit',
                    '429',
                    'too many requests',
                    'quota exceeded'
                ])
                
                if is_rate_limit and retry_count < max_retries:
                    retry_count += 1
                    logger.warning(f"   ⚠️  Rate limit hit (attempt {retry_count}/{max_retries})")
                    logger.warning(f"   ⏸️  Backing off for {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    # Not a rate limit error, or max retries exceeded
                    logger.error(f"   ❌ Sub-batch failed: {e}")
                    
                    results.append({
                        'batch_index': batch_idx,
                        'success': False,
                        'count': len(sub_batch),
                        'tokens_estimated': batch_tokens,
                        'error': str(e),
                        'retry_count': retry_count
                    })
                    
                    total_failed += len(sub_batch)
                    break  # Give up on this sub-batch
        
        # STEP 3C: Delay before next sub-batch (except for last one)
        if batch_idx < num_sub_batches - 1:
            logger.debug(f"   ⏳ Waiting {delay_between_batches}s before next sub-batch...")
            await asyncio.sleep(delay_between_batches)
    
    # STEP 4: Summary
    elapsed = time.time() - start_time
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Bulk Ingestion Summary")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Success: {total_success}/{len(episodes)} episodes")
    logger.info(f"❌ Failed: {total_failed}/{len(episodes)} episodes")
    logger.info(f"📦 Sub-batches: {num_sub_batches}")
    logger.info(f"⏱️  Total time: {elapsed:.1f}s")
    logger.info(f"⚡ Avg per episode: {elapsed/len(episodes):.1f}s")
    logger.info(f"{'='*60}\n")
    
    return {
        'total_success': total_success,
        'total_failed': total_failed,
        'sub_batches': num_sub_batches,
        'total_tokens_estimated': total_estimated_tokens,
        'elapsed_seconds': elapsed,
        'results': results
    }
```

---

### Change 2: Update nightly_ingest.py to Use New Method

**File:** `aria/scripts/nightly_ingest.py`  
**Location:** Inside `ingest_reports_since()` method, after preparing `all_episodes`

**BEFORE:**
```python
# STEP 2: BULK INGEST ALL EPISODES
print(f"{'='*60}")
print(f"📤 PHASE 2: Bulk Ingestion")
print(f"{'='*60}\n")

if not all_episodes:
    print("⚠️  No episodes to ingest")
    return {...}

print(f"📊 Total episodes prepared: {len(all_episodes)}")
print(f"🚀 Initiating bulk ingestion...")

try:
    await self.graphiti.initialize()
    
    start_time = time.time()
    
    # Direct bulk call (no rate limiting)
    await self.graphiti.graphiti.add_episode_bulk(all_episodes)
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Bulk ingestion complete!")
    print(f"   ├─ Episodes: {len(all_episodes)}")
    print(f"   ├─ Time: {elapsed:.1f}s")
    
    return {
        'total_ingested': len(all_episodes),
        'failed_reports': failed_reports,
        'elapsed_seconds': elapsed
    }
    
except Exception as e:
    logger.error(f"❌ Bulk ingestion failed: {e}")
    # ... error handling
```

**AFTER:**
```python
# STEP 2: BULK INGEST ALL EPISODES (with rate limiting)
print(f"{'='*60}")
print(f"📤 PHASE 2: Bulk Ingestion (Rate-Limited)")
print(f"{'='*60}\n")

if not all_episodes:
    print("⚠️  No episodes to ingest")
    return {
        'total_ingested': 0,
        'failed_reports': failed_reports
    }

print(f"📊 Total episodes prepared: {len(all_episodes)}")
print(f"🚀 Initiating safe bulk ingestion...\n")

try:
    await self.graphiti.initialize()
    
    # Use SafeIngestionQueue for rate-limited bulk ingestion
    result = await self.safe_queue.safe_ingest_bulk(
        graphiti_client=self.graphiti,
        episodes=all_episodes,
        max_tokens_per_min=3_200_000,  # 80% of Tier 4 limit (4M)
        max_episodes_per_batch=20,      # Conservative batch size
        delay_between_batches=10.0      # 10s between batches (if multiple)
    )
    
    # Update failed reports with any bulk ingestion failures
    if result['total_failed'] > 0:
        for batch_result in result['results']:
            if not batch_result['success']:
                failed_reports.append({
                    'batch': batch_result['batch_index'],
                    'error': batch_result.get('error', 'Unknown error'),
                    'phase': 'bulk_ingestion'
                })
    
    print(f"\n✅ Safe bulk ingestion complete!")
    print(f"   ├─ Success: {result['total_success']}/{len(all_episodes)}")
    print(f"   ├─ Failed: {result['total_failed']}/{len(all_episodes)}")
    print(f"   ├─ Sub-batches: {result['sub_batches']}")
    print(f"   ├─ Time: {result['elapsed_seconds']:.1f}s")
    print(f"   └─ Rate limit safe: ✅")
    
    return {
        'total_ingested': result['total_success'],
        'failed_reports': failed_reports,
        'elapsed_seconds': result['elapsed_seconds'],
        'sub_batches': result['sub_batches']
    }
    
except Exception as e:
    logger.error(f"❌ Safe bulk ingestion failed: {e}")
    
    # Log all episodes that failed
    for episode in all_episodes:
        failed_reports.append({
            'episode': episode['name'],
            'error': str(e),
            'phase': 'bulk_ingestion_wrapper'
        })
    
    return {
        'total_ingested': 0,
        'failed_reports': failed_reports
    }
```

---

### Change 3: Update STEPH-KB Ingestion

**File:** `aria/scripts/nightly_ingest.py`  
**Location:** STEPH-KB section (Phase 3)

**BEFORE:**
```python
# STEP 3: Handle STEPH-KB (if changed)
kb_episode = {...}

try:
    # Direct bulk call with single episode
    await self.graphiti.graphiti.add_episode_bulk([kb_episode])
    print(f"✅ STEPH-KB snapshot ingested")
    
except Exception as e:
    logger.error(f"❌ STEPH-KB ingestion failed: {e}")
    failed_reports.append({...})
```

**AFTER:**
```python
# STEP 3: Handle STEPH-KB (if changed) - with rate limiting
kb_episode = {
    "name": snapshot["episode_id"],
    "episode_body": snapshot["content"],
    "source": EpisodeType.json,
    "source_description": "STEPH-KB Knowledge Base snapshot",
    "reference_time": snapshot["timestamp"]
}

print(f"📤 Ingesting STEPH-KB snapshot (rate-limited)...")

try:
    # Use safe bulk ingestion for consistency
    kb_result = await self.safe_queue.safe_ingest_bulk(
        graphiti_client=self.graphiti,
        episodes=[kb_episode],
        max_tokens_per_min=3_200_000,
        max_episodes_per_batch=1,  # Single episode
        delay_between_batches=0    # No delay needed for single episode
    )
    
    if kb_result['total_success'] == 1:
        print(f"✅ STEPH-KB snapshot ingested (rate-limit safe)")
    else:
        raise Exception(kb_result['results'][0].get('error', 'Unknown error'))
    
except Exception as e:
    logger.error(f"❌ STEPH-KB ingestion failed: {e}")
    failed_reports.append({
        'episode': 'STEPH-KB',
        'error': str(e),
        'phase': 'kb_ingestion'
    })
```

---

## ✅ VALIDATION

### Test 1: Single Episode (Baseline)

```python
# Test with 1 episode to verify basic functionality
import asyncio
from aria.scripts.nightly_ingest import NightlyIngestion

async def test_single_episode():
    ingestor = NightlyIngestion()
    
    # Single test episode
    test_episode = {
        "name": "test_episode_001",
        "episode_body": "This is a test episode." * 100,
        "source": EpisodeType.text,
        "source_description": "Test episode",
        "reference_time": datetime.now(timezone.utc)
    }
    
    result = await ingestor.safe_queue.safe_ingest_bulk(
        graphiti_client=ingestor.graphiti,
        episodes=[test_episode]
    )
    
    print(f"\n✅ Single episode test:")
    print(f"   Success: {result['total_success']}/1")
    print(f"   Sub-batches: {result['sub_batches']}")
    print(f"   Time: {result['elapsed_seconds']:.1f}s")
    
    assert result['total_success'] == 1, "Single episode should succeed"
    assert result['sub_batches'] == 1, "Should use 1 sub-batch"

asyncio.run(test_single_episode())
```

**Expected Output:**
```
🔒 SafeIngestionQueue: Bulk Ingestion
📊 Total episodes: 1
💭 Estimated tokens: ~2,500
📋 Batching strategy:
   ├─ Episodes per sub-batch: 20
   ├─ Total sub-batches: 1
📤 Sub-batch 1/1:
   ✅ Success!
✅ Single episode test:
   Success: 1/1
   Sub-batches: 1
   Time: 2.3s
```

---

### Test 2: Multiple Episodes (Nightly Scenario)

```python
async def test_nightly_scenario():
    ingestor = NightlyIngestion()
    
    # Simulate 3 reports (CARO + BOB + K2000)
    test_episodes = [
        {
            "name": "CARO_20251102_001",
            "episode_body": "CARO report content..." * 500,  # ~88KB
            "source": EpisodeType.text,
            "source_description": "CARO nightly report",
            "reference_time": datetime.now(timezone.utc)
        },
        {
            "name": "BOB_20251102_001",
            "episode_body": "BOB report content..." * 400,   # ~64KB
            "source": EpisodeType.text,
            "source_description": "BOB nightly report",
            "reference_time": datetime.now(timezone.utc)
        },
        {
            "name": "K2000_20251102_001",
            "episode_body": "K2000 report content..." * 100, # ~16KB
            "source": EpisodeType.text,
            "source_description": "K2000 nightly report",
            "reference_time": datetime.now(timezone.utc)
        }
    ]
    
    result = await ingestor.safe_queue.safe_ingest_bulk(
        graphiti_client=ingestor.graphiti,
        episodes=test_episodes
    )
    
    print(f"\n✅ Nightly scenario test:")
    print(f"   Success: {result['total_success']}/3")
    print(f"   Failed: {result['total_failed']}/3")
    print(f"   Sub-batches: {result['sub_batches']}")
    print(f"   Tokens: {result['total_tokens_estimated']:,}")
    print(f"   Time: {result['elapsed_seconds']:.1f}s")
    
    assert result['total_success'] == 3, "All 3 episodes should succeed"
    assert result['sub_batches'] == 1, "Should fit in 1 sub-batch"
    assert result['elapsed_seconds'] < 30, "Should complete in <30s"

asyncio.run(test_nightly_scenario())
```

**Expected Output:**
```
🔒 SafeIngestionQueue: Bulk Ingestion
📊 Total episodes: 3
💭 Estimated tokens: ~36,000 (0.9% of limit)
📋 Batching strategy:
   ├─ Episodes per sub-batch: 20
   ├─ Total sub-batches: 1
📤 Sub-batch 1/1:
   ├─ Episodes: 3
   └─ Estimated tokens: 36,000
   ✅ Success!
✅ Nightly scenario test:
   Success: 3/3
   Failed: 0/3
   Sub-batches: 1
   Tokens: 36,000
   Time: 8.4s
```

---

### Test 3: Large Batch (Sub-batching)

```python
async def test_large_batch():
    ingestor = NightlyIngestion()
    
    # Simulate 50 episodes (stress test)
    test_episodes = [
        {
            "name": f"test_episode_{i:03d}",
            "episode_body": f"Test content {i}..." * 200,
            "source": EpisodeType.text,
            "source_description": f"Test episode {i}",
            "reference_time": datetime.now(timezone.utc)
        }
        for i in range(50)
    ]
    
    result = await ingestor.safe_queue.safe_ingest_bulk(
        graphiti_client=ingestor.graphiti,
        episodes=test_episodes,
        max_episodes_per_batch=10  # Force sub-batching
    )
    
    print(f"\n✅ Large batch test:")
    print(f"   Success: {result['total_success']}/50")
    print(f"   Failed: {result['total_failed']}/50")
    print(f"   Sub-batches: {result['sub_batches']}")
    print(f"   Time: {result['elapsed_seconds']:.1f}s")
    
    assert result['total_success'] == 50, "All 50 should succeed"
    assert result['sub_batches'] == 5, "Should use 5 sub-batches (50/10)"
    assert result['elapsed_seconds'] < 120, "Should complete in <2 minutes"

asyncio.run(test_large_batch())
```

**Expected Output:**
```
🔒 SafeIngestionQueue: Bulk Ingestion
📊 Total episodes: 50
📋 Batching strategy:
   ├─ Episodes per sub-batch: 10
   ├─ Total sub-batches: 5
📤 Sub-batch 1/5: ✅
   ⏳ Waiting 10s...
📤 Sub-batch 2/5: ✅
   ⏳ Waiting 10s...
📤 Sub-batch 3/5: ✅
   ⏳ Waiting 10s...
📤 Sub-batch 4/5: ✅
   ⏳ Waiting 10s...
📤 Sub-batch 5/5: ✅
✅ Large batch test:
   Success: 50/50
   Failed: 0/50
   Sub-batches: 5
   Time: 98.2s
```

---

### Test 4: Rate Limit Simulation

```python
async def test_rate_limit_handling():
    """
    Test how system handles rate limit errors.
    
    Note: This test simulates rate limit by using very aggressive settings.
    In production, Tier 4 limits are high enough that nightly runs won't hit them.
    """
    ingestor = NightlyIngestion()
    
    # Create 30 episodes
    test_episodes = [...]  # Similar to Test 3
    
    # Use aggressive settings to potentially trigger rate limit
    result = await ingestor.safe_queue.safe_ingest_bulk(
        graphiti_client=ingestor.graphiti,
        episodes=test_episodes,
        max_tokens_per_min=500_000,     # Artificially low limit
        max_episodes_per_batch=5,       # Small batches
        delay_between_batches=1.0       # Short delay
    )
    
    print(f"\n✅ Rate limit handling test:")
    print(f"   Success: {result['total_success']}/30")
    print(f"   Failed: {result['total_failed']}/30")
    
    # With retry logic, should eventually succeed
    assert result['total_success'] >= 25, "Most should succeed with retry"

# asyncio.run(test_rate_limit_handling())  # Run manually if needed
```

---

## 📊 MONITORING

### Metrics to Track

After implementation, monitor these metrics:

```python
# Add to nightly_ingest.py after bulk ingestion

def log_metrics_to_file(result: Dict[str, Any], output_dir: Path):
    """Log bulk ingestion metrics for monitoring."""
    metrics = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_episodes': result['total_success'] + result['total_failed'],
        'success': result['total_success'],
        'failed': result['total_failed'],
        'sub_batches': result['sub_batches'],
        'tokens_estimated': result['total_tokens_estimated'],
        'elapsed_seconds': result['elapsed_seconds'],
        'rate_limit_errors': sum(
            1 for r in result['results'] 
            if not r['success'] and 'rate_limit' in r.get('error', '').lower()
        )
    }
    
    metrics_file = output_dir / 'bulk_ingestion_metrics.jsonl'
    with open(metrics_file, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

# Usage in ingest_reports_since()
log_metrics_to_file(result, output_dir=Path('logs'))
```

### Dashboard Query

```python
# Analyze metrics over time
import pandas as pd

def analyze_metrics(days: int = 7):
    """Analyze bulk ingestion performance over last N days."""
    metrics_file = Path('logs/bulk_ingestion_metrics.jsonl')
    
    if not metrics_file.exists():
        print("No metrics file found")
        return
    
    # Load metrics
    metrics = []
    with open(metrics_file) as f:
        for line in f:
            metrics.append(json.loads(line))
    
    df = pd.DataFrame(metrics)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter last N days
    cutoff = datetime.now() - timedelta(days=days)
    df = df[df['timestamp'] >= cutoff]
    
    print(f"\n📊 Bulk Ingestion Metrics (Last {days} Days)")
    print(f"{'='*60}")
    print(f"Total runs: {len(df)}")
    print(f"Avg episodes/run: {df['total_episodes'].mean():.1f}")
    print(f"Avg success rate: {(df['success'].sum() / df['total_episodes'].sum() * 100):.1f}%")
    print(f"Avg time/run: {df['elapsed_seconds'].mean():.1f}s")
    print(f"Avg tokens/run: {df['tokens_estimated'].mean():,.0f}")
    print(f"Rate limit errors: {df['rate_limit_errors'].sum()}")
    print(f"{'='*60}\n")

# Run analysis
analyze_metrics(days=7)
```

---

## 🚨 TROUBLESHOOTING

### Issue 1: Still Hitting Rate Limits

**Symptoms:**
- Logs show "Rate limit hit" messages
- Multiple retries before success
- Failed sub-batches

**Diagnosis:**
```bash
# Check metrics
grep "rate_limit" logs/bulk_ingestion_metrics.jsonl

# Count occurrences
grep -c "Rate limit hit" logs/aria-nightly.log
```

**Fix:**
```python
# In nightly_ingest.py, reduce concurrency:
result = await self.safe_queue.safe_ingest_bulk(
    graphiti_client=self.graphiti,
    episodes=all_episodes,
    max_tokens_per_min=2_400_000,   # Lower to 60% of limit
    max_episodes_per_batch=10,       # Smaller batches
    delay_between_batches=15.0       # Longer delays
)

# Also lower SEMAPHORE_LIMIT
os.environ['SEMAPHORE_LIMIT'] = '5'
```

---

### Issue 2: Sub-batching Not Working

**Symptoms:**
- Single large batch attempted
- Rate limit errors on first batch
- No sub-batch logs

**Diagnosis:**
```python
# Check token estimation
episodes = [...]
for ep in episodes:
    tokens = len(ep['episode_body']) // 4 + 2048
    print(f"{ep['name']}: {tokens:,} tokens")
```

**Fix:**
- Verify `max_episodes_per_batch` is being respected
- Check token estimation formula
- Lower `max_episodes_per_batch` manually

---

### Issue 3: Slower Than Expected

**Symptoms:**
- Runtime > 60s for 3 episodes
- Long delays between batches
- Excessive waiting

**Diagnosis:**
```bash
# Check timing logs
grep "Waiting" logs/aria-nightly.log | tail -20

# Should not show delays for single batch (3 episodes)
```

**Fix:**
```python
# If only 1 sub-batch, no delays should occur
# Check that delay_between_batches logic skips last batch

# Also verify SEMAPHORE_LIMIT isn't too low
os.environ['SEMAPHORE_LIMIT'] = '10'  # Increase if safe
```

---

### Issue 4: Token Estimation Inaccurate

**Symptoms:**
- Actual token usage much higher/lower than estimate
- Unexpected rate limit hits or overly conservative

**Diagnosis:**
```python
# Compare estimates vs actual (check Anthropic dashboard)
result = await safe_queue.safe_ingest_bulk(...)
print(f"Estimated: {result['total_tokens_estimated']:,}")

# Check Anthropic dashboard for actual usage
```

**Fix:**
```python
# Adjust estimation formula in safe_ingest_bulk()
def estimate_tokens(episode: Dict[str, Any]) -> int:
    content = episode.get('episode_body', '')
    input_tokens = len(content) // 3.5  # Adjust divisor (was 4)
    output_tokens = 2048
    total = int((input_tokens + output_tokens) * 1.3)  # Adjust margin (was 1.2)
    return total
```

---

## 🎯 SUCCESS CRITERIA

Mark implementation complete when ALL of these are true:

- [ ] `safe_ingest_bulk()` method added to SafeIngestionQueue
- [ ] `nightly_ingest.py` updated to use new method
- [ ] STEPH-KB ingestion updated
- [ ] All 4 validation tests pass
- [ ] No rate limit errors in test runs
- [ ] Metrics logging implemented
- [ ] Dashboard analysis shows expected performance
- [ ] Production run completes successfully

**Expected Metrics:**
```
✅ 3 episodes/night ingested in single sub-batch
✅ No rate limit errors
✅ Runtime: 8-15 seconds (vs 2-3 minutes before delays)
✅ Tokens: ~36,000 (0.9% of 4M limit)
✅ 100% success rate
```

---

## 📝 ROLLBACK PLAN

If issues occur:

### Quick Rollback (< 2 minutes)

```python
# In nightly_ingest.py, revert to direct bulk call:

# Replace:
result = await self.safe_queue.safe_ingest_bulk(...)

# With:
await self.graphiti.graphiti.add_episode_bulk(all_episodes)
```

### Full Rollback

```bash
# Revert git commits
git revert HEAD  # Revert SafeIngestionQueue changes
git push

# OR restore from backup
cp backups/safe_queue.py.bak aria/common/safe_queue.py
cp backups/nightly_ingest.py.bak aria/scripts/nightly_ingest.py
```

---

## 🎓 IMPLEMENTATION NOTES

### Design Decisions

1. **Why 80% of rate limit?**
   - Leaves 20% headroom for concurrent processes
   - Protects against estimation errors
   - Allows manual API calls during nightly run

2. **Why sub-batching?**
   - Future-proofs for larger imports
   - Handles edge cases (many manual runs)
   - Provides checkpoint recovery points

3. **Why keep delays between sub-batches?**
   - Prevents burst overload on Anthropic's side
   - Gives sliding window time to clear
   - Minimal impact (only if >20 episodes)

4. **Why reuse existing sliding window?**
   - Proven logic from single-document ingestion
   - Consistent rate limiting across all operations
   - Less code duplication

### Future Optimizations

After stable for 1 week, consider:

1. **Increase batch size:** 20 → 30 episodes/batch
2. **Reduce delays:** 10s → 5s between batches
3. **Increase rate limit:** 80% → 90% of Tier 4 limit
4. **Dynamic tuning:** Auto-adjust based on historical metrics

---

## 📚 REFERENCES

- **Anthropic Rate Limits:** https://docs.anthropic.com/en/api/rate-limits
- **Production Guide:** ARIA GRAPHITI - IMPLEMENTATION GUIDE
- **Original Audit:** 251101-CODEX-LINE-BY-LINE-AUDIT
- **SafeIngestionQueue:** aria/common/safe_queue.py (existing)

---

**Implementation Guide Version:** 1.0  
**Created:** 2025-11-02  
**Context:** Post-ARIA-GRAPHITI-IMPLEMENTATION-GUIDE  
**Target:** Anthropic Tier 4 (4M TPM)  
**Status:** READY FOR IMPLEMENTATION ✅

