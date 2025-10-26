"""
File Upload Endpoint
"""

import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.processor import process_document, get_processing_status

router = APIRouter()


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload document for processing
    
    Args:
        file: Uploaded file (PDF, PPT, etc.)
        
    Returns:
        Upload ID and status
    """
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lstrip(".")
    allowed_extensions = settings.ALLOWED_EXTENSIONS.split(",")
    
    if file_ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (read in chunks to avoid memory issues)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes
    total_size = 0
    chunks = []
    
    async for chunk in file.file:
        total_size += len(chunk)
        if total_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        chunks.append(chunk)
    
    # Generate unique upload ID
    upload_id = str(uuid.uuid4())
    
    # Save file to upload directory
    file_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{file.filename}")
    
    async with aiofiles.open(file_path, "wb") as f:
        for chunk in chunks:
            await f.write(chunk)
    
    # Start background processing
    metadata = {
        "filename": file.filename,
        "size_bytes": total_size,
        "content_type": file.content_type,
    }
    
    background_tasks.add_task(
        process_document, 
        file_path=file_path, 
        upload_id=upload_id,
        metadata=metadata
    )
    
    return JSONResponse(content={
        "upload_id": upload_id,
        "filename": file.filename,
        "status": "processing",
        "message": "Document uploaded successfully and processing started"
    })


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

