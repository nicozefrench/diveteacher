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
from time import time

from app.core.config import settings
from app.core.logging_config import (
    get_context_logger,
    log_stage_start,
    log_stage_progress,
    log_stage_complete,
    log_error
)
from app.integrations.dockling import (
    convert_document_to_docling, 
    extract_document_metadata
)
from app.services.document_chunker import get_chunker  # ARIA production-validated pattern (RecursiveCharacterTextSplitter)
from app.integrations.graphiti import ingest_chunks_to_graph
from app.integrations.neo4j import neo4j_client
import sentry_sdk

logger = logging.getLogger('diveteacher.processor')

# In-memory status tracking (in production, use Redis or database)
processing_status: Dict[str, Dict[str, Any]] = {}


async def get_entity_count() -> int:
    """
    Query Neo4j for Entity node count
    
    Returns:
        Total number of Entity nodes in Neo4j
        
    Note:
        - Uses asyncio.to_thread for synchronous Neo4j driver
        - Returns 0 if query fails (graceful degradation)
    """
    try:
        # Run in thread pool (Neo4j driver is synchronous)
        def _query():
            with neo4j_client.driver.session() as session:
                result = session.run("MATCH (n:Entity) RETURN count(n) as count")
                record = result.single()
                return record["count"] if record else 0
        
        count = await asyncio.to_thread(_query)
        return count
    except Exception as e:
        logger.warning(f"⚠️  Failed to get entity count: {e}")
        return 0


