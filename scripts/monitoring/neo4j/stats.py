"""
Neo4j Statistics Module

Retrieves and displays Neo4j graph statistics.
"""

import httpx
import sys
from typing import Dict, Any, Optional


API_BASE = "http://localhost:8000/api/neo4j"
TIMEOUT = 30.0


def get_stats(api_base: str = API_BASE) -> Optional[Dict[str, Any]]:
    """
    Get Neo4j statistics from API
    
    Returns:
        Dict with nodes, relationships, indexes, storage info
        None if error
    """
    try:
        response = httpx.get(
            f"{api_base}/stats",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Error fetching stats: {e}", file=sys.stderr)
        return None


def show_stats(api_base: str = API_BASE) -> int:
    """
    Fetch and display Neo4j statistics in formatted output
    
    Returns:
        0 on success, 1 on error
    """
    stats = get_stats(api_base)
    
    if not stats:
        return 1
    
    # Header
    print("=" * 60)
    print("Neo4j Graph Statistics")
    print("=" * 60)
    print()
    
    # Status
    status = stats.get("status", "unknown")
    status_icon = "✅" if status == "healthy" else "⚠️"
    print(f"Status:        {status_icon} {status.capitalize()}")
    print(f"Version:       {stats.get('version', 'N/A')}")
    print(f"Database:      {stats.get('database', 'N/A')}")
    print()
    
    # Nodes
    nodes = stats.get("nodes", {})
    print(f"Total Nodes:   {nodes.get('total', 0):,}")
    
    by_label = nodes.get("by_label", {})
    if by_label:
        print("\nNodes by Label:")
        for label, count in sorted(by_label.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {label:20s} {count:,}")
    
    # Relationships
    rels = stats.get("relationships", {})
    print(f"\nTotal Relationships: {rels.get('total', 0):,}")
    
    by_type = rels.get("by_type", {})
    if by_type:
        print("\nRelationships by Type:")
        for rel_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rel_type:20s} {count:,}")
    
    # Indexes
    indexes = stats.get("indexes", {})
    if indexes:
        print(f"\nIndexes:       {indexes.get('total', 0)}")
        types = indexes.get("types", [])
        if types:
            print(f"  Types: {', '.join(types)}")
    
    # Storage
    storage = stats.get("storage", {})
    if storage:
        print(f"\nStorage:")
        size_mb = storage.get("size_mb", 0)
        print(f"  Total size:  {size_mb:.1f} MB")
    
    print()
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(show_stats())

