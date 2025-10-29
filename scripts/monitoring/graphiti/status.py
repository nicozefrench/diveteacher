"""
Graphiti Ingestion Status Module

Check status of document ingestion.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/upload"
TIMEOUT = 10.0


def get_status(upload_id: str, api_base: str = API_BASE) -> Optional[Dict[str, Any]]:
    """
    Get processing status for an upload
    
    Args:
        upload_id: Upload identifier
        api_base: API base URL
        
    Returns:
        Dict with status info, None on error
    """
    try:
        response = httpx.get(
            f"{api_base}/status/{upload_id}",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Status error: {e}", file=sys.stderr)
        return None


def show_status(upload_id: str, api_base: str = API_BASE) -> int:
    """
    Display processing status
    
    Returns:
        0 on success, 1 on error
    """
    status = get_status(upload_id, api_base)
    
    if not status:
        return 1
    
    # Status icons
    status_icons = {
        "pending": "⏳",
        "processing": "🔄",
        "completed": "✅",
        "failed": "❌"
    }
    
    current_status = status.get("status", "unknown")
    icon = status_icons.get(current_status, "❓")
    
    print(f"Upload: {upload_id}")
    print("=" * 60)
    print(f"Status:    {icon} {current_status.upper()}")
    print(f"Stage:     {status.get('stage', 'N/A')}")
    
    sub_stage = status.get("sub_stage")
    if sub_stage:
        print(f"Sub-stage: {sub_stage}")
    
    progress = status.get("progress", 0)
    print(f"Progress:  {progress}%")
    
    # Progress detail
    detail = status.get("progress_detail", {})
    if detail:
        print(f"           {detail.get('current', 0)}/{detail.get('total', 0)} {detail.get('unit', '')}")
    
    # Timestamps
    started_at = status.get("started_at")
    if started_at:
        print(f"\nStarted:   {started_at}")
    
    completed_at = status.get("completed_at")
    if completed_at:
        print(f"Completed: {completed_at}")
    
    # Metrics
    metrics = status.get("metrics", {})
    if metrics:
        print("\nMetrics:")
        for key, value in sorted(metrics.items()):
            # Format key nicely
            key_display = key.replace("_", " ").title()
            print(f"  • {key_display:25s} {value}")
    
    # Error
    error = status.get("error")
    if error:
        print(f"\n❌ Error: {error}")
    
    print()
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.monitoring.graphiti.status <upload_id>")
        sys.exit(1)
    
    upload_id = sys.argv[1]
    sys.exit(show_status(upload_id))

