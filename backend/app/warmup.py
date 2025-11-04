#!/usr/bin/env python3
"""
Warm-up script for Docling models and Cross-Encoder Reranker

Executed at container startup to pre-download:
1. Docling recognition models from HuggingFace
2. Cross-Encoder reranker model (ms-marco-MiniLM-L-6-v2)

This ensures that the first document upload and RAG query are fast
and don't timeout waiting for model downloads.

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
    
    Warms up:
    1. Docling models (OCR, table recognition)
    2. Cross-Encoder reranker (ms-marco-MiniLM-L-6-v2)
    
    Returns:
        0 if successful, 1 if failed (non-blocking - container continues)
    """
    logger.info("")
    logger.info("🚀 Starting Model Warm-up (Docling + Reranker)...")
    logger.info("")
    
    success = True
    
    # Step 1: Warm-up Docling
    logger.info("=" * 60)
    logger.info("STEP 1: Warming up Docling models...")
    logger.info("=" * 60)
    
    try:
        from app.integrations.dockling import DoclingSingleton
        docling_success = DoclingSingleton.warmup()
        
        if docling_success:
            logger.info("✅ Docling warm-up completed successfully!")
        else:
            logger.warning("⚠️  Docling warm-up completed with warnings")
            success = False
    except Exception as e:
        logger.error(f"❌ Docling warm-up failed: {e}")
        success = False
    
    logger.info("")
    
    # Step 2: Warm-up Cross-Encoder Reranker
    logger.info("=" * 60)
    logger.info("STEP 2: Warming up Cross-Encoder Reranker...")
    logger.info("=" * 60)
    
    try:
        from app.core.reranker import get_reranker
        from app.core.config import settings
        
        if settings.RAG_RERANKING_ENABLED:
            logger.info("📊 Reranking is ENABLED, loading model...")
            
            # Load reranker (will download model if not cached)
            reranker = get_reranker()
            
            # Perform a test reranking to ensure model is fully loaded
            test_facts = [
                {"fact": "Test fact 1", "id": 1},
                {"fact": "Test fact 2", "id": 2},
                {"fact": "Test fact 3", "id": 3}
            ]
            test_query = "test query"
            
            logger.info("🧪 Performing test reranking...")
            result = reranker.rerank(test_query, test_facts, top_k=2)
            
            if len(result) == 2:
                logger.info("✅ Cross-Encoder Reranker warm-up completed successfully!")
                logger.info(f"   Model: {reranker.model_name}")
                logger.info("   Status: Ready for RAG queries")
            else:
                logger.warning("⚠️  Reranker test returned unexpected results")
                success = False
        else:
            logger.info("ℹ️  Reranking is DISABLED (RAG_RERANKING_ENABLED=False)")
            logger.info("   Skipping reranker warm-up")
    except Exception as e:
        logger.error(f"❌ Reranker warm-up failed: {e}")
        logger.warning("⚠️  RAG queries will still work, but reranking will be unavailable")
        success = False
    
    logger.info("")
    logger.info("=" * 60)
    
    if success:
        logger.info("🎯 All warm-ups completed successfully!")
        logger.info("   ✅ Docling: Ready")
        logger.info("   ✅ Reranker: Ready")
        logger.info("")
        return 0
    else:
        logger.warning("⚠️  Warm-up completed with warnings")
        logger.warning("⚠️  Application will continue, but some features may be slower")
        logger.info("")
        return 1


if __name__ == "__main__":
    sys.exit(main())