async def get_relation_count() -> int:
    """
    Query Neo4j for RELATES_TO relationship count
    
    Returns:
        Total number of RELATES_TO relationships in Neo4j
        
    Note:
        - Uses asyncio.to_thread for synchronous Neo4j driver
        - Returns 0 if query fails (graceful degradation)
    """
    try:
        def _query():
            with neo4j_client.driver.session() as session:
                result = session.run(
                    "MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count"
                )
                record = result.single()
                return record["count"] if record else 0
        
        count = await asyncio.to_thread(_query)
        return count
    except Exception as e:
        logger.warning(f"⚠️  Failed to get relation count: {e}")
        return 0


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
    
    # Initialize status dict FIRST (before any exception)
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    file_size_mb = file_size / (1024 * 1024)
    
    processing_status[upload_id] = {
        "status": "processing",
        "stage": "initialization",
        "sub_stage": "starting",
        "progress": 0,
        "progress_detail": {
            "current": 0,
            "total": 4,
            "unit": "stages"
        },
        "error": None,
        "started_at": datetime.now().isoformat(),
        "metrics": {
            "file_size_mb": round(file_size_mb, 2),
            "filename": Path(file_path).name
        }
    }
    
    # Structured logging
    log_stage_start(
        logger,
        upload_id=upload_id,
        stage="initialization",
        details={
            "filename": Path(file_path).name,
            "file_size_mb": round(file_size_mb, 2),
            "metadata": metadata
        }
    )
    
    start_time = time()
    
    try:
        # STEP 1: Convert to DoclingDocument
        processing_status[upload_id].update({
            "stage": "conversion",
            "sub_stage": "docling_start",
            "progress": 10,
            "progress_detail": {
                "current": 1,
                "total": 4,
                "unit": "stages"
            }
        })
        
        log_stage_start(logger, upload_id, "conversion")
        conversion_start = time()
        
        docling_doc = await convert_document_to_docling(file_path, upload_id=upload_id)
        doc_metadata = extract_document_metadata(docling_doc)
        
        conversion_duration = time() - conversion_start
        
        log_stage_complete(
            logger,
            upload_id=upload_id,
            stage="conversion",
            duration=conversion_duration,
            metrics={
                "pages": len(docling_doc.pages) if hasattr(docling_doc, 'pages') else 0,
                "file_size_mb": round(file_size_mb, 2)
            }
        )
        
        processing_status[upload_id].update({
            "progress": 40,
            "sub_stage": "conversion_complete",
            "metrics": {
                **processing_status[upload_id].get("metrics", {}),
                "pages": len(docling_doc.pages) if hasattr(docling_doc, 'pages') else 0,
                "conversion_duration": round(conversion_duration, 2)
            }
        })
        
        # STEP 2: Semantic Chunking
        processing_status[upload_id].update({
            "stage": "chunking",
            "sub_stage": "tokenizing",
            "progress": 50,
            "progress_detail": {
                "current": 2,
                "total": 4,
                "unit": "stages"
            }
        })
        
        log_stage_start(logger, upload_id, "chunking")
        chunking_start = time()
        
        chunker = get_chunker()
        chunks = chunker.chunk_document(
            docling_doc=docling_doc,
            filename=Path(file_path).name,
            upload_id=upload_id
        )
        
        chunking_duration = time() - chunking_start
        # Chunks are dicts with "text" key, not objects with .content attribute
        avg_chunk_size = sum(len(c["text"]) for c in chunks) / len(chunks) if chunks else 0
        total_tokens = sum(c.get("metadata", {}).get("num_tokens", 0) for c in chunks)
        
        log_stage_complete(
            logger,
            upload_id=upload_id,
            stage="chunking",
            duration=chunking_duration,
            metrics={
                "num_chunks": len(chunks),
                "avg_chunk_size": round(avg_chunk_size, 0),
                "total_tokens": total_tokens
            }
        )
        
        processing_status[upload_id].update({
            "progress": 70,
            "sub_stage": "chunking_complete",
            "metrics": {
                **processing_status[upload_id].get("metrics", {}),
                "num_chunks": len(chunks),
                "avg_chunk_size": round(avg_chunk_size, 0),
                "chunking_duration": round(chunking_duration, 2)
            }
        })
        
        # STEP 3: Ingest to Knowledge Graph
        processing_status[upload_id].update({
            "stage": "ingestion",
            "sub_stage": "graphiti_start",
            "progress": 75,
            "progress_detail": {
                "current": 3,
                "total": 4,
                "unit": "stages"
            },
            "ingestion_progress": {
                "chunks_completed": 0,
                "chunks_total": len(chunks),
                "progress_pct": 0,
                "current_chunk_index": 0,
            }
        })
        
        log_stage_start(
            logger,
            upload_id,
            "ingestion",
            details={"num_chunks": len(chunks)}
        )
        ingestion_start = time()
        
        # Enriched metadata
        enriched_metadata = {
            "filename": Path(file_path).name,
            "upload_id": upload_id,
            "processed_at": datetime.now().isoformat(),
            "num_chunks": len(chunks),
            **doc_metadata,
            **(metadata or {})
        }
        
        # 🔧 Pass processing_status for real-time updates
        await ingest_chunks_to_graph(
            chunks=chunks,
            metadata=enriched_metadata,
            upload_id=upload_id,
            processing_status=processing_status  # ← ADD THIS
        )
        
        ingestion_duration = time() - ingestion_start
        
        log_stage_complete(
            logger,
            upload_id=upload_id,
            stage="ingestion",
            duration=ingestion_duration,
            metrics={
                "chunks_processed": len(chunks)
            }
        )
        
        # 🔧 QUERY NEO4J FOR ENTITY/RELATION COUNTS (Bug #10 Fix)
        logger.info(f"📊 Querying Neo4j for entity/relation counts...", extra={'upload_id': upload_id})
        entity_count = await get_entity_count()
        relation_count = await get_relation_count()
        logger.info(
            f"✅ Neo4j counts: {entity_count} entities, {relation_count} relations",
            extra={
                'upload_id': upload_id,
                'entities': entity_count,
                'relations': relation_count
            }
        )
        
        processing_status[upload_id].update({
            "progress": 95,
            "sub_stage": "ingestion_complete",
            "metrics": {
                **processing_status[upload_id].get("metrics", {}),
                "ingestion_duration": round(ingestion_duration, 2),
                "entities": entity_count,      # ← ADD
                "relations": relation_count,    # ← ADD
            }
        })
        
        # STEP 4: Finalize and complete
        total_duration = time() - start_time
        
        # Ensure metadata is JSON-serializable
        safe_metadata = {}
        for key, value in doc_metadata.items():
            if isinstance(value, datetime):
                safe_metadata[key] = value.isoformat()
            elif callable(value):
                continue
            else:
                safe_metadata[key] = value
        
        processing_status[upload_id].update({
            "status": "completed",
            "stage": "completed",
            "sub_stage": "finalized",
            "progress": 100,
            "progress_detail": {
                "current": 4,
                "total": 4,
                "unit": "stages"
            },
            "metadata": safe_metadata,
            "durations": {
                "conversion": round(conversion_duration, 2),
                "chunking": round(chunking_duration, 2),
                "ingestion": round(ingestion_duration, 2),
                "total": round(total_duration, 2)
            },
            "completed_at": datetime.now().isoformat(),
        })
        
        logger.info(
            f"✅ Processing complete",
            extra={
                'upload_id': upload_id,
                'stage': 'completed',
                'duration': round(total_duration, 2),
                'metrics': {
                    'total_duration': round(total_duration, 2),
                    'conversion_duration': round(conversion_duration, 2),
                    'chunking_duration': round(chunking_duration, 2),
                    'ingestion_duration': round(ingestion_duration, 2),
                    'num_chunks': len(chunks),
                    'pages': len(docling_doc.pages) if hasattr(docling_doc, 'pages') else 0
                }
            }
        )
        
    except ValueError as e:
        log_error(logger, upload_id, "validation", e)
        sentry_sdk.capture_exception(e)
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "validation_error",
            "sub_stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat(),
        })
        raise
        
    except TimeoutError as e:
        log_error(logger, upload_id, "conversion", e)
        sentry_sdk.capture_exception(e)
        processing_status[upload_id].update({
            "status": "failed",
            "stage": "timeout_error",
            "sub_stage": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat(),
        })
        raise
        
    except Exception as e:
        log_error(logger, upload_id, processing_status[upload_id].get("stage", "unknown"), e)
        sentry_sdk.capture_exception(e)
        
        if upload_id in processing_status:
            processing_status[upload_id].update({
                "status": "failed",
                "stage": "unknown_error",
                "sub_stage": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "failed_at": datetime.now().isoformat(),
            })
    
    finally:
        status = processing_status.get(upload_id, {}).get("status", "unknown")
        logger.info(
            f"Processing finished: {status}",
            extra={
                'upload_id': upload_id,
                'stage': 'finalized',
                'final_status': status
            }
        )


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
