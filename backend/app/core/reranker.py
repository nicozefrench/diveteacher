"""
Cross-Encoder Reranker Module for DiveTeacher RAG System

This module implements cross-encoder reranking to improve retrieval precision.
Based on Cole Medin's "Ultimate n8n RAG Agent" reranking strategy.

Model: ms-marco-MiniLM-L-6-v2 (FREE, 100MB, proven for RAG)
- Input: Query + Fact pairs
- Output: Relevance scores (-inf to +inf)
- Performance: ~100ms for 20 facts (CPU)
- Cost: FREE (local inference)

Author: DiveTeacher Team
Date: November 4, 2025
"""

from sentence_transformers import CrossEncoder
import logging
from typing import List, Dict, Any
import time

logger = logging.getLogger('diveteacher.reranker')


class CrossEncoderReranker:
    """
    Production-ready reranker using sentence-transformers cross-encoder.

    Model: ms-marco-MiniLM-L-6-v2 (FREE, 100MB, proven for RAG)

    This reranker improves retrieval precision by scoring query-fact pairs
    using a cross-encoder model specifically trained for information retrieval.

    Based on Cole Medin's "Ultimate n8n RAG Agent" reranking strategy.

    Attributes:
        model: CrossEncoder instance (ms-marco-MiniLM-L-6-v2)
        model_name: Name of the HuggingFace model

    Example:
        >>> reranker = CrossEncoderReranker()
        >>> facts = [{"fact": "Safety first"}, {"fact": "Check equipment"}]
        >>> reranked = reranker.rerank("diving safety", facts, top_k=1)
        >>> print(reranked[0]["fact"])
        "Safety first"
    """

    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        """
        Initialize cross-encoder model.

        Args:
            model_name: HuggingFace model name (default: ms-marco-MiniLM-L-6-v2)

        Raises:
            RuntimeError: If model fails to load

        Note:
            First run will download ~100MB model from HuggingFace Hub.
            Subsequent runs load from cache (~/.cache/huggingface/).
        """
        logger.info(f"🔧 Loading cross-encoder model: {model_name}...")
        logger.info("   This may take 10-20 seconds on first run (downloading 100MB model)")

        try:
            self.model = CrossEncoder(model_name)
            self.model_name = model_name
            logger.info(f"✅ Cross-encoder loaded successfully: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load cross-encoder: {e}")
            raise RuntimeError(f"Cross-encoder initialization failed: {e}")

    def rerank(
        self,
        query: str,
        facts: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank facts using cross-encoder relevance scoring.

        Args:
            query: User's question
            facts: List of facts from Graphiti (e.g., top_k=20)
            top_k: Number of results to return after reranking (default: 5)

        Returns:
            Reranked list of top_k facts (sorted by relevance, descending)

        Note:
            - If len(facts) <= top_k, returns facts as-is (no reranking needed)
            - Runs on CPU (~100ms for 20 facts)
            - Scores range from -inf to +inf (higher = more relevant)
            - Falls back to original order on error

        Example:
            >>> reranker = CrossEncoderReranker()
            >>> facts = [
            ...     {"fact": "Equipment maintenance is important"},
            ...     {"fact": "Diving safety procedures"}
            ... ]
            >>> reranked = reranker.rerank("What are diving safety rules?", facts, top_k=1)
            >>> print(reranked[0]["fact"])
            "Diving safety procedures"
        """
        if not facts:
            logger.warning("⚠️  Empty facts list, returning empty")
            return []

        if len(facts) <= top_k:
            logger.info(f"ℹ️  Only {len(facts)} facts (≤ top_k={top_k}), no reranking needed")
            return facts[:top_k]

        logger.info(f"🔁 Reranking {len(facts)} facts to top {top_k}...")

        try:
            # Create query-fact pairs for cross-encoder
            pairs = []
            for fact in facts:
                fact_text = fact.get("fact", "")
                if not fact_text:
                    logger.warning(f"⚠️  Empty fact text in fact: {fact}")
                    fact_text = ""
                pairs.append([query, fact_text])

            # Score pairs (CPU-based, ~100ms for 20 pairs)
            start_time = time.time()
            scores = self.model.predict(pairs)
            rerank_duration = time.time() - start_time

            # Sort by score (descending = highest relevance first)
            facts_with_scores = list(zip(facts, scores))
            facts_with_scores.sort(key=lambda x: x[1], reverse=True)

            # Return top_k
            reranked_facts = [fact for fact, score in facts_with_scores[:top_k]]

            # Log statistics
            if len(scores) > 0:
                top_score = facts_with_scores[0][1]
                bottom_score = facts_with_scores[-1][1]
                avg_score = sum(scores) / len(scores)

                logger.info(f"✅ Reranking complete in {rerank_duration*1000:.0f}ms:")
                logger.info(f"   Top score: {top_score:.3f}")
                logger.info(f"   Bottom score: {bottom_score:.3f}")
                logger.info(f"   Avg score: {avg_score:.3f}")
                logger.info(f"   Returned top {len(reranked_facts)} facts")

            return reranked_facts

        except Exception as e:
            logger.error(f"❌ Reranking failed: {e}", exc_info=True)
            # Fallback to original order
            logger.warning("⚠️  Falling back to original order (no reranking)")
            return facts[:top_k]


# Singleton instance
_reranker_instance = None


def get_reranker() -> CrossEncoderReranker:
    """
    Get or create singleton CrossEncoderReranker instance.

    Returns:
        Global reranker instance (loads model once, reuses for all queries)

    Note:
        Singleton pattern ensures model is loaded only once, improving performance.
        Model stays in RAM (~200MB) for the lifetime of the application.

    Example:
        >>> reranker1 = get_reranker()
        >>> reranker2 = get_reranker()
        >>> assert reranker1 is reranker2  # Same instance
    """
    global _reranker_instance
    if _reranker_instance is None:
        logger.info("🏗️  Creating CrossEncoderReranker singleton...")
        _reranker_instance = CrossEncoderReranker()
    return _reranker_instance

