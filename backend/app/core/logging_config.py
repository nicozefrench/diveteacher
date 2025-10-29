"""
Structured Logging Configuration for DiveTeacher RAG System

Provides JSON-formatted logging with contextual information for production monitoring.
All logs include: timestamp, level, logger name, upload_id (when applicable), and structured data.
"""
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON-structured logs
    
    Format:
    {
        "timestamp": "2025-10-29T10:30:45.123456Z",
        "level": "INFO",
        "logger": "diveteacher.processor",
        "upload_id": "abc-123",
        "stage": "graphiti",
        "sub_stage": "entity_extraction",
        "message": "Extracted 15 entities from chunk 3/10",
        "metrics": {
            "entities": 15,
            "relations": 8,
            "chunk_index": 3,
            "total_chunks": 10
        }
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add contextual fields if present
        if hasattr(record, 'upload_id'):
            log_data['upload_id'] = record.upload_id
        
        if hasattr(record, 'stage'):
            log_data['stage'] = record.stage
        
        if hasattr(record, 'sub_stage'):
            log_data['sub_stage'] = record.sub_stage
        
        if hasattr(record, 'metrics'):
            log_data['metrics'] = record.metrics
        
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that adds contextual information to all log records
    
    Usage:
        logger = ContextLogger(
            logging.getLogger('diveteacher.processor'),
            {'upload_id': 'abc-123', 'stage': 'docling'}
        )
        logger.info("Processing started")
        # Output includes upload_id and stage automatically
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add context to log record"""
        # Get or create 'extra' dict
        extra = kwargs.get('extra', {})
        
        # Add adapter context
        extra.update(self.extra)
        
        # Update kwargs
        kwargs['extra'] = extra
        
        return msg, kwargs


def setup_structured_logging(level: str = "INFO") -> None:
    """
    Configure structured JSON logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Features:
        - JSON-formatted output
        - Contextual information (upload_id, stage, metrics)
        - Separate loggers for different components
        - Console output to stdout
    """
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(handler)
    
    # Configure application loggers
    app_loggers = [
        'diveteacher',
        'diveteacher.processor',
        'diveteacher.docling',
        'diveteacher.graphiti',
        'diveteacher.llm',
        'diveteacher.neo4j',
        'diveteacher.rag',
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # Capture all levels
        logger.propagate = True  # Propagate to root handler
    
    # Reduce noise from third-party libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.INFO)
    logging.getLogger('openai').setLevel(logging.INFO)
    logging.getLogger('neo4j').setLevel(logging.WARNING)
    
    # Log startup
    startup_logger = logging.getLogger('diveteacher')
    startup_logger.info(
        "Structured logging initialized",
        extra={
            'level': level,
            'format': 'json',
            'loggers': app_loggers
        }
    )


def get_context_logger(
    name: str,
    upload_id: Optional[str] = None,
    stage: Optional[str] = None
) -> ContextLogger:
    """
    Get a context-aware logger
    
    Args:
        name: Logger name (e.g., 'diveteacher.processor')
        upload_id: Optional upload ID to add to all logs
        stage: Optional processing stage to add to all logs
    
    Returns:
        ContextLogger instance with automatic context
    
    Example:
        logger = get_context_logger(
            'diveteacher.processor',
            upload_id='abc-123',
            stage='docling'
        )
        logger.info("Starting conversion")
        # Output includes upload_id and stage automatically
    """
    base_logger = logging.getLogger(name)
    
    context = {}
    if upload_id:
        context['upload_id'] = upload_id
    if stage:
        context['stage'] = stage
    
    return ContextLogger(base_logger, context)


# Convenience functions for common logging patterns

def log_stage_start(
    logger: logging.Logger,
    upload_id: str,
    stage: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Log the start of a processing stage"""
    logger.info(
        f"🔄 Starting {stage}",
        extra={
            'upload_id': upload_id,
            'stage': stage,
            'sub_stage': 'started',
            'metrics': details or {}
        }
    )


def log_stage_progress(
    logger: logging.Logger,
    upload_id: str,
    stage: str,
    sub_stage: str,
    current: int,
    total: int,
    metrics: Optional[Dict[str, Any]] = None
) -> None:
    """Log progress within a stage"""
    progress_pct = int((current / total) * 100) if total > 0 else 0
    
    logger.info(
        f"📊 {stage}: {sub_stage} ({current}/{total} - {progress_pct}%)",
        extra={
            'upload_id': upload_id,
            'stage': stage,
            'sub_stage': sub_stage,
            'metrics': {
                'current': current,
                'total': total,
                'progress_pct': progress_pct,
                **(metrics or {})
            }
        }
    )


def log_stage_complete(
    logger: logging.Logger,
    upload_id: str,
    stage: str,
    duration: float,
    metrics: Optional[Dict[str, Any]] = None
) -> None:
    """Log the completion of a processing stage"""
    logger.info(
        f"✅ {stage} complete",
        extra={
            'upload_id': upload_id,
            'stage': stage,
            'sub_stage': 'completed',
            'duration': duration,
            'metrics': metrics or {}
        }
    )


def log_error(
    logger: logging.Logger,
    upload_id: str,
    stage: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with full context"""
    logger.error(
        f"❌ Error in {stage}: {str(error)}",
        extra={
            'upload_id': upload_id,
            'stage': stage,
            'sub_stage': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        },
        exc_info=True
    )

