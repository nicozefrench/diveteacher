"""
FastAPI Backend for RAG Knowledge Graph Application

This is the main entry point for the backend API server.
It sets up:
- FastAPI application
- CORS middleware
- Sentry monitoring
- API routes
- Background tasks
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.core.config import settings
from app.api import upload, query, health, graph
from app.integrations.neo4j import neo4j_client
from app.integrations.sentry import init_sentry

# Initialize Sentry (if configured)
if settings.SENTRY_DSN_BACKEND:
    init_sentry()

# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Graph API",
    description="Backend API for document upload, processing, and intelligent Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(graph.router, prefix="/api", tags=["Graph"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting RAG Knowledge Graph API...")
    
    # Test Neo4j connection
    try:
        await neo4j_client.verify_connection()
        print("✅ Neo4j connection established")
    except Exception as e:
        print(f"⚠️  Neo4j connection failed: {e}")
        # Don't crash - let health check report the issue
    
    print("✅ API server ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down RAG Knowledge Graph API...")
    await neo4j_client.close()
    print("✅ Cleanup complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RAG Knowledge Graph API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with Sentry integration"""
    if settings.SENTRY_DSN_BACKEND:
        sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )

