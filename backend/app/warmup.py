#!/usr/bin/env python3
"""
Warm-up script for Docling models

Executed at container startup to pre-download Docling recognition models
from HuggingFace and initialize the DoclingSingleton.

This ensures that the first document upload is fast and doesn't timeout
waiting for model downloads.

Usage:
    python3 -m app.warmup

Environment Variables:
    SKIP_WARMUP: Set to "true" to skip warm-up (useful for debugging)
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main warm-up entry point
    
    Returns:
        0 if successful, 1 if failed (non-blocking - container continues)
    """
    logger.info("")
    logger.info("🚀 Starting Docling Model Warm-up...")
    logger.info("")
    
    # Import here to avoid circular imports
    from app.integrations.dockling import DoclingSingleton
    
    # Call warmup method
    success = DoclingSingleton.warmup()
    
    if success:
        logger.info("🎯 Warm-up completed successfully!")
        logger.info("")
        return 0
    else:
        logger.warning("⚠️  Warm-up completed with warnings")
        logger.warning("⚠️  Application will continue, but first upload may be slower")
        logger.info("")
        return 1


if __name__ == "__main__":
    sys.exit(main())

