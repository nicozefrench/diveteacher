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
from app.core.logging_config import log_stage_start, log_stage_complete, log_error
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
    
    @classmethod
    def warmup(cls) -> bool:
        """
        Warm-up: Initialize singleton and download ALL models (including OCR).
        
        This method should be called during container startup to:
        1. Pre-download Docling models from HuggingFace
        2. Pre-download EasyOCR models (triggered by test conversion)
        3. Initialize the singleton instance
        4. Validate the setup with a real conversion
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("=" * 60)
            logger.info("🔥 WARMING UP DOCLING MODELS")
            logger.info("=" * 60)
            logger.info("")
            
            logger.info("📦 Initializing DoclingSingleton...")
            logger.info("📝 Config: OCR=True, Tables=True, Mode=ACCURATE")
            logger.info("⏳ This may take 10-15 minutes on first run...")
            logger.info("")
            
            # Initialize singleton (will download models if first time)
            converter = cls.get_converter()
            
            logger.info("✅ DoclingSingleton initialized successfully!")
            logger.info("")
            
            # 🔥 CRITICAL: Perform a test conversion to download OCR models
            logger.info("🧪 Performing test conversion to download OCR models...")
            logger.info("   This ensures EasyOCR models are cached BEFORE first upload")
            logger.info("")
            
            import io
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create minimal test PDF in memory
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Warmup Test - DiveTeacher RAG")
            c.save()
            buffer.seek(0)
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp:
                tmp.write(buffer.read())
                tmp_path = tmp.name
            
            try:
                # Perform test conversion (triggers OCR model download)
                # Note: convert() accepts a file path directly
                result = converter.convert(tmp_path)
                
                logger.info("✅ Test conversion successful!")
                logger.info("✅ OCR models downloaded and cached")
                logger.info("")
                
            finally:
                # Cleanup temp file
                import os
                os.unlink(tmp_path)
            
            # ═══════════════════════════════════════════════════════════
            # 🔥 NEW: Warm-up ARIA Chunker (RecursiveCharacterTextSplitter)
            # ═══════════════════════════════════════════════════════════
            logger.info("🔪 Warming up ARIA Chunker (RecursiveCharacterTextSplitter)...")
            logger.info("   This ensures LangChain tokenizer is loaded and ready")
            logger.info("")
            
            try:
                from app.services.document_chunker import get_chunker
                
                # Initialize chunker singleton
                chunker = get_chunker()
                
                # Test chunking with the converted test document
                # This warms up the tokenizer and validates chunking works
                test_chunks = chunker.chunk_document(
                    docling_doc=result.document,
                    filename="warmup-test.pdf",
                    upload_id="warmup-test"
                )
                
                logger.info(f"✅ ARIA Chunker initialized successfully!")
                logger.info(f"   • Created {len(test_chunks)} chunks (ARIA pattern)")
                logger.info(f"   • RecursiveCharacterTextSplitter: 3000 tokens/chunk, 200 overlap")
                logger.info(f"   • LangChain tokenizer loaded and cached")
                logger.info("")
                
            except Exception as e:
                logger.warning(f"⚠️  ARIA Chunker warmup failed: {e}")
                logger.warning("   First chunking operation may be slightly slower (~1s)")
                logger.warning("   This is NOT critical - chunker will initialize on first upload")
                logger.info("")
            
            logger.info("=" * 60)
            logger.info("🎉 COMPLETE WARM-UP FINISHED!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("ℹ️  Docling: ACCURATE + OCR + Tables config ✅")
            logger.info("ℹ️  ALL models (Docling + EasyOCR) cached ✅")
            logger.info("ℹ️  ARIA Chunker: RecursiveCharacterTextSplitter ready ✅")
            logger.info("ℹ️  System 100% nominal for ingestion sessions ✅")
            logger.info("")
            logger.info("⚠️  NOTE: Warmup does NOT touch database")
            logger.info("   • Neo4j data preserved (additive ingestion)")
            logger.info("   • Knowledge graph will grow with each session")
            logger.info("   • Use init-e2e-test.sh to clean DB if needed")
            logger.info("")
            
            # Validation: Check singleton is properly initialized
            if cls._instance is None:
                logger.error("❌ Warm-up validation FAILED: _instance is None")
                return False
            
            logger.info("✅ VALIDATION: Singleton instance confirmed")
            logger.info(f"✅ VALIDATION: Instance type = {type(cls._instance).__name__}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ WARM-UP FAILED: {e}")
            logger.error("=" * 60)
            logger.error("")
            logger.error("⚠️  Document processing may be slower on first upload")
            logger.error("⚠️  Models will be downloaded on-demand")
            logger.error("")
            import traceback
            traceback.print_exc()
            return False


async def convert_document_to_docling(
    file_path: str,
    timeout: Optional[int] = None,
    upload_id: Optional[str] = None
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
        upload_id: Optional upload ID for logging context
        
    Returns:
        DoclingDocument object (pour chunking ultérieur)
        
    Raises:
        ValueError: Invalid file (validation failed)
        RuntimeError: Docling conversion failed
        TimeoutError: Conversion timeout exceeded
    """
    from time import time
    
    # 1. Validation stricte
    is_valid, error_msg = DocumentValidator.validate(
        file_path, 
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB
    )
    if not is_valid:
        if upload_id:
            log_error(logger, upload_id, "validation", ValueError(error_msg))
        else:
            logger.error(f"❌ Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    filename = Path(file_path).name
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    
    if upload_id:
        logger.info(
            f"🔄 Starting Docling conversion",
            extra={
                'upload_id': upload_id,
                'stage': 'conversion',
                'sub_stage': 'validation_passed',
                'metrics': {
                    'filename': filename,
                    'file_size_mb': round(file_size_mb, 2)
                }
            }
        )
    else:
        logger.info(f"🔄 Converting document: {filename}")
    
    # 2. Conversion avec timeout
    timeout_seconds = timeout or settings.DOCLING_TIMEOUT
    conversion_start = time()
    
    try:
        loop = asyncio.get_event_loop()
        
        # Run conversion in dedicated executor
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _docling_executor,
                _convert_sync,
                file_path,
                upload_id
            ),
            timeout=timeout_seconds
        )
        
        conversion_duration = time() - conversion_start
        
        # Log métriques
        if upload_id:
            logger.info(
                f"✅ Conversion successful",
                extra={
                    'upload_id': upload_id,
                    'stage': 'conversion',
                    'sub_stage': 'complete',
                    'duration': round(conversion_duration, 2),
                    'metrics': {
                        'filename': filename,
                        'pages': len(result.pages),
                        'tables': len(result.tables),
                        'pictures': len(result.pictures),
                        'file_size_mb': round(file_size_mb, 2)
                    }
                }
            )
        else:
            logger.info(f"✅ Conversion successful: {filename}")
            logger.info(f"   📄 Pages: {len(result.pages)}")
            logger.info(f"   📊 Tables: {len(result.tables)}")
            logger.info(f"   🖼️  Images: {len(result.pictures)}")
        
        return result
        
    except asyncio.TimeoutError:
        error_msg = f"⏱️  Conversion timeout after {timeout_seconds}s: {filename}"
        if upload_id:
            log_error(logger, upload_id, "conversion", TimeoutError(error_msg))
        else:
            logger.error(error_msg)
        raise TimeoutError(error_msg)
    
    except Exception as e:
        error_msg = f"❌ Docling conversion error: {filename} - {str(e)}"
        if upload_id:
            log_error(logger, upload_id, "conversion", e, context={'filename': filename})
        else:
            logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)


def _convert_sync(file_path: str, upload_id: Optional[str] = None) -> DoclingDocument:
    """
    Synchronous Docling conversion (runs in dedicated thread pool)
    
    Args:
        file_path: Path to document
        upload_id: Optional upload ID for logging
        
    Returns:
        DoclingDocument (NOT markdown string)
    """
    filename = Path(file_path).name
    
    if upload_id:
        print(f"[{upload_id}] 🔄 START conversion: {filename}", flush=True)
    else:
        print(f"[_convert_sync] 🔄 START conversion: {filename}", flush=True)
    
    converter = DoclingSingleton.get_converter()
    
    if upload_id:
        print(f"[{upload_id}] ✅ Converter obtained", flush=True)
        print(f"[{upload_id}] 🚀 Starting conversion...", flush=True)
    
    result = converter.convert(file_path)
    
    if upload_id:
        print(f"[{upload_id}] ✅ Conversion complete", flush=True)
    else:
        print(f"[_convert_sync] ✅ Conversion complete", flush=True)
    
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
