"""
Neo4j Export Module

Export graph data via API.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/neo4j"
TIMEOUT = 120.0


def export_graph(
    format: str = "json",
    api_base: str = API_BASE,
    timeout: float = TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Export graph data
    
    Args:
        format: Export format (json, cypher, graphml)
        api_base: API base URL
        timeout: Request timeout
        
    Returns:
        Dict with export_id and download_url, None on error
    """
    try:
        response = httpx.post(
            f"{api_base}/export",
            json={"format": format},
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Export error: {e}", file=sys.stderr)
        return None


def show_export_info(
    format: str = "json",
    api_base: str = API_BASE
) -> int:
    """
    Export graph and display info
    
    Returns:
        0 on success, 1 on error
    """
    print(f"Exporting graph data (format: {format})...")
    
    result = export_graph(format, api_base)
    
    if not result:
        return 1
    
    print()
    print("✅ Export successful!")
    print()
    print(f"Export ID:     {result.get('export_id', 'N/A')}")
    print(f"Download URL:  {result.get('download_url', 'N/A')}")
    print(f"Size:          {result.get('size_bytes', 0):,} bytes")
    print(f"Records:       {result.get('record_count', 0):,}")
    print()
    
    return 0


if __name__ == "__main__":
    format_arg = sys.argv[1] if len(sys.argv) > 1 else "json"
    sys.exit(show_export_info(format_arg))

