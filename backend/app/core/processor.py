"""
Document Processing Pipeline

Handles:
1. PDF/PPT → Markdown conversion (Dockling)
2. Markdown → Knowledge Graph ingestion (Graphiti + Neo4j)
3. Status tracking
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.integrations.dockling import convert_document_to_markdown
from app.integrations.graphiti import ingest_document_to_graph
from app.integrations.neo4j import neo4j_client
import sentry_sdk


# In-memory status tracking (in production, use Redis or database)
processing_status: Dict[str, Dict[str, Any]] = {}


async def process_document(
    file_path: str, 
    upload_id: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Process uploaded document through the pipeline
    
    Steps:
    1. Convert to markdown (Dockling)
    2. Ingest to knowledge graph (Graphiti + Neo4j)
    3. Update status
    
    Args:
        file_path: Path to uploaded file
        upload_id: Unique upload identifier
        metadata: Optional document metadata
    """
    
    try:
        # Initialize status
        processing_status[upload_id] = {
            "status": "processing",
            "stage": "conversion",
            "progress": 0,
            "error": None,
            "started_at": datetime.utcnow().isoformat(),
        }
        
        # Step 1: Convert to markdown
        processing_status[upload_id]["stage"] = "conversion"
        processing_status[upload_id]["progress"] = 10
        
        markdown_content = await convert_document_to_markdown(file_path)
        
        processing_status[upload_id]["progress"] = 50
        
        # Step 2: Ingest to knowledge graph
        processing_status[upload_id]["stage"] = "ingestion"
        processing_status[upload_id]["progress"] = 60
        
        # Extract metadata
        file_name = Path(file_path).name
        doc_metadata = {
            "filename": file_name,
            "upload_id": upload_id,
            "processed_at": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        await ingest_document_to_graph(
            markdown_content=markdown_content,
            metadata=doc_metadata
        )
        
        processing_status[upload_id]["progress"] = 90
        
        # Step 3: Mark as completed
        processing_status[upload_id].update({
            "status": "completed",
            "stage": "completed",
            "progress": 100,
            "completed_at": datetime.utcnow().isoformat(),
        })
        
    except Exception as e:
        # Capture exception in Sentry
        sentry_sdk.capture_exception(e)
        
        # Update status
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "error",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        })
        
        raise


def get_processing_status(upload_id: str) -> Optional[Dict[str, Any]]:
    """
    Get processing status for a document
    
    Args:
        upload_id: Upload identifier
        
    Returns:
        Status dictionary or None if not found
    """
    return processing_status.get(upload_id)


async def cleanup_old_status(max_age_hours: int = 24):
    """
    Cleanup old processing status entries
    
    Args:
        max_age_hours: Maximum age in hours before cleanup
    """
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
    
    to_delete = []
    for upload_id, status in processing_status.items():
        started_at = datetime.fromisoformat(status.get("started_at", ""))
        if started_at < cutoff:
            to_delete.append(upload_id)
    
    for upload_id in to_delete:
        del processing_status[upload_id]

