"""
Docling Warm-up Verification Module

Wrapper for verify-warmup.sh script with Python interface.
"""

import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parent.parent.parent / "verify-warmup.sh"


def verify_warmup() -> int:
    """
    Verify Docling warm-up effectiveness
    
    Calls the verify-warmup.sh script
    
    Returns:
        0 if warm-up is effective, 1 otherwise
    """
    if not SCRIPT_PATH.exists():
        print(f"❌ Error: Script not found: {SCRIPT_PATH}")
        return 1
    
    try:
        result = subprocess.run(
            [str(SCRIPT_PATH)],
            check=False,
            capture_output=False
        )
        return result.returncode
    except Exception as e:
        print(f"❌ Error running verification: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(verify_warmup())

