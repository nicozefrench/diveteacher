"""
Health Check Endpoint
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

from app.integrations.neo4j import neo4j_client
from app.core.llm import get_llm
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Service health status
    """

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }

    # Check Neo4j
    try:
        await neo4j_client.verify_connection()
        health_status["services"]["neo4j"] = "connected"
    except Exception as e:
        health_status["services"]["neo4j"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check LLM provider
    try:
        get_llm()
        health_status["services"]["llm"] = {
            "provider": settings.LLM_PROVIDER,
            "status": "configured"
        }
    except Exception as e:
        health_status["services"]["llm"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return JSONResponse(content=health_status)

