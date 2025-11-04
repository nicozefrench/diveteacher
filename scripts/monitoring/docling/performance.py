"""
Docling Performance Module

Monitor Docling conversion performance.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/upload"
TIMEOUT = 10.0


def get_performance_metrics(upload_id: str) -> Optional[Dict[str, Any]]:
    """
    Get Docling performance metrics from upload status
    
    Returns:
        Dict with performance metrics, None on error
    """
    try:
        response = httpx.get(
            f"{API_BASE}/{upload_id}/status",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        durations = data.get("durations", {})
        metrics = data.get("metrics", {})
        
        return {
            "conversion_duration": durations.get("docling", 0),
            "pages": metrics.get("pages", 0),
            "file_size_mb": metrics.get("file_size_mb", 0),
            "tables": metrics.get("tables", 0),
            "pictures": metrics.get("pictures", 0)
        }
    except httpx.HTTPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None


def show_performance(upload_id: str) -> int:
    """
    Display Docling performance metrics
    
    Returns:
        0 on success, 1 on error
    """
    metrics = get_performance_metrics(upload_id)
    
    if not metrics:
        return 1
    
    print(f"Docling Performance: {upload_id}")
    print("=" * 60)
    print()
    
    duration = metrics["conversion_duration"]
    pages = metrics["pages"]
    file_size = metrics["file_size_mb"]
    
    print(f"Conversion time:  {duration:.1f}s")
    print(f"File size:        {file_size:.2f} MB")
    print(f"Pages:            {pages}")
    print(f"Tables detected:  {metrics['tables']}")
    print(f"Pictures:         {metrics['pictures']}")
    print()
    
    # Calculate metrics
    if pages > 0 and duration > 0:
        pages_per_sec = pages / duration
        print(f"Speed:            {pages_per_sec:.2f} pages/second")
    
    if file_size > 0 and duration > 0:
        mb_per_sec = file_size / duration
        print(f"Throughput:       {mb_per_sec:.2f} MB/second")
    
    print()
    
    # Performance assessment
    if duration > 0 and pages > 0:
        time_per_page = duration / pages
        if time_per_page < 5:
            print("✅ Performance: EXCELLENT (< 5s/page)")
        elif time_per_page < 15:
            print("✅ Performance: GOOD (5-15s/page)")
        elif time_per_page < 30:
            print("⚠️  Performance: ACCEPTABLE (15-30s/page)")
        else:
            print("⚠️  Performance: SLOW (> 30s/page)")
    
    print()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.monitoring.docling.performance <upload_id>")
        sys.exit(1)
    
    upload_id = sys.argv[1]
    sys.exit(show_performance(upload_id))

