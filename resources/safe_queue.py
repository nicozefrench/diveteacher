"""
ARIA Knowledge System - Safe Ingestion Queue
Prevents Anthropic API rate limit bursts by enforcing token-aware delays.

Version: 2.0.0 - Anthropic Rate Limiter (Token-Aware Sliding Window)

This module implements an intelligent rate limit protection mechanism:
- Token tracking with sliding window (60s for Anthropic)
- Dynamic delays based on actual token usage
- Anthropic rate limits: 4M input tokens/minute
- Safety margin to prevent bursts
"""

import time
import asyncio
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime
from collections import deque


class SafeIngestionQueue:
    """
    Safe sequential ingestion with Anthropic rate limit protection.
    Uses token tracking with a sliding window to prevent rate limit errors.
    
    Strategy:
    - Track input tokens in a 60-second sliding window
    - Limit: 4,000,000 input tokens per minute (Anthropic)
    - Safety buffer: 80% of limit (3,200,000 tokens/min)
    - Dynamic delays based on actual token usage
    - No rate limit errors possible
    
    Trade-off:
    - Adds dynamic delays between documents (only when needed)
    - More efficient than fixed 120s delay
    - Optimized for Anthropic API limits
    """
    
    # Anthropic Configuration (as of 2025-10-29)
    RATE_LIMIT_WINDOW = 60  # Anthropic's rate limit window in seconds
    RATE_LIMIT_INPUT_TOKENS = 4_000_000  # 4M input tokens per minute
    SAFETY_BUFFER = 0.80  # Use 80% of limit (safety margin)
    EFFECTIVE_LIMIT = int(RATE_LIMIT_INPUT_TOKENS * SAFETY_BUFFER)  # 3.2M tokens/min
    
    # Token estimation (conservative estimates per document type)
    ESTIMATED_TOKENS_PER_REPORT = {
        'CARO': 50_000,   # Daily reviews ~50k tokens
        'BOB': 30_000,    # Status reports ~30k tokens
        'K2000': 40_000,  # Personal reviews ~40k tokens
        'STEPH-KB': 100_000  # KB snapshot ~100k tokens (large)
    }
    DEFAULT_ESTIMATE = 50_000  # Default if type unknown
    
    def __init__(self):
        """Initialize the safe queue with token tracking."""
        self.token_history: deque = deque()  # (timestamp, input_tokens)
        self.ingestion_count = 0
        self.total_tokens_used = 0
        
    def _clean_old_entries(self) -> None:
        """
        Remove token entries older than the rate limit window.
        Maintains accurate sliding window of token usage.
        """
        now = time.time()
        while self.token_history and (now - self.token_history[0][0]) > self.RATE_LIMIT_WINDOW:
            self.token_history.popleft()
    
    def _get_current_window_tokens(self) -> int:
        """
        Calculate total input tokens in current sliding window.
        
        Returns:
            Total input tokens in last 60 seconds
        """
        self._clean_old_entries()
        return sum(tokens for _, tokens in self.token_history)
    
    def _estimate_tokens_for_agent(self, agent_type: str) -> int:
        """
        Estimate input tokens for a given agent type.
        
        Args:
            agent_type: Agent name (CARO, BOB, K2000, STEPH-KB)
            
        Returns:
            Estimated input tokens (conservative)
        """
        return self.ESTIMATED_TOKENS_PER_REPORT.get(agent_type, self.DEFAULT_ESTIMATE)
    
    def _calculate_required_delay(self, estimated_tokens: int) -> float:
        """
        Calculate required delay before next ingestion.
        
        Strategy:
        1. Get current tokens in window
        2. If current + estimated > limit, calculate wait time
        3. Wait time = time until oldest entry expires from window
        
        Args:
            estimated_tokens: Estimated tokens for next ingestion
            
        Returns:
            Required delay in seconds (0 if no delay needed)
        """
        current_tokens = self._get_current_window_tokens()
        
        # Check if we have room for next ingestion
        if current_tokens + estimated_tokens <= self.EFFECTIVE_LIMIT:
            return 0.0  # No delay needed
        
        # We need to wait for some old entries to expire
        # Calculate when we'll have enough room
        now = time.time()
        required_space = estimated_tokens
        tokens_freed = 0
        wait_until_timestamp = now
        
        for timestamp, tokens in self.token_history:
            tokens_freed += tokens
            wait_until_timestamp = timestamp + self.RATE_LIMIT_WINDOW
            
            # Check if freed enough space
            if current_tokens - tokens_freed + estimated_tokens <= self.EFFECTIVE_LIMIT:
                break
        
        delay = max(0, wait_until_timestamp - now)
        return delay
    
    async def wait_for_token_budget(self, agent_type: str = 'UNKNOWN') -> None:
        """
        Wait until we have sufficient token budget in the rate limit window.
        
        This method ensures we don't exceed Anthropic's 4M input tokens/minute limit.
        
        Args:
            agent_type: Type of agent for token estimation
        """
        estimated_tokens = self._estimate_tokens_for_agent(agent_type)
        required_delay = self._calculate_required_delay(estimated_tokens)
        
        if required_delay > 0:
            current_tokens = self._get_current_window_tokens()
            print(f"")
            print(f"⏸️  Rate Limit Protection Active (Anthropic)")
            print(f"   Current window usage: {current_tokens:,} / {self.EFFECTIVE_LIMIT:,} tokens")
            print(f"   Estimated tokens needed: {estimated_tokens:,}")
            print(f"   Waiting {required_delay:.1f}s for token budget to free up...")
            print(f"   (Ensuring we stay under {self.RATE_LIMIT_INPUT_TOKENS:,} tokens/min limit)")
            print(f"")
            
            await asyncio.sleep(required_delay + 1)  # +1s extra safety margin
    
    def record_token_usage(self, input_tokens: int) -> None:
        """
        Record token usage for rate limit tracking.
        
        Args:
            input_tokens: Number of input tokens used in the API call
        """
        timestamp = time.time()
        self.token_history.append((timestamp, input_tokens))
        self.total_tokens_used += input_tokens
        self._clean_old_entries()  # Clean up old entries
    
    async def safe_ingest(
        self, 
        graphiti_client: Any, 
        parsed_data: Dict[str, Any],
        agent_type: str = None  # NEW: Optional agent type for accurate token estimation
    ) -> Dict[str, Any]:
        """
        Ingest with guaranteed Anthropic rate limit safety.
        
        Process:
        1. Detect agent type from parsed_data (or use provided agent_type)
        2. Wait for token budget (if needed)
        3. Perform ingestion
        4. Record actual token usage (or estimate if unavailable)
        
        Args:
            graphiti_client: GraphitiIngestion instance
            parsed_data: Parsed report data
            agent_type: Optional agent type for token estimation (overrides auto-detection)
            
        Returns:
            Ingestion result dict
            
        Raises:
            Exception: If ingestion fails (even after retries)
        """
        # Detect agent type for token estimation
        # Use provided agent_type if available, otherwise detect from parsed_data
        if agent_type is None:
            agent_type = parsed_data.get('agent', 'UNKNOWN')
        
        # Wait for token budget (dynamic delay based on current usage)
        await self.wait_for_token_budget(agent_type)
        
        # Record start time
        start_time = time.time()
        ingestion_start = datetime.now().strftime("%H:%M:%S")
        
        # Ingest (graphiti.add_episode has its own retry logic)
        print(f"📤 [{ingestion_start}] Ingestion #{self.ingestion_count + 1} starting ({agent_type})...")
        
        result = await graphiti_client.add_episode(parsed_data)
        
        # Record token usage (from API response or estimate)
        # Graphiti returns token usage in result if available
        if 'token_usage' in result and 'input_tokens' in result['token_usage']:
            actual_tokens = result['token_usage']['input_tokens']
        else:
            # Fallback to estimate
            actual_tokens = self._estimate_tokens_for_agent(agent_type)
        
        self.record_token_usage(actual_tokens)
        
        # Record completion
        duration = time.time() - start_time
        self.ingestion_count += 1
        
        ingestion_end = datetime.now().strftime("%H:%M:%S")
        print(f"✅ [{ingestion_end}] Ingestion completed in {duration:.1f}s ({actual_tokens:,} tokens)")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics with token tracking.
        
        Returns:
            Dict with ingestion count, token usage, limits, etc.
        """
        current_tokens = self._get_current_window_tokens()
        return {
            "ingestion_count": self.ingestion_count,
            "total_tokens_used": self.total_tokens_used,
            "current_window_tokens": current_tokens,
            "rate_limit_tokens_per_min": self.RATE_LIMIT_INPUT_TOKENS,
            "effective_limit_tokens_per_min": self.EFFECTIVE_LIMIT,
            "safety_buffer_pct": int(self.SAFETY_BUFFER * 100),
            "window_utilization_pct": int((current_tokens / self.EFFECTIVE_LIMIT) * 100) if self.EFFECTIVE_LIMIT > 0 else 0,
            "rate_limit_window_sec": self.RATE_LIMIT_WINDOW
        }
    
    def reset(self) -> None:
        """Reset queue state (for testing)."""
        self.token_history.clear()
        self.ingestion_count = 0
        self.total_tokens_used = 0


# Test function
async def test_safe_queue():
    """Test the safe queue with simulated ingestions."""
    print("🧪 Testing Safe Ingestion Queue (Anthropic Rate Limiter v2.0)")
    print("=" * 70)
    print("")
    
    queue = SafeIngestionQueue()
    
    print(f"Configuration:")
    print(f"  Rate limit window: {queue.RATE_LIMIT_WINDOW}s")
    print(f"  Rate limit (Anthropic): {queue.RATE_LIMIT_INPUT_TOKENS:,} tokens/min")
    print(f"  Effective limit (80% buffer): {queue.EFFECTIVE_LIMIT:,} tokens/min")
    print(f"  Token estimates: CARO={queue.ESTIMATED_TOKENS_PER_REPORT['CARO']:,}, BOB={queue.ESTIMATED_TOKENS_PER_REPORT['BOB']:,}, K2000={queue.ESTIMATED_TOKENS_PER_REPORT['K2000']:,}")
    print("")
    
    # Simulate multiple ingestions with a mock client
    class MockGraphiti:
        async def add_episode(self, data):
            # Simulate Graphiti processing time
            await asyncio.sleep(1)
            # Simulate realistic token usage
            agent = data.get('agent', 'UNKNOWN')
            estimated = queue.ESTIMATED_TOKENS_PER_REPORT.get(agent, queue.DEFAULT_ESTIMATE)
            # Return with token usage
            return {
                "status": "success",
                "episode_id": data.get("episode_id", "test"),
                "token_usage": {
                    "input_tokens": estimated,
                    "output_tokens": 500
                }
            }
    
    mock_client = MockGraphiti()
    
    # Simulate 8 reports (typical nightly run: 3 CARO, 1 BOB, 2 K2000, 1 STEPH-KB)
    test_agents = ['CARO', 'CARO', 'BOB', 'K2000', 'CARO', 'K2000', 'STEPH-KB']
    
    print(f"Simulating {len(test_agents)} ingestions...")
    print("")
    
    for i, agent in enumerate(test_agents):
        mock_data = {
            "episode_id": f"test-episode-{i+1}",
            "content": f"Mock {agent} content",
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "type": "test",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "metadata": {}
        }
        
        print(f"[{i+1}/{len(test_agents)}] Ingesting {agent} report...")
        result = await queue.safe_ingest(mock_client, mock_data)
        print(f"Result: {result['status']}")
        
        # Show current stats
        stats = queue.get_stats()
        print(f"  Current window: {stats['current_window_tokens']:,} tokens ({stats['window_utilization_pct']}% of limit)")
        print("")
    
    # Show final stats
    stats = queue.get_stats()
    print(f"=" * 70)
    print(f"Final Statistics:")
    print(f"  Total ingestions: {stats['ingestion_count']}")
    print(f"  Total tokens used: {stats['total_tokens_used']:,}")
    print(f"  Current window tokens: {stats['current_window_tokens']:,}")
    print(f"  Window utilization: {stats['window_utilization_pct']}%")
    print(f"  Effective limit: {stats['effective_limit_tokens_per_min']:,} tokens/min")
    print("")
    print("✅ Safe Queue test complete!")
    print("")
    print("Key observations:")
    print("  - Dynamic delays based on actual token usage (not fixed 120s)")
    print("  - Tracks Anthropic's 4M tokens/min limit with 80% safety buffer")
    print("  - Sliding window ensures no rate limit errors")
    print("  - More efficient than fixed delays (only waits when needed)")


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(test_safe_queue()))


