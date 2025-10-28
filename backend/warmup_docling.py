#!/usr/bin/env python3
"""
Warm-up script for Docling models
Downloads and caches all required models at container startup
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def warmup_docling_models():
    """
    Download and cache Docling models before first document processing
    This prevents timeout issues during the first upload
    """
    logger.info("=" * 60)
    logger.info("🔥 WARMING UP DOCLING MODELS")
    logger.info("=" * 60)
    
    try:
        # Import Docling - this triggers model downloads
        logger.info("📦 Importing Docling library...")
        from docling.document_converter import DocumentConverter
        
        logger.info("✅ Docling library imported successfully")
        
        # Create a dummy converter to trigger model downloads
        logger.info("🔄 Initializing DocumentConverter (downloads models)...")
        logger.info("⏳ This may take several minutes on first run...")
        
        converter = DocumentConverter()
        
        logger.info("✅ DocumentConverter initialized - models cached!")
        logger.info("=" * 60)
        logger.info("🎉 DOCLING WARM-UP COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("ℹ️  Models are now cached and ready for use")
        logger.info("ℹ️  Subsequent document processing will be fast")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ WARM-UP FAILED: {e}")
        logger.error("=" * 60)
        logger.error("")
        logger.error("⚠️  Document processing may be slower on first upload")
        logger.error("⚠️  Models will be downloaded on-demand")
        logger.error("")
        return False

if __name__ == "__main__":
    logger.info("")
    logger.info("🚀 Starting Docling Model Warm-up...")
    logger.info("")
    
    success = warmup_docling_models()
    
    sys.exit(0 if success else 1)

