"""
Graphiti Metrics Module

Display ingestion metrics for an upload.
"""

import httpx
import sys
from typing import Optional, Dict, Any


API_BASE = "http://localhost:8000/api/upload"
TIMEOUT = 10.0


def get_metrics(upload_id: str, api_base: str = API_BASE) -> Optional[Dict[str, Any]]:
    """
    Get processing metrics for an upload
    
    Args:
        upload_id: Upload identifier
        api_base: API base URL
        
    Returns:
        Dict with metrics, None on error
    """
    try:
        # Get status which includes metrics
        response = httpx.get(
            f"{api_base}/status/{upload_id}",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("metrics", {})
    except httpx.HTTPError as e:
        print(f"❌ Metrics error: {e}", file=sys.stderr)
        return None


def show_metrics(upload_id: str, api_base: str = API_BASE) -> int:
    """
    Display ingestion metrics
    
    Returns:
        0 on success, 1 on error
    """
    metrics = get_metrics(upload_id, api_base)
    
    if metrics is None:
        return 1
    
    if not metrics:
        print(f"No metrics available for upload: {upload_id}")
        return 0
    
    print(f"Ingestion Metrics: {upload_id}")
    print("=" * 60)
    print()
    
    # Document metrics
    print("Document:")
    print(f"  File size:       {metrics.get('file_size_mb', 0):.2f} MB")
    print(f"  Pages:           {metrics.get('pages', 0)}")
    print()
    
    # Chunking metrics
    chunks_total = metrics.get("chunks_total", 0)
    chunks_processed = metrics.get("chunks_processed", 0)
    print("Chunking:")
    print(f"  Total chunks:    {chunks_total}")
    print(f"  Processed:       {chunks_processed}")
    if chunks_total > 0:
        pct = (chunks_processed / chunks_total) * 100
        print(f"  Progress:        {pct:.1f}%")
    print()
    
    # Graphiti metrics
    print("Graphiti Ingestion:")
    print(f"  Entities:        {metrics.get('entities_extracted', 0)}")
    print(f"  Relations:       {metrics.get('relations_extracted', 0)}")
    print()
    
    # Neo4j metrics
    print("Neo4j:")
    print(f"  Nodes created:   {metrics.get('neo4j_nodes_created', 0)}")
    print(f"  Relations:       {metrics.get('neo4j_relations_created', 0)}")
    print()
    
    # API usage
    print("Claude API:")
    print(f"  API calls:       {metrics.get('claude_api_calls', 0)}")
    print(f"  Tokens used:     {metrics.get('claude_tokens_used', 0):,}")
    print()
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.monitoring.graphiti.metrics <upload_id>")
        sys.exit(1)
    
    upload_id = sys.argv[1]
    sys.exit(show_metrics(upload_id))

