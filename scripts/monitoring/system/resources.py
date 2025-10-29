"""
System Resources Module

Display system resource usage.
"""

import subprocess
import sys
from typing import Dict, Any


def get_resources() -> Dict[str, Any]:
    """
    Get system resource usage from Docker
    
    Returns:
        Dict with resource usage for each container
    """
    containers = {}
    
    try:
        # Get container stats
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", 
             "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) >= 4:
                name = parts[0]
                if "rag-" in name:  # Only RAG containers
                    containers[name] = {
                        "cpu": parts[1],
                        "memory": parts[2],
                        "memory_pct": parts[3]
                    }
                    
    except Exception as e:
        print(f"❌ Error getting resources: {e}", file=sys.stderr)
    
    return containers


def show_resources() -> int:
    """
    Display system resources
    
    Returns:
        0 on success, 1 on error
    """
    print("System Resource Usage")
    print("=" * 80)
    print()
    
    resources = get_resources()
    
    if not resources:
        print("No containers found or error reading stats")
        return 1
    
    # Header
    print(f"{'Container':<25s} {'CPU':>10s} {'Memory':>20s} {'Mem %':>10s}")
    print("-" * 80)
    
    # Each container
    for name, stats in sorted(resources.items()):
        print(f"{name:<25s} {stats['cpu']:>10s} {stats['memory']:>20s} {stats['memory_pct']:>10s}")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(show_resources())

