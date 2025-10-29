"""
File Upload Endpoint - ARIA Pattern (asyncio.create_task)
"""

import os
import uuid
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.processor import process_document, get_processing_status

router = APIRouter()
logger = logging.getLogger('diveteacher.upload')


# ════════════════════════════════════════════════════════
# Pydantic Models for Enhanced Status API
# ════════════════════════════════════════════════════════

class IngestionProgress(BaseModel):
    """Real-time ingestion progress (Bug #9 Fix)"""
    chunks_completed: int
    chunks_total: int
    progress_pct: int
    current_chunk_index: int


class ProcessingMetrics(BaseModel):
    """Processing metrics"""
    file_size_mb: Optional[float] = None
    filename: Optional[str] = None
    pages: Optional[int] = None
    conversion_duration: Optional[float] = None
    num_chunks: Optional[int] = None
    avg_chunk_size: Optional[float] = None
    chunking_duration: Optional[float] = None
    ingestion_duration: Optional[float] = None
    entities: Optional[int] = None       # ← Bug #10 Fix
    relations: Optional[int] = None      # ← Bug #10 Fix


class UploadStatusResponse(BaseModel):
    """Enhanced upload status response"""
    status: str  # "processing", "completed", "failed"
    stage: str   # "validation", "conversion", "chunking", "ingestion", "completed"
    sub_stage: str
    progress: int  # 0-100
    progress_detail: Optional[Dict[str, Any]] = None
    ingestion_progress: Optional[IngestionProgress] = None  # ← Bug #9 Fix
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    metrics: Optional[ProcessingMetrics] = None
    durations: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

