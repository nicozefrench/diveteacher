"""
Docling Cache Info Module

Display Docling model cache information.
"""

import subprocess
import sys
from pathlib import Path


def get_cache_info() -> dict:
    """
    Get cache information from container
    
    Returns:
        Dict with cache info
    """
    container_name = "rag-backend"
    cache_dir = "/root/.cache/huggingface"
    
    info = {
        "exists": False,
        "size_mb": 0,
        "file_count": 0,
        "files": []
    }
    
    # Check if cache exists
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "test", "-d", cache_dir],
            capture_output=True,
            check=False
        )
        info["exists"] = (result.returncode == 0)
    except:
        pass
    
    if not info["exists"]:
        return info
    
    # Get cache size
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "du", "-sm", cache_dir],
            capture_output=True,
            text=True,
            check=True
        )
        size_str = result.stdout.strip().split()[0]
        info["size_mb"] = int(size_str)
    except:
        pass
    
    # List model files
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "find", cache_dir, 
             "-type", "f", "(", "-name", "*.bin", "-o", "-name", "*.safetensors", ")"],
            capture_output=True,
            text=True,
            check=False
        )
        files = [f for f in result.stdout.strip().split("\n") if f]
        info["file_count"] = len(files)
        info["files"] = [Path(f).name for f in files[:10]]  # First 10
    except:
        pass
    
    return info


def show_cache_info() -> int:
    """
    Display cache information
    
    Returns:
        0 on success, 1 on error
    """
    print("Docling Model Cache Information")
    print("=" * 60)
    print()
    
    info = get_cache_info()
    
    if not info["exists"]:
        print("❌ Cache directory not found")
        print("\nThis means Docling models are NOT cached.")
        print("Run: docker compose -f docker/docker-compose.dev.yml build backend")
        print()
        return 1
    
    print("✅ Cache directory exists")
    print(f"Size:       {info['size_mb']} MB")
    print(f"Files:      {info['file_count']}")
    print()
    
    if info["files"]:
        print("Model files (showing first 10):")
        for f in info["files"]:
            print(f"  • {f}")
        print()
    
    # Assessment
    if info["size_mb"] >= 50:
        print("✅ Cache size looks good (>= 50 MB)")
    else:
        print("⚠️  Cache size is small (< 50 MB)")
        print("Models may not be fully cached.")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(show_cache_info())

