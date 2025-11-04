"""
Test API endpoints for A/B testing and benchmarking

These endpoints are designed for testing specific components
without full RAG pipeline overhead.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.rag import retrieve_context
from app.core.config import settings

router = APIRouter()


class RetrievalTestRequest(BaseModel):
    """Request model for retrieval-only testing"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    use_reranking: Optional[bool] = Field(None, description="Enable cross-encoder reranking")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of facts to retrieve")
    group_ids: Optional[List[str]] = Field(None, description="Filter by group IDs (multi-tenant)")


class RetrievalTestResponse(BaseModel):
    """Response model for retrieval-only testing"""
    question: str
    facts: list
    total: int
    reranked: bool


@router.post("/retrieval", response_model=RetrievalTestResponse)
async def test_retrieval(request: RetrievalTestRequest):
    """
    Test retrieval + reranking WITHOUT LLM generation
    
    This endpoint is designed for A/B testing the cross-encoder reranking
    without the overhead of LLM answer generation.
    
    Expected performance: ~2-5 seconds per query
    
    Args:
        request: Retrieval test parameters
        
    Returns:
        Retrieved facts (optionally reranked) without LLM answer
    """
    # Use settings defaults if not provided
    top_k = request.top_k if request.top_k is not None else settings.RAG_TOP_K
    use_reranking = request.use_reranking if request.use_reranking is not None else settings.RAG_RERANKING_ENABLED
    
    # Retrieve context (with optional reranking)
    context = await retrieve_context(
        question=request.question,
        top_k=top_k,
        group_ids=request.group_ids,
        use_reranking=use_reranking
    )
    
    return RetrievalTestResponse(
        question=request.question,
        facts=context['facts'],
        total=context['total'],
        reranked=context.get('reranked', False)
    )

