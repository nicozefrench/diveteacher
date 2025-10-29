"""
Docker Container Stats Module

Display Docker container status and information.
"""

import subprocess
import sys
from typing import Dict, Any, List


def get_docker_stats() -> List[Dict[str, Any]]:
    """
    Get Docker container statistics
    
    Returns:
        List of dicts with container info
    """
    containers = []
    
    try:
        # Get container list
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", 
             "{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) >= 3:
                name = parts[0]
                if "rag-" in name:  # Only RAG containers
                    containers.append({
                        "name": name,
                        "status": parts[1],
                        "image": parts[2],
                        "ports": parts[3] if len(parts) > 3 else ""
                    })
                    
    except Exception as e:
        print(f"❌ Error getting Docker stats: {e}", file=sys.stderr)
    
    return containers


def show_docker_stats() -> int:
    """
    Display Docker container stats
    
    Returns:
        0 on success, 1 on error
    """
    print("Docker Container Status")
    print("=" * 100)
    print()
    
    containers = get_docker_stats()
    
    if not containers:
        print("No RAG containers found")
        return 1
    
    # Count statuses
    running = sum(1 for c in containers if "Up" in c["status"])
    stopped = len(containers) - running
    
    print(f"Total: {len(containers)} containers ({running} running, {stopped} stopped)")
    print()
    
    # Header
    print(f"{'Container':<20s} {'Status':<30s} {'Image':<30s}")
    print("-" * 100)
    
    # Each container
    for container in sorted(containers, key=lambda x: x["name"]):
        status_icon = "✅" if "Up" in container["status"] else "❌"
        name = container["name"]
        status = container["status"]
        image = container["image"][:28]  # Truncate long image names
        
        print(f"{status_icon} {name:<18s} {status:<29s} {image:<30s}")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(show_docker_stats())

