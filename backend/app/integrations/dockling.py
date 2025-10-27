"""
Docling Integration avec Configuration Avancée

Ce module gère la conversion de documents (PDF, PPT, DOCX) en DoclingDocument
avec configuration optimisée pour DiveTeacher (OCR + tables + ACCURATE mode).
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.document import DoclingDocument

from app.core.config import settings
from app.services.document_validator import DocumentValidator

logger = logging.getLogger('diveteacher.docling')

# ═══════════════════════════════════════════════════════════
# ✅ NEW: Dedicated executor for Docling (module-level)
# ═══════════════════════════════════════════════════════════
_docling_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="docling_")


class DoclingSingleton:
    """
    Singleton pour réutiliser DocumentConverter (performance)
    
    Le converter Docling charge des modèles ML lourds (DocLayNet, TableFormer).
    Réutiliser la même instance améliore drastiquement les performances.
    """
    _instance: Optional[DocumentConverter] = None
    
    @classmethod
    def get_converter(cls) -> DocumentConverter:
        """Get or create DocumentConverter singleton"""
        if cls._instance is None:
            logger.info("Initializing Docling DocumentConverter...")
            
            # Configuration pour documents plongée (tableaux + OCR)
            pipeline_options = PdfPipelineOptions(
                do_ocr=True,                    # OCR pour scans MFT FFESSM
                do_table_structure=True,        # Tableaux critiques pour plongée
                artifacts_path=None,            # Auto-download from HuggingFace
            )
            
            # Mode ACCURATE pour qualité maximale (extraction tables)
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            
            cls._instance = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            logger.info("✅ DocumentConverter initialized (ACCURATE mode + OCR)")
        
        return cls._instance


async def convert_document_to_docling(
    file_path: str,
    timeout: Optional[int] = None
) -> DoclingDocument:
    """
    Convert document to DoclingDocument (NOT markdown)
    
    Cette fonction retourne un DoclingDocument pour permettre le chunking
    sémantique ultérieur avec HybridChunker.
    
    ✅ Uses dedicated executor (not default)
    ✅ Works with any event loop (single or multi)
    
    Args:
        file_path: Path to document file
        timeout: Optional timeout in seconds (default: from settings)
        
    Returns:
        DoclingDocument object (pour chunking ultérieur)
        
    Raises:
        ValueError: Invalid file (validation failed)
        RuntimeError: Docling conversion failed
        TimeoutError: Conversion timeout exceeded
    """
    
    # 1. Validation stricte
    is_valid, error_msg = DocumentValidator.validate(
        file_path, 
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB
    )
    if not is_valid:
        logger.error(f"❌ Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    filename = Path(file_path).name
    logger.info(f"🔄 Converting document: {filename}")
    
    # 2. Conversion avec timeout
    timeout_seconds = timeout or settings.DOCLING_TIMEOUT
    
    try:
        loop = asyncio.get_event_loop()
        
        # ═══════════════════════════════════════════════════════════
        # ✅ FIXED: Use dedicated executor (not None!)
        # ═══════════════════════════════════════════════════════════
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _docling_executor,  # ← Dedicated executor (module-level)
                _convert_sync,
                file_path
            ),
            timeout=timeout_seconds
        )
        
        # Log métriques
        logger.info(f"✅ Conversion successful: {filename}")
        logger.info(f"   📄 Pages: {len(result.pages)}")
        logger.info(f"   📊 Tables: {len(result.tables)}")
        logger.info(f"   🖼️  Images: {len(result.pictures)}")
        
        return result
        
    except asyncio.TimeoutError:
        error_msg = f"⏱️  Conversion timeout after {timeout_seconds}s: {filename}"
        logger.error(error_msg)
        raise TimeoutError(error_msg)
    
    except Exception as e:
        error_msg = f"❌ Docling conversion error: {filename} - {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)


def _convert_sync(file_path: str) -> DoclingDocument:
    """
    Synchronous Docling conversion (runs in dedicated thread pool)
    
    Args:
        file_path: Path to document
        
    Returns:
        DoclingDocument (NOT markdown string)
    """
    converter = DoclingSingleton.get_converter()
    result = converter.convert(file_path)
    
    # Return DoclingDocument object pour chunking
    return result.document


def extract_document_metadata(doc: DoclingDocument) -> Dict[str, Any]:
    """
    Extract metadata from DoclingDocument
    
    Args:
        doc: DoclingDocument from converter
        
    Returns:
        Dictionary with document metadata
        
    Note:
        DoclingDocument doesn't have .metadata attribute
        Use .name, .origin, and direct attributes instead
    """
    return {
        "name": doc.name if hasattr(doc, "name") else "Untitled",
        "origin": str(doc.origin) if hasattr(doc, "origin") else "unknown",
        "num_pages": doc.num_pages if hasattr(doc, "num_pages") else len(doc.pages),
        "num_tables": len(doc.tables),
        "num_pictures": len(doc.pictures),
    }
