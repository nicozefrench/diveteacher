"""
Query API - RAG endpoints for DiveTeacher

This module provides the query endpoints for the RAG (Retrieval-Augmented Generation) system.
It handles both streaming and non-streaming queries using Qwen 2.5 7B Q8_0 model.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from app.core.rag import rag_stream_response, rag_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")
    max_tokens: Optional[int] = Field(2000, ge=100, le=4000, description="Max response tokens")
    stream: Optional[bool] = Field(True, description="Stream response")
    group_ids: Optional[List[str]] = Field(None, description="Filter by group IDs (multi-tenant)")
    use_reranking: Optional[bool] = Field(
        None, 
        description="Enable cross-encoder reranking (default: from settings). Expected +10-15% precision."
    )


class QueryResponse(BaseModel):
    """Response model for non-streaming query"""
    question: str
    answer: str
    num_sources: int
    context: dict
    reranked: bool = Field(False, description="True if cross-encoder reranking was applied")


@router.post("/", response_model=QueryResponse)
async def query_knowledge_graph(request: QueryRequest):
    """
    Query the knowledge graph (non-streaming)
    
    This endpoint retrieves relevant facts from the Graphiti knowledge graph
    (optionally reranked using cross-encoder) and generates a grounded answer
    using Qwen 2.5 7B Q8_0.
    
    Args:
        request: QueryRequest containing the question and parameters
        
    Returns:
        QueryResponse with the answer and context information
        
    Note:
        - If use_reranking=True: retrieves top_k × 4 facts, reranks to top_k
        - Cross-encoder: ms-marco-MiniLM-L-6-v2 (~100ms for 20 facts)
        - Expected +10-15% retrieval precision with reranking
    """
    try:
        logger.info(f"RAG query (non-streaming, reranking={'ON' if request.use_reranking else 'AUTO'}): {request.question[:50]}...")
        
        result = await rag_query(
            question=request.question,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            group_ids=request.group_ids,
            use_reranking=request.use_reranking
        )
        
        logger.info(f"RAG query complete: {result['num_sources']} sources used, reranked={result.get('reranked', False)}")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"RAG query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/stream")
async def query_knowledge_graph_stream(request: QueryRequest):
    """
    Query the knowledge graph (streaming)
    
    This endpoint provides real-time streaming of the LLM response using
    Server-Sent Events (SSE) protocol. Each token is sent as it's generated.
    Facts are retrieved from Graphiti (optionally reranked) before streaming.
    
    Args:
        request: QueryRequest containing the question and parameters
        
    Returns:
        StreamingResponse with SSE format
        
    Note:
        - If use_reranking=True: retrieves top_k × 4 facts, reranks to top_k
        - Cross-encoder: ms-marco-MiniLM-L-6-v2 (~100ms for 20 facts)
        - Expected +10-15% retrieval precision with reranking
    """
    try:
        logger.info(f"RAG stream query (reranking={'ON' if request.use_reranking else 'AUTO'}): {request.question[:50]}...")
        
        async def event_generator():
            """Generate SSE events"""
            try:
                async for token in rag_stream_response(
                    question=request.question,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    group_ids=request.group_ids,
                    use_reranking=request.use_reranking
                ):
                    # SSE format: data: {token}\n\n
                    yield f"data: {token}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}", exc_info=True)
                yield f"data: [ERROR: {str(e)}]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error(f"RAG stream setup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stream setup failed: {str(e)}")


@router.get("/health")
async def query_health():
    """
    Health check for query endpoint
    
    Verifies that the Ollama service and Qwen 2.5 7B Q8_0 model are available
    by attempting a simple test completion.
    
    Returns:
        Health status and model information
    """
    from app.core.llm import get_llm
    
    try:
        llm = get_llm()
        
        # Test simple completion
        response = ""
        async for token in llm.stream_completion(
            prompt="Test: What is 2+2?",
            temperature=0.1,
            max_tokens=50
        ):
            response += token
            if len(response) > 10:  # Early exit
                break
        
        return {
            "status": "healthy",
            "provider": "ollama",
            "model": getattr(llm, 'model', 'unknown'),
            "test_response": response[:50]
        }
        
    except Exception as e:
        logger.error(f"Query health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Query service unavailable: {str(e)}")
