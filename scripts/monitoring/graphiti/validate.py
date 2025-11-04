"""
Graphiti Validation Module

Validate Graphiti ingestion results.
"""

import httpx
import sys
from typing import Optional, Dict, Any, List


API_BASE_NEO4J = "http://localhost:8000/api/neo4j"
API_BASE_UPLOAD = "http://localhost:8000/api/upload"
TIMEOUT = 30.0


def validate_ingestion(upload_id: str) -> Dict[str, Any]:
    """
    Validate Graphiti ingestion for an upload
    
    Checks:
    1. Upload status is completed
    2. Neo4j has nodes and relationships
    3. Metrics match expectations
    
    Returns:
        Dict with validation results
    """
    results = {
        "upload_id": upload_id,
        "checks": [],
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    # Check 1: Upload status
    try:
        response = httpx.get(f"{API_BASE_UPLOAD}/{upload_id}/status", timeout=TIMEOUT)
        response.raise_for_status()
        status_data = response.json()
        
        status = status_data.get("status")
        if status == "completed":
            results["checks"].append({
                "name": "Upload Status",
                "status": "✅ PASS",
                "detail": "Completed successfully"
            })
            results["passed"] += 1
        elif status == "failed":
            results["checks"].append({
                "name": "Upload Status",
                "status": "❌ FAIL",
                "detail": f"Upload failed: {status_data.get('error', 'Unknown error')}"
            })
            results["failed"] += 1
        else:
            results["checks"].append({
                "name": "Upload Status",
                "status": "⚠️  WARN",
                "detail": f"Upload still {status}"
            })
            results["warnings"] += 1
            
        metrics = status_data.get("metrics", {})
        
    except Exception as e:
        results["checks"].append({
            "name": "Upload Status",
            "status": "❌ FAIL",
            "detail": f"Error: {e}"
        })
        results["failed"] += 1
        metrics = {}
    
    # Check 2: Neo4j nodes exist
    try:
        response = httpx.get(f"{API_BASE_NEO4J}/stats", timeout=TIMEOUT)
        response.raise_for_status()
        neo4j_stats = response.json()
        
        node_count = neo4j_stats.get("nodes", {}).get("total", 0)
        if node_count > 0:
            results["checks"].append({
                "name": "Neo4j Nodes",
                "status": "✅ PASS",
                "detail": f"{node_count} nodes found"
            })
            results["passed"] += 1
        else:
            results["checks"].append({
                "name": "Neo4j Nodes",
                "status": "❌ FAIL",
                "detail": "No nodes in database"
            })
            results["failed"] += 1
            
    except Exception as e:
        results["checks"].append({
            "name": "Neo4j Nodes",
            "status": "❌ FAIL",
            "detail": f"Error: {e}"
        })
        results["failed"] += 1
    
    # Check 3: Entities extracted
    entities = metrics.get("entities_extracted", 0)
    if entities > 0:
        results["checks"].append({
            "name": "Entity Extraction",
            "status": "✅ PASS",
            "detail": f"{entities} entities extracted"
        })
        results["passed"] += 1
    elif metrics:
        results["checks"].append({
            "name": "Entity Extraction",
            "status": "⚠️  WARN",
            "detail": "No entities extracted"
        })
        results["warnings"] += 1
    
    # Check 4: Relations extracted
    relations = metrics.get("relations_extracted", 0)
    if relations > 0:
        results["checks"].append({
            "name": "Relation Extraction",
            "status": "✅ PASS",
            "detail": f"{relations} relations extracted"
        })
        results["passed"] += 1
    elif metrics:
        results["checks"].append({
            "name": "Relation Extraction",
            "status": "⚠️  WARN",
            "detail": "No relations extracted"
        })
        results["warnings"] += 1
    
    return results


def show_validation(upload_id: str) -> int:
    """
    Validate and display results
    
    Returns:
        0 if all checks passed, 1 otherwise
    """
    print(f"Validating Graphiti ingestion: {upload_id}")
    print("=" * 60)
    print()
    
    results = validate_ingestion(upload_id)
    
    for check in results["checks"]:
        print(f"{check['status']:10s} {check['name']}")
        print(f"           {check['detail']}")
        print()
    
    print("=" * 60)
    print(f"Results: {results['passed']} passed, {results['failed']} failed, {results['warnings']} warnings")
    print()
    
    if results['failed'] > 0:
        print("❌ Validation FAILED")
        return 1
    elif results['warnings'] > 0:
        print("⚠️  Validation passed with warnings")
        return 0
    else:
        print("✅ Validation PASSED")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.monitoring.graphiti.validate <upload_id>")
        sys.exit(1)
    
    upload_id = sys.argv[1]
    sys.exit(show_validation(upload_id))