# ❌ REMOVED: ThreadPoolExecutor
# from concurrent.futures import ThreadPoolExecutor
# _thread_pool = ThreadPoolExecutor(max_workers=4)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload document for processing
    
    Uses asyncio.create_task() for background processing (ARIA pattern).
    Zero threading - single event loop.
    
    Args:
        file: Uploaded file (PDF, PPT, etc.)
        
    Returns:
        Upload ID and status
    """
    
    logger.info("=" * 60)
    logger.info(f"📤 UPLOAD START: {file.filename}")
    print(f"\n{'='*60}")
    print(f"📤 UPLOAD START: {file.filename}")
    print(f"{'='*60}\n", flush=True)
    
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lstrip(".")
        allowed_extensions = settings.ALLOWED_EXTENSIONS.split(",")
        
        if file_ext.lower() not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
            )
        
        logger.info(f"✅ File extension validated: {file_ext}")
        
        # Validate file size (read in chunks to avoid memory issues)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes
        total_size = 0
        chunks = []
        
        # Read file
        chunk_size = 8192
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
                )
            chunks.append(chunk)
        
        logger.info(f"✅ File read: {total_size} bytes ({len(chunks)} chunks)")
        
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        logger.info(f"✅ Generated upload_id: {upload_id}")
        
        # Save file to upload directory
        file_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{file.filename}")
        
        async with aiofiles.open(file_path, "wb") as f:
            for chunk in chunks:
                await f.write(chunk)
        
        logger.info(f"✅ File saved to: {file_path}")
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "size_bytes": total_size,
            "content_type": file.content_type,
        }
        
        # ═══════════════════════════════════════════════════════════
        # 🔧 FIX: Initialize status BEFORE creating background task
        # This ensures status endpoint returns 200 immediately
        # ═══════════════════════════════════════════════════════════
        from app.core.processor import processing_status
        from datetime import datetime
        
        print(f"[{upload_id}] Initializing status dict...", flush=True)
        
        # Pre-initialize status to prevent 404
        processing_status[upload_id] = {
            "status": "processing",
            "stage": "queued",
            "sub_stage": "initializing",
            "progress": 0,
            "progress_detail": {
                "current": 0,
                "total": 4,
                "unit": "stages"
            },
            "error": None,
            "started_at": datetime.now().isoformat(),
            "metrics": {
                "file_size_mb": round(total_size / (1024 * 1024), 2),
                "filename": file.filename
            }
        }
        
        logger.info(f"[{upload_id}] ✅ Status dict initialized (pre-processing)")
        print(f"[{upload_id}] ✅ Status initialized in processing_status dict", flush=True)
        
        # ═══════════════════════════════════════════════════════════
        # ✅ NEW APPROACH: asyncio.create_task() (ARIA pattern)
        # ═══════════════════════════════════════════════════════════
        print(f"[{upload_id}] Creating async background task...", flush=True)
        
        # Create background task in SAME event loop
        asyncio.create_task(
            process_document_wrapper(
                file_path=file_path,
                upload_id=upload_id,
                metadata=metadata
            )
        )
        
        print(f"[{upload_id}] ✅ Processing task created (async)", flush=True)
        logger.info(f"[{upload_id}] ✅ Background processing task created")
        
        return JSONResponse(content={
            "upload_id": upload_id,
            "filename": file.filename,
            "status": "processing",
            "message": "Document uploaded successfully and processing started"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_wrapper(file_path: str, upload_id: str, metadata: dict):
    """
    Wrapper for process_document() to handle errors gracefully.
    
    Runs in same event loop as FastAPI (no threading).
    This allows long-running processing without blocking the API.
    
    Args:
        file_path: Path to uploaded file
        upload_id: Unique upload identifier
        metadata: File metadata
    """
    try:
        print(f"[{upload_id}] 🚀 Starting background processing (async wrapper)...", flush=True)
        logger.info(f"[{upload_id}] Background processing wrapper started")
        
        print(f"[{upload_id}] 🔍 DEBUG: About to call process_document()...", flush=True)
        print(f"[{upload_id}] 🔍 DEBUG: file_path={file_path}", flush=True)
        print(f"[{upload_id}] 🔍 DEBUG: upload_id={upload_id}", flush=True)
        print(f"[{upload_id}] 🔍 DEBUG: metadata={metadata}", flush=True)
        
        # Call process_document (already async)
        await process_document(
            file_path=file_path,
            upload_id=upload_id,
            metadata=metadata
        )
        
        print(f"[{upload_id}] ✅ Background processing complete", flush=True)
        logger.info(f"[{upload_id}] ✅ Background processing complete")
        
    except Exception as e:
        print(f"[{upload_id}] ❌ Background processing error: {e}", flush=True)
        logger.error(f"[{upload_id}] ❌ Background processing error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        
        # Error is already captured in process_document status dict
        # No need to re-raise (background task completes gracefully)


def _sanitize_for_json(obj):
    """
    Recursively sanitize object for JSON serialization.
    
    Handles:
    - datetime objects → isoformat()
    - method/function objects → string representation
    - custom objects → string representation
    - nested dicts and lists
    
    Args:
        obj: Object to sanitize
        
    Returns:
        JSON-serializable version of obj
    """
    from datetime import datetime, date
    
    if obj is None or isinstance(obj, (str, int, float, bool)):
        # Primitive types are already JSON-serializable
        return obj
    
    elif isinstance(obj, (datetime, date)):
        # Convert datetime to ISO format string
        return obj.isoformat()
    
    elif isinstance(obj, dict):
        # Recursively sanitize dict values
        return {key: _sanitize_for_json(value) for key, value in obj.items()}
    
    elif isinstance(obj, (list, tuple)):
        # Recursively sanitize list/tuple items
        return [_sanitize_for_json(item) for item in obj]
    
    elif callable(obj):
        # Methods, functions, lambdas → string representation
        return f"<{obj.__class__.__name__}: {obj.__name__ if hasattr(obj, '__name__') else 'anonymous'}>"
    
    else:
        # For any other object type, try str() or repr()
        try:
            return str(obj)
        except Exception:
            return f"<{obj.__class__.__name__}>"


@router.get("/upload/{upload_id}/status", response_model=None)
async def get_upload_status(upload_id: str):
    """
    Get processing status for uploaded document (Enhanced with real-time progress)
    
    Args:
        upload_id: Upload identifier
        
    Returns:
        Processing status with real-time ingestion_progress, entity/relation counts
        
    Status Structure:
        - status: "processing" | "completed" | "failed"
        - stage: Current processing stage
        - sub_stage: Current sub-stage within stage
        - progress: Overall progress percentage (0-100)
        - progress_detail: {current, total, unit}
        - ingestion_progress: Real-time chunk progress (Bug #9 Fix)
        - metrics: Stage-specific metrics including entities/relations (Bug #10 Fix)
        - durations: Time spent in each stage
        - started_at, completed_at/failed_at: Timestamps
    """
    
    status = get_processing_status(upload_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Upload ID not found: {upload_id}"
        )
    
    # Sanitize status dict to ensure JSON serializability
    sanitized_status = _sanitize_for_json(status)
    
    # Pre-serialize to JSON to ensure no errors
    import json as json_module
    from starlette.responses import Response
    
    try:
        json_str = json_module.dumps(sanitized_status, indent=2)
        return Response(content=json_str, media_type="application/json")
    except Exception as e:
        logger.error(f"[{upload_id}] ❌ Status serialization failed: {e}")
        return JSONResponse(content={
            "error": "Status serialization failed",
            "upload_id": upload_id,
            "details": str(e)
        }, status_code=500)


@router.get("/upload/{upload_id}/logs")
async def get_upload_logs(
    upload_id: str,
    limit: int = 100,
    level: str = "INFO"
):
    """
    Get structured logs for a specific upload
    
    Args:
        upload_id: Upload identifier
        limit: Maximum number of log entries to return (default: 100)
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        List of log entries with timestamps, levels, stages, and metrics
        
    Note:
        This endpoint reads from structured JSON logs.
        In production, this would query a centralized logging system (e.g., ELK, Datadog).
        For MVP, we return logs from memory (if available).
    """
    
    # Check if upload exists
    status = get_processing_status(upload_id)
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Upload ID not found: {upload_id}"
        )
    
    # 🔧 FIX: Return accurate status from processing_status dict
    # Don't hardcode "failed" when still processing
    current_status = status.get("status", "unknown")
    current_stage = status.get("stage", "unknown")
    sub_stage = status.get("sub_stage", "")
    
    # Build log entries from status information
    logs = [
        {
            "timestamp": status.get("started_at"),
            "level": "INFO",
            "stage": "initialization",
            "message": "Processing started"
        }
    ]
    
    # Add current stage info if processing
    if current_status == "processing" and current_stage != "initialization":
        logs.append({
            "timestamp": status.get("started_at"),  # Would be stage start time in prod
            "level": "INFO",
            "stage": current_stage,
            "sub_stage": sub_stage,
            "message": f"Currently processing: {current_stage}"
        })
    
    # Add completion/error log if done
    if current_status == "completed":
        logs.append({
            "timestamp": status.get("completed_at"),
            "level": "INFO",
            "stage": "completed",
            "message": "Processing completed successfully"
        })
    elif current_status == "failed":
        logs.append({
            "timestamp": status.get("failed_at"),
            "level": "ERROR",
            "stage": "error",
            "message": status.get("error", "Processing failed")
        })
    
    # TODO: In production, query centralized logging system
    # For MVP, return logs built from status dict
    return JSONResponse(content={
        "upload_id": upload_id,
        "logs": logs,
        "note": "Full log streaming requires centralized logging setup (Phase 2)",
        "status": current_status,  # Use actual status, not hardcoded "failed"
        "current_stage": current_stage,
        "sub_stage": sub_stage,
        "progress": status.get("progress", 0)
    })
