"""
File Upload Endpoint - ARIA Pattern (asyncio.create_task)
"""

import os
import uuid
import asyncio
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.processor import process_document, get_processing_status

router = APIRouter()
logger = logging.getLogger('diveteacher.upload')

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


@router.get("/upload/status/{upload_id}")
async def get_upload_status(upload_id: str):
    """
    Get processing status for uploaded document
    
    Args:
        upload_id: Upload identifier
        
    Returns:
        Processing status
    """
    
    status = get_processing_status(upload_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Upload ID not found: {upload_id}"
        )
    
    return JSONResponse(content=status)
