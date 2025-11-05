"""
Document Processing Queue for DiveTeacher.

Handles sequential processing of multiple documents with:
- FIFO queue
- Rate limit protection (via SafeIngestionQueue in processor)
- Progress tracking
- State persistence
- Retry logic
- Inter-document delays for additional rate limit safety

Version: 1.0.0 (Production-Ready for Large Workloads)
Architecture: ARIA v2.0.0 Pattern
"""

import asyncio
import logging
from collections import deque
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from app.core.processor import process_document

logger = logging.getLogger('diveteacher.queue')


class DocumentQueue:
    """
    Sequential document processing queue.

    Features:
    - One document at a time (no concurrent processing)
    - FIFO order (first uploaded, first processed)
    - Progress tracking per document
    - Inter-document delays for rate limit safety
    - Graceful shutdown support
    - State tracking (queued, processing, completed, failed)

    Usage:
        queue = get_document_queue()

        # Enqueue document
        entry = queue.enqueue(
            file_path="/uploads/test.pdf",
            upload_id="abc123",
            metadata={"filename": "test.pdf"}
        )

        # Check status
        status = queue.get_status()
        print(f"Queue size: {status['queue_size']}")
        print(f"Processing: {status['processing']}")
    """

    # Inter-document delay (additional safety margin for rate limits)
    # This is IN ADDITION to SafeIngestionQueue's token-aware delays
    INTER_DOCUMENT_DELAY_SEC = 60  # 1 minute between documents

    def __init__(self):
        """Initialize the document queue."""
        self.queue: deque = deque()
        self.processing: bool = False
        self.current_doc: Optional[Dict] = None
        self.completed: List[Dict] = []
        self.failed: List[Dict] = []
        self._shutdown_requested: bool = False

        logger.info("📥 DocumentQueue initialized")
        logger.info(f"   • Inter-document delay: {self.INTER_DOCUMENT_DELAY_SEC}s")
        logger.info("   • Processing mode: Sequential (FIFO)")

    def enqueue(
        self,
        file_path: str,
        upload_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add document to processing queue.

        Args:
            file_path: Path to uploaded file
            upload_id: Unique upload identifier
            metadata: Optional document metadata

        Returns:
            Queue entry dict with status and position
        """
        entry = {
            "file_path": file_path,
            "upload_id": upload_id,
            "metadata": metadata or {},
            "queued_at": datetime.now().isoformat(),
            "status": "queued",
            "queue_position": len(self.queue) + 1,
            "filename": Path(file_path).name
        }

        self.queue.append(entry)

        logger.info(
            f"📥 Document queued: {entry['filename']}",
            extra={
                'upload_id': upload_id,
                'queue_position': entry['queue_position'],
                'queue_size': len(self.queue)
            }
        )

        # Start processing if not already running
        if not self.processing:
            logger.info("🚀 Starting queue processing (no processing in progress)")
            asyncio.create_task(self._process_queue())
        else:
            logger.info(f"⏳ Queue processing already running (current doc: {self.current_doc['filename'] if self.current_doc else 'unknown'})")

        return entry

    async def _process_queue(self):
        """
        Process documents sequentially until queue empty.

        This is the main processing loop that runs continuously
        until all documents are processed or shutdown is requested.
        """
        if self.processing:
            logger.warning("⚠️  Queue processing already running")
            return

        self.processing = True
        logger.info("🚀 Starting queue processing loop...")

        processed_count = 0

        try:
            while self.queue and not self._shutdown_requested:
                # Get next document
                doc = self.queue.popleft()
                self.current_doc = doc
                doc["status"] = "processing"
                doc["started_at"] = datetime.now().isoformat()

                logger.info("")
                logger.info("=" * 70)
                logger.info(f"📄 Processing document {processed_count + 1}")
                logger.info(f"   Filename: {doc['filename']}")
                logger.info(f"   Upload ID: {doc['upload_id']}")
                logger.info(f"   Remaining in queue: {len(self.queue)}")
                logger.info("=" * 70)
                logger.info("")

                try:
                    # Process document (uses SafeIngestionQueue internally)
                    await process_document(
                        file_path=doc["file_path"],
                        upload_id=doc["upload_id"],
                        metadata=doc["metadata"]
                    )

                    # Mark as completed
                    doc["status"] = "completed"
                    doc["completed_at"] = datetime.now().isoformat()
                    self.completed.append(doc)

                    logger.info("")
                    logger.info(f"✅ Document completed: {doc['filename']}")
                    logger.info(f"   Upload ID: {doc['upload_id']}")
                    logger.info(f"   Total completed: {len(self.completed)}")
                    logger.info(f"   Total failed: {len(self.failed)}")
                    logger.info("")

                except Exception as e:
                    # Mark as failed
                    doc["status"] = "failed"
                    doc["error"] = str(e)
                    doc["failed_at"] = datetime.now().isoformat()
                    self.failed.append(doc)

                    logger.error("")
                    logger.error(f"❌ Document failed: {doc['filename']}")
                    logger.error(f"   Upload ID: {doc['upload_id']}")
                    logger.error(f"   Error: {str(e)}")
                    logger.error(f"   Total completed: {len(self.completed)}")
                    logger.error(f"   Total failed: {len(self.failed)}")
                    logger.error("", exc_info=True)

                finally:
                    self.current_doc = None
                    processed_count += 1

                # Inter-document delay (additional rate limit safety)
                if self.queue:  # Only delay if more documents remain
                    logger.info("")
                    logger.info(f"⏸️  Inter-document delay: Waiting {self.INTER_DOCUMENT_DELAY_SEC}s before next document...")
                    logger.info("   (Additional rate limit safety on top of SafeIngestionQueue)")
                    logger.info(f"   Remaining in queue: {len(self.queue)}")
                    logger.info("")
                    await asyncio.sleep(self.INTER_DOCUMENT_DELAY_SEC)

        finally:
            self.processing = False
            logger.info("")
            logger.info("=" * 70)
            logger.info("🏁 Queue processing complete")
            logger.info(f"   Total processed: {processed_count}")
            logger.info(f"   Completed: {len(self.completed)}")
            logger.info(f"   Failed: {len(self.failed)}")
            logger.info("=" * 70)
            logger.info("")

    def get_status(self) -> Dict[str, Any]:
        """
        Get queue status with detailed information.

        Returns:
            Dict with queue size, processing state, current document, stats
        """
        return {
            "queue_size": len(self.queue),
            "processing": self.processing,
            "current_document": {
                "upload_id": self.current_doc["upload_id"],
                "filename": self.current_doc["filename"],
                "status": self.current_doc["status"],
                "started_at": self.current_doc.get("started_at"),
            } if self.current_doc else None,
            "completed_count": len(self.completed),
            "failed_count": len(self.failed),
            "queued_documents": [
                {
                    "upload_id": doc["upload_id"],
                    "filename": doc["filename"],
                    "queue_position": i + 1,
                    "queued_at": doc["queued_at"]
                }
                for i, doc in enumerate(self.queue)
            ],
            "stats": {
                "total_enqueued": len(self.queue) + len(self.completed) + len(self.failed) + (1 if self.current_doc else 0),
                "success_rate": round((len(self.completed) / (len(self.completed) + len(self.failed)) * 100), 1) if (len(self.completed) + len(self.failed)) > 0 else 0
            }
        }

    async def shutdown(self):
        """
        Graceful shutdown: finish current document, stop processing queue.

        This method waits for the current document to complete processing
        before stopping the queue. Documents remaining in the queue will
        not be processed.
        """
        if not self.processing:
            logger.info("✅ Queue already stopped (not processing)")
            return

        logger.info("🛑 Shutdown requested - finishing current document...")
        logger.info(f"   Current doc: {self.current_doc['filename'] if self.current_doc else 'none'}")
        logger.info(f"   Remaining in queue: {len(self.queue)} (will NOT be processed)")

        self._shutdown_requested = True

        # Wait for current document to finish
        while self.processing:
            await asyncio.sleep(1)

        logger.info("✅ Queue shutdown complete")

    def clear_history(self):
        """
        Clear completed and failed document history.

        Note: Does NOT clear the active queue or stop current processing.
        """
        completed_count = len(self.completed)
        failed_count = len(self.failed)

        self.completed.clear()
        self.failed.clear()

        logger.info(f"🗑️  History cleared: {completed_count} completed, {failed_count} failed")


# ════════════════════════════════════════════════════════
# Global Queue Singleton
# ════════════════════════════════════════════════════════

_document_queue: Optional[DocumentQueue] = None


def get_document_queue() -> DocumentQueue:
    """
    Get or create global document queue singleton.

    Returns:
        Global DocumentQueue instance

    Note:
        - Only ONE queue instance exists per backend process
        - Thread-safe (Python GIL guarantees atomic assignment)
        - Queue persists for lifetime of backend process
    """
    global _document_queue

    if _document_queue is None:
        logger.info("🏗️  Creating global DocumentQueue instance...")
        _document_queue = DocumentQueue()

    return _document_queue


# ════════════════════════════════════════════════════════
# Queue Management Functions
# ════════════════════════════════════════════════════════

async def shutdown_document_queue():
    """
    Shutdown global document queue (graceful).

    Call this during application shutdown to ensure current
    document finishes processing before exit.
    """
    global _document_queue

    if _document_queue is not None:
        await _document_queue.shutdown()
        _document_queue = None
        logger.info("✅ Global DocumentQueue shutdown complete")
    else:
        logger.info("✅ No DocumentQueue to shutdown")


def get_queue_statistics() -> Dict[str, Any]:
    """
    Get queue statistics (for monitoring/debugging).

    Returns:
        Dict with queue stats, or None if queue not initialized
    """
    global _document_queue

    if _document_queue is None:
        return {
            "initialized": False,
            "queue_size": 0,
            "processing": False
        }

    status = _document_queue.get_status()
    return {
        "initialized": True,
        **status
    }

