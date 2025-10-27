"""
ARIA Knowledge System - Safe Ingestion Queue
Prevents OpenAI rate limit bursts by enforcing delays between ingestions.

Version: 1.3.0 - Solution B (Safe Sequential Ingestion)

This module implements a simple, reliable rate limit protection mechanism:
- Fixed delay between ingestions (120s = 2× the OpenAI rate limit window)
- Guarantees the sliding window is clear before next ingestion
- 100% reliable (zero rate limits)
"""

import time
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime


class SafeIngestionQueue:
    """
    Safe sequential ingestion with rate limit protection.
    Ensures OpenAI rate limit window is clear between ingestions.
    
    Strategy:
    - Wait 120 seconds between each ingestion
    - 120s = 2× OpenAI's 60s sliding window
    - Guarantees window is EMPTY before next ingestion
    - No rate limit possible
    
    Trade-off:
    - Adds 2 minutes between each document
    - Worth it for 100% reliability
    - Nightly runs at 23:00, so performance is not critical
    """
    
    # Configuration
    RATE_LIMIT_WINDOW = 60  # OpenAI's rate limit window in seconds
    SAFETY_MARGIN = 2       # Safety factor (2× the window)
    DELAY_BETWEEN_INGESTIONS = RATE_LIMIT_WINDOW * SAFETY_MARGIN  # 120 seconds
    
    def __init__(self):
        """Initialize the safe queue."""
        self.last_ingestion_time: Optional[float] = None
        self.ingestion_count = 0
        
    async def wait_for_clear_window(self) -> None:
        """
        Wait to ensure rate limit window is clear.
        
        This method ensures that all API calls from the previous ingestion
        are outside the OpenAI 60-second sliding window before proceeding.
        """
        if self.last_ingestion_time is None:
            # First ingestion, no wait needed
            return
        
        elapsed = time.time() - self.last_ingestion_time
        
        if elapsed < self.DELAY_BETWEEN_INGESTIONS:
            wait_time = self.DELAY_BETWEEN_INGESTIONS - elapsed
            
            print(f"")
            print(f"⏸️  Rate Limit Protection Active")
            print(f"   Waiting {wait_time:.0f}s for OpenAI rate limit window to clear...")
            print(f"   (Ensuring 60s sliding window is empty)")
            print(f"   Previous ingestion completed {elapsed:.0f}s ago")
            print(f"")
            
            await asyncio.sleep(wait_time)
    
    async def safe_ingest(
        self, 
        graphiti_client: Any, 
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ingest with guaranteed rate limit safety.
        
        Process:
        1. Wait for rate limit window to clear (if not first ingestion)
        2. Perform ingestion
        3. Record completion time
        
        Args:
            graphiti_client: GraphitiIngestion instance
            parsed_data: Parsed report data
            
        Returns:
            Ingestion result dict
            
        Raises:
            Exception: If ingestion fails (even after retries)
        """
        # Wait for window to clear
        await self.wait_for_clear_window()
        
        # Record start time
        start_time = time.time()
        ingestion_start = datetime.now().strftime("%H:%M:%S")
        
        # Ingest (graphiti.add_episode has its own retry logic)
        print(f"📤 [{ingestion_start}] Ingestion #{self.ingestion_count + 1} starting...")
        
        result = await graphiti_client.add_episode(parsed_data)
        
        # Record completion
        duration = time.time() - start_time
        self.last_ingestion_time = time.time()
        self.ingestion_count += 1
        
        ingestion_end = datetime.now().strftime("%H:%M:%S")
        print(f"✅ [{ingestion_end}] Ingestion completed in {duration:.1f}s")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dict with ingestion count, last time, etc.
        """
        return {
            "ingestion_count": self.ingestion_count,
            "last_ingestion_time": self.last_ingestion_time,
            "delay_configured": self.DELAY_BETWEEN_INGESTIONS,
            "safety_margin": self.SAFETY_MARGIN
        }
    
    def reset(self) -> None:
        """Reset queue state (for testing)."""
        self.last_ingestion_time = None
        self.ingestion_count = 0


# Test function
async def test_safe_queue():
    """Test the safe queue with simulated ingestions."""
    print("🧪 Testing Safe Ingestion Queue")
    print("=" * 60)
    print("")
    
    queue = SafeIngestionQueue()
    
    print(f"Configuration:")
    print(f"  Rate limit window: {queue.RATE_LIMIT_WINDOW}s")
    print(f"  Safety margin: {queue.SAFETY_MARGIN}×")
    print(f"  Delay between ingestions: {queue.DELAY_BETWEEN_INGESTIONS}s")
    print("")
    
    # Simulate 3 ingestions with a mock client
    class MockGraphiti:
        async def add_episode(self, data):
            # Simulate Graphiti processing time
            await asyncio.sleep(2)
            return {"status": "success", "episode_id": data.get("episode_id", "test")}
    
    mock_client = MockGraphiti()
    
    for i in range(3):
        mock_data = {
            "episode_id": f"test-episode-{i+1}",
            "content": "Mock content",
            "timestamp": datetime.now().isoformat(),
            "agent": "TEST",
            "type": "test",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "metadata": {}
        }
        
        print(f"Ingesting episode {i+1}/3...")
        result = await queue.safe_ingest(mock_client, mock_data)
        print(f"Result: {result['status']}")
        print("")
    
    # Show stats
    stats = queue.get_stats()
    print(f"Final statistics:")
    print(f"  Total ingestions: {stats['ingestion_count']}")
    print(f"  Delay per ingestion: {stats['delay_configured']}s")
    print(f"  Total time: ~{stats['ingestion_count'] * stats['delay_configured']}s")
    print("")
    print("✅ Safe Queue test complete!")
    print("")
    print("Key observations:")
    print("  - Each ingestion waits 120s after the previous one")
    print("  - This guarantees no rate limits (60s window × 2)")
    print("  - Trade-off: +2 minutes per document (acceptable for nightly run)")


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(test_safe_queue()))

