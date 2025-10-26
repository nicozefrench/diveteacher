"""
RAG Query Endpoint (Streaming)
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.core.rag import rag_stream_response
from app.core.config import settings

router = APIRouter()


@router.post("/query")
async def rag_query_stream(
    question: str,
    temperature: Optional[float] = Query(default=0.7, ge=0.0, le=1.0),
    max_tokens: Optional[int] = Query(default=2000, ge=100, le=4000)
):
    """
    Query the knowledge graph with RAG (streaming response)
    
    Args:
        question: User's question
        temperature: LLM sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Server-Sent Events (SSE) stream of response tokens
    """
    
    async def event_generator():
        """Generate Server-Sent Events for streaming response"""
        try:
            # Send start event
            yield f"data: {json.dumps({'type': 'start'})}\n\n"
            
            # Stream response tokens
            async for token in rag_stream_response(
                question=question,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            
            # Send end event
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            # Send error event
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in Nginx
        }
    )

