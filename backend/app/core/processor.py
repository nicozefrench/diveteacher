"""
Document Processing Pipeline

Pipeline complet:
1. Validation
2. Conversion Docling → DoclingDocument
3. Chunking sémantique (HybridChunker)
4. Ingestion Neo4j (Graphiti)
"""
import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.integrations.dockling import (
    convert_document_to_docling, 
    extract_document_metadata
)
from app.services.document_chunker import get_chunker
from app.integrations.graphiti import ingest_chunks_to_graph
from app.integrations.neo4j import neo4j_client
import sentry_sdk

logger = logging.getLogger('diveteacher.processor')

# In-memory status tracking (in production, use Redis or database)
processing_status: Dict[str, Dict[str, Any]] = {}


async def process_document(
    file_path: str, 
    upload_id: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Process uploaded document through the complete pipeline
    
    Steps:
    1. Validate (dans convert_document_to_docling)
    2. Convert to DoclingDocument (Docling)
    3. Chunk semantically (HybridChunker)
    4. Ingest to knowledge graph (Graphiti + Neo4j)
    5. Update status & cleanup
    
    Args:
        file_path: Path to uploaded file
        upload_id: Unique upload identifier
        metadata: Optional document metadata
    """
    
    logger.info(f"[{upload_id}] ═══════════════════════════════════════")
    logger.info(f"[{upload_id}] Starting document processing")
    logger.info(f"[{upload_id}] File: {Path(file_path).name}")
    start_time = datetime.now()
    
    try:
        # Initialize status
        processing_status[upload_id] = {
            "status": "processing",
            "stage": "validation",
            "progress": 0,
            "error": None,
            "started_at": datetime.now().isoformat(),
        }
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Convert to DoclingDocument
        # ═══════════════════════════════════════════════════════════
        processing_status[upload_id]["stage"] = "conversion"
        processing_status[upload_id]["progress"] = 10
        
        logger.info(f"[{upload_id}] Step 1/4: Docling conversion")
        
        docling_doc = await convert_document_to_docling(file_path)
        doc_metadata = extract_document_metadata(docling_doc)
        
        conversion_duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{upload_id}] ✅ Conversion: {conversion_duration:.2f}s")
        
        processing_status[upload_id]["progress"] = 40
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Semantic Chunking avec HybridChunker
        # ═══════════════════════════════════════════════════════════
        processing_status[upload_id]["stage"] = "chunking"
        processing_status[upload_id]["progress"] = 50
        
        logger.info(f"[{upload_id}] Step 2/4: Semantic chunking")
        
        chunker = get_chunker()
        chunks = chunker.chunk_document(
            docling_doc=docling_doc,
            filename=Path(file_path).name,
            upload_id=upload_id
        )
        
        chunking_duration = (datetime.now() - start_time).total_seconds() - conversion_duration
        logger.info(f"[{upload_id}] ✅ Chunking: {chunking_duration:.2f}s ({len(chunks)} chunks)")
        
        processing_status[upload_id]["progress"] = 70
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Ingest chunks to knowledge graph
        # ═══════════════════════════════════════════════════════════
        processing_status[upload_id]["stage"] = "ingestion"
        processing_status[upload_id]["progress"] = 75
        
        logger.info(f"[{upload_id}] Step 3/4: Neo4j ingestion")
        
        # Métadonnées enrichies
        enriched_metadata = {
            "filename": Path(file_path).name,
            "upload_id": upload_id,
            "processed_at": datetime.now().isoformat(),
            "num_chunks": len(chunks),
            **doc_metadata,
            **(metadata or {})
        }
        
        await ingest_chunks_to_graph(
            chunks=chunks,
            metadata=enriched_metadata
        )
        
        ingestion_duration = (datetime.now() - start_time).total_seconds() - conversion_duration - chunking_duration
        logger.info(f"[{upload_id}] ✅ Ingestion: {ingestion_duration:.2f}s")
        
        processing_status[upload_id]["progress"] = 95
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: Cleanup & Mark complete
        # ═══════════════════════════════════════════════════════════
        logger.info(f"[{upload_id}] Step 4/4: Cleanup")
        
        # Optionnel: Supprimer fichier après ingestion réussie
        # os.remove(file_path)
        # logger.info(f"[{upload_id}] Deleted temporary file")
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        processing_status[upload_id].update({
            "status": "completed",
            "stage": "completed",
            "progress": 100,
            "num_chunks": len(chunks),
            "metadata": doc_metadata,
            "durations": {
                "conversion": round(conversion_duration, 2),
                "chunking": round(chunking_duration, 2),
                "ingestion": round(ingestion_duration, 2),
                "total": round(total_duration, 2)
            },
            "completed_at": datetime.now().isoformat(),
        })
        
        logger.info(f"[{upload_id}] ✅ Processing COMPLETE ({total_duration:.2f}s)")
        logger.info(f"[{upload_id}] ═══════════════════════════════════════")
        
    except ValueError as e:
        # Validation error
        logger.error(f"[{upload_id}] ❌ Validation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "validation_error",
            "error": str(e),
            "failed_at": datetime.now().isoformat(),
        })
        raise
        
    except TimeoutError as e:
        # Conversion timeout
        logger.error(f"[{upload_id}] ❌ Timeout error: {str(e)}")
        sentry_sdk.capture_exception(e)
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "timeout_error",
            "error": str(e),
            "failed_at": datetime.now().isoformat(),
        })
        raise
        
    except Exception as e:
        # Unexpected error
        logger.error(f"[{upload_id}] ❌ Unexpected error: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "unknown_error",
            "error": str(e),
            "failed_at": datetime.now().isoformat(),
        })
        raise


def get_processing_status(upload_id: str) -> Optional[Dict[str, Any]]:
    """Get processing status for a document"""
    return processing_status.get(upload_id)


async def cleanup_old_status(max_age_hours: int = 24):
    """Cleanup old processing status entries"""
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    to_delete = []
    for upload_id, status in processing_status.items():
        started_at = datetime.fromisoformat(status.get("started_at", ""))
        if started_at < cutoff:
            to_delete.append(upload_id)
    
    for upload_id in to_delete:
        del processing_status[upload_id]
    
    logger.info(f"Cleaned up {len(to_delete)} old status entries")
