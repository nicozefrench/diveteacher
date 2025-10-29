"""
Neo4j Health Check Module

Check Neo4j connection health via API.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/neo4j"
TIMEOUT = 10.0


def check_health(api_base: str = API_BASE) -> Optional[Dict[str, Any]]:
    """
    Check Neo4j health
    
    Returns:
        Dict with health status, None on error
    """
    try:
        response = httpx.get(
            f"{api_base}/health",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Health check error: {e}", file=sys.stderr)
        return None


def show_health(api_base: str = API_BASE) -> int:
    """
    Check and display Neo4j health
    
    Returns:
        0 if healthy, 1 if unhealthy or error
    """
    health = check_health(api_base)
    
    if not health:
        return 1
    
    status = health.get("status", "unknown")
    connection = health.get("connection", "unknown")
    latency = health.get("latency_ms", 0)
    issues = health.get("issues", [])
    
    # Status icons
    status_icons = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌"
    }
    icon = status_icons.get(status, "❓")
    
    print("Neo4j Health Check")
    print("=" * 40)
    print(f"Status:     {icon} {status.upper()}")
    print(f"Connection: {connection}")
    print(f"Latency:    {latency:.1f}ms")
    
    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  • {issue}")
    
    print()
    
    return 0 if status == "healthy" else 1


if __name__ == "__main__":
    sys.exit(show_health())

