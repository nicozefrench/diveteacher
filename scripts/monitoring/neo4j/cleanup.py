"""
Neo4j Cleanup Module

Safe graph cleanup with automatic backup.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/neo4j"
TIMEOUT = 120.0


def clear_graph(
    confirm: bool = False,
    api_base: str = API_BASE
) -> Optional[Dict[str, Any]]:
    """
    Clear all data from Neo4j with backup
    
    Args:
        confirm: If False, will prompt for confirmation
        api_base: API base URL
        
    Returns:
        Dict with deletion info, None on error
    """
    # Interactive confirmation if not confirmed
    if not confirm:
        print("⚠️  WARNING: This will DELETE ALL DATA in Neo4j")
        print()
        print("A backup will be created before clearing.")
        print()
        response = input("Type 'DELETE_ALL_DATA' to confirm: ")
        
        if response != "DELETE_ALL_DATA":
            print("Cancelled.")
            return None
    
    try:
        response = httpx.delete(
            f"{api_base}/clear",
            json={
                "confirm": True,
                "confirmation_code": "DELETE_ALL_DATA",
                "backup_first": True
            },
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Clear error: {e}", file=sys.stderr)
        return None


def show_clear_result(confirm: bool = False, api_base: str = API_BASE) -> int:
    """
    Clear graph and display results
    
    Returns:
        0 on success, 1 on error
    """
    result = clear_graph(confirm, api_base)
    
    if not result:
        return 1
    
    print()
    print("✅ Graph cleared successfully!")
    print()
    print(f"Backup ID:    {result.get('backup_export_id', 'N/A')}")
    
    deleted = result.get("deleted", {})
    print(f"Deleted:")
    print(f"  • Nodes:         {deleted.get('nodes', 0):,}")
    print(f"  • Relationships: {deleted.get('relationships', 0):,}")
    print()
    
    return 0


if __name__ == "__main__":
    confirm_flag = "--confirm" in sys.argv
    sys.exit(show_clear_result(confirm_flag))

