"""
System Health Check Module

Overall system health check.
"""

import httpx
import sys
from typing import Dict, Any, List


API_BASE = "http://localhost:8000/api"
TIMEOUT = 10.0


def check_health() -> Dict[str, Any]:
    """
    Check health of all system components
    
    Returns:
        Dict with health status of each component
    """
    results = {
        "components": [],
        "healthy": 0,
        "unhealthy": 0,
        "overall": "unknown"
    }
    
    # Check backend API
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        results["components"].append({
            "name": "Backend API",
            "status": "✅ HEALTHY",
            "detail": f"Response time: {response.elapsed.total_seconds():.2f}s"
        })
        results["healthy"] += 1
        
        # Check sub-components from health endpoint
        neo4j_status = data.get("neo4j", {}).get("status", "unknown")
        if neo4j_status == "healthy":
            results["components"].append({
                "name": "Neo4j",
                "status": "✅ HEALTHY",
                "detail": "Connected"
            })
            results["healthy"] += 1
        else:
            results["components"].append({
                "name": "Neo4j",
                "status": "❌ UNHEALTHY",
                "detail": neo4j_status
            })
            results["unhealthy"] += 1
            
        ollama_status = data.get("ollama", {}).get("status", "unknown")
        if ollama_status == "healthy":
            results["components"].append({
                "name": "Ollama",
                "status": "✅ HEALTHY",
                "detail": "Connected"
            })
            results["healthy"] += 1
        else:
            results["components"].append({
                "name": "Ollama",
                "status": "⚠️  DEGRADED",
                "detail": ollama_status
            })
            results["unhealthy"] += 1
            
    except Exception as e:
        results["components"].append({
            "name": "Backend API",
            "status": "❌ UNHEALTHY",
            "detail": str(e)
        })
        results["unhealthy"] += 1
    
    # Overall status
    if results["unhealthy"] == 0:
        results["overall"] = "✅ HEALTHY"
    elif results["healthy"] > 0:
        results["overall"] = "⚠️  DEGRADED"
    else:
        results["overall"] = "❌ UNHEALTHY"
    
    return results


def show_health() -> int:
    """
    Display system health
    
    Returns:
        0 if healthy, 1 if unhealthy
    """
    print("System Health Check")
    print("=" * 60)
    print()
    
    health = check_health()
    
    for component in health["components"]:
        print(f"{component['status']:15s} {component['name']}")
        print(f"                {component['detail']}")
        print()
    
    print("=" * 60)
    print(f"Overall: {health['overall']}")
    print(f"Summary: {health['healthy']} healthy, {health['unhealthy']} unhealthy")
    print()
    
    return 0 if health["unhealthy"] == 0 else 1


if __name__ == "__main__":
    sys.exit(show_health())

