"""
Neo4j Query Executor Module

Execute Cypher queries via API.
"""

import httpx
import sys
import json
from typing import Dict, Any, Optional, List


API_BASE = "http://localhost:8000/api/neo4j"
TIMEOUT = 30.0


def execute_query(
    cypher: str,
    params: Optional[Dict[str, Any]] = None,
    api_base: str = API_BASE,
    timeout: float = TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Execute a Cypher query via API
    
    Args:
        cypher: Cypher query string
        params: Optional query parameters
        api_base: API base URL
        timeout: Request timeout
        
    Returns:
        Dict with records and summary, None on error
    """
    try:
        response = httpx.post(
            f"{api_base}/query",
            json={
                "cypher": cypher,
                "params": params or {},
                "timeout": int(timeout)
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Query error: {e}", file=sys.stderr)
        return None


def show_query_results(
    cypher: str,
    params: Optional[Dict[str, Any]] = None,
    api_base: str = API_BASE
) -> int:
    """
    Execute query and display formatted results
    
    Returns:
        0 on success, 1 on error
    """
    print(f"Executing query: {cypher}")
    if params:
        print(f"Parameters: {params}")
    print()
    
    result = execute_query(cypher, params, api_base)
    
    if not result:
        return 1
    
    records = result.get("records", [])
    summary = result.get("summary", {})
    
    if not records:
        print("No results returned")
        return 0
    
    # Display results as table
    if records:
        # Get all keys from first record
        keys = list(records[0].keys())
        
        # Print header
        print("┌" + "─" * 60 + "┐")
        for key in keys:
            print(f"│ {key:58s} │")
        print("├" + "─" * 60 + "┤")
        
        # Print records
        for record in records:
            for key in keys:
                value = record.get(key, "")
                # Truncate long values
                value_str = str(value)[:56]
                print(f"│ {value_str:58s} │")
            print("├" + "─" * 60 + "┤")
        
        print("└" + "─" * 60 + "┘")
    
    # Summary
    print()
    print(f"Returned: {len(records)} records")
    exec_time = summary.get("execution_time_ms", 0)
    print(f"Execution time: {exec_time:.1f}ms")
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.monitoring.neo4j.query '<CYPHER>'")
        sys.exit(1)
    
    cypher = sys.argv[1]
    sys.exit(show_query_results(cypher))

