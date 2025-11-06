# 📄 Docling - Document Processing Guide

> **Purpose:** Transform PDFs/PPTs into structured, RAG-ready chunks with OCR and table extraction  
> **Version:** Docling 2.60.1 + HybridChunker ✅ **POC GO!**  
> **Last Updated:** November 5, 2025, 18:45 CET ✅ **HybridChunker Validated (Session 14)**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Document Conversion](#document-conversion)
- [Metadata Extraction](#metadata-extraction)
- [Semantic Chunking](#semantic-chunking)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## Overview

**Docling** est une bibliothèque open-source d'IBM pour convertir des documents (PDF, DOCX, PPTX) en formats structurés avec extraction avancée de contenu (OCR, tables, images).

### Why Docling?

✅ **OCR intégré** - Texte scanné → Markdown  
✅ **TableFormer** - Reconnaissance structure tableaux  
✅ **Layout Analysis** - Préserve hiérarchie (titres, sections)  
✅ **Metadata riche** - Pages, tables, images, BBox  
✅ **Production-ready** - Utilisé par IBM Watson

### Key Features for DiveTeacher

- **OCR:** Manuels plongée souvent scannés (MFT FFESSM)
- **Tables:** Tableaux de décompression critiques
- **Hiérarchie:** Structure cours (chapitres, sections)
- **Chunking sémantique:** Chunks cohérents pour RAG

---

## Installation

### Requirements

```bash
# Backend requirements.txt
docling==2.60.1  # ✅ HybridChunker POC GO!
docling-core>=2.48.2,<3.0.0
sentence-transformers==3.3.1
transformers==4.57.1  # Upgraded for Docling 2.60.1
numpy>=2.0,<3.0      # Required by Docling 2.60.1
langchain==1.0.3     # Upgraded for numpy 2.x compatibility
langchain-text-splitters==1.0.0
```

### Docker Setup

**Dockerfile important:**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies (including OpenCV libs for Docling 2.60.1)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
```

**Pourquoi `tqdm==4.66.0`?**
- Docling utilise `tqdm` pour progress bars
- Versions récentes supprimées attribut `_lock`
- → Force install version compatible

### Auto-Download Models

**Au premier usage, Docling télécharge:**
- TableFormer models (HuggingFace)
- Layout analysis models
- OCR engines

**Stockage:** `~/.cache/huggingface/`

**Taille:** ~500MB-1GB

**Temps:** 1-2 min (première fois seulement)

---

## Configuration

### PdfPipelineOptions

**Configuration optimale pour documents plongée:**

```python
# backend/app/integrations/dockling.py
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(
    do_ocr=True,                    # ✅ Pour scans MFT
    do_table_structure=True,        # ✅ Pour tableaux décompression
    artifacts_path=None,            # ✅ Auto-download from HuggingFace
)

# Mode ACCURATE (vs FAST)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
```

### Mode Comparison

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| **FAST** | 🚀 Rapide | 📊 Moyen | Prototyping, dev |
| **ACCURATE** | 🐢 Lent | 📊📊📊 Excellent | Production, tables critiques |

**DiveTeacher:** ACCURATE (tableaux MN90 critiques)

### Timeout Configuration

```python
# env.template
DOCLING_TIMEOUT=300  # 5 minutes (35 pages PDF)
```

**Ajuster selon taille docs:**
- Petit PDF (<10 pages): 60s
- Moyen (10-50 pages): 300s
- Gros (>50 pages): 600s+

---

## Document Conversion

### Singleton Pattern

**Pourquoi singleton?**
- Models Docling chargés **une seule fois**
- Réutilisés pour tous uploads
- Économie mémoire + temps

```python
# backend/app/integrations/dockling.py
class DoclingSingleton:
    """Singleton pour réutiliser DocumentConverter"""
    _instance: Optional[DocumentConverter] = None
    
    @classmethod
    def get_converter(cls) -> DocumentConverter:
        if cls._instance is None:
            logger.info("Initializing Docling DocumentConverter")
            
            pipeline_options = PdfPipelineOptions(
                do_ocr=True,
                do_table_structure=True,
                artifacts_path=None,
            )
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            
            cls._instance = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            logger.info("DocumentConverter initialized with ACCURATE mode + OCR")
        
        return cls._instance
```

### Conversion Function

```python
async def convert_document_to_docling(
    file_path: str,
    timeout: Optional[int] = None
) -> DoclingDocument:
    """
    Convert document to DoclingDocument (pas markdown directement)
    
    Returns:
        DoclingDocument object (pour chunking ultérieur)
    """
    
    # 1. Validation
    is_valid, error_msg = DocumentValidator.validate(
        file_path, 
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB
    )
    if not is_valid:
        raise ValueError(error_msg)
    
    # 2. Conversion avec timeout
    timeout_seconds = timeout or settings.DOCLING_TIMEOUT
    
    try:
        loop = asyncio.get_event_loop()
        
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _convert_sync, file_path),
            timeout=timeout_seconds
        )
        
        logger.info(f"Conversion successful: {len(result.pages)} pages")
        return result
        
    except asyncio.TimeoutError:
        raise TimeoutError(f"Conversion timeout after {timeout_seconds}s")
    except Exception as e:
        raise RuntimeError(f"Docling conversion error: {str(e)}")


def _convert_sync(file_path: str) -> DoclingDocument:
    """Synchronous Docling conversion (runs in thread pool)"""
    converter = DoclingSingleton.get_converter()
    result = converter.convert(file_path)
    return result.document  # ✅ Return DoclingDocument object
```

### Output: DoclingDocument

**Structure:**
```python
DoclingDocument:
  .name: str                    # Filename
  .origin: DocumentOrigin       # Source info
  .num_pages: int               # Page count
  .pages: Dict[int, PageItem]   # Page objects
  .tables: List[TableItem]      # Extracted tables
  .pictures: List[PictureItem]  # Extracted images
  .texts: List[TextItem]        # Text blocks
  .export_to_markdown() -> str  # Export to Markdown
```

**⚠️ Important:** `DoclingDocument` n'a PAS d'attribut `.metadata`!

---

## Metadata Extraction

### Correct Implementation

```python
def extract_document_metadata(doc: DoclingDocument) -> Dict[str, Any]:
    """
    Extract metadata from DoclingDocument
    
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
```

### Example Output

```json
{
  "name": "Niveau 4 GP.pdf",
  "origin": "DocumentOrigin(mimetype='application/pdf', binary_hash=8424329334982803325, filename='Niveau 4 GP.pdf')",
  "num_pages": 35,
  "num_tables": 22,
  "num_pictures": 145
}
```

---

## Semantic Chunking

### HierarchicalChunker

**Purpose:** Découper `DoclingDocument` en chunks sémantiquement cohérents pour RAG.

**Key Features:**
- ✅ Respecte structure document (titres, sections)
- ✅ Boundaries sémantiques (pas taille fixe)
- ✅ Contextualization (garde contexte parent)
- ✅ Token-aware (limite embedding model)

### Configuration

```python
# backend/app/services/document_chunker.py
from docling_core.transforms.chunker import HierarchicalChunker

class DocumentChunker:
    def __init__(
        self,
        tokenizer: str = "BAAI/bge-small-en-v1.5",  # ✅ Embedding model
        max_tokens: int = 512,                       # ✅ Embedding limit
        min_tokens: int = 64,                        # ✅ Éviter tiny chunks
        merge_peers: bool = True                     # ✅ Merge small adjacent
    ):
        self.chunker = HierarchicalChunker(
            tokenizer=tokenizer,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            merge_peers=merge_peers
        )
```

### Tokenizer Choice

**Recommandé:** `BAAI/bge-small-en-v1.5`
- ✅ Multilingual (français + anglais)
- ✅ 512 tokens max
- ✅ Bon équilibre performance/qualité
- ✅ Léger (~120MB)

**Alternatives:**
- `sentence-transformers/all-MiniLM-L6-v2` (anglais, léger)
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (multilingue, gros)

### Chunking Process

```python
def chunk_document(
    self,
    docling_doc: DoclingDocument,
    filename: str,
    upload_id: str
) -> List[Dict[str, Any]]:
    """Chunk a DoclingDocument with semantic boundaries"""
    
    # 1. HierarchicalChunker returns DocChunk objects (NOT dicts!)
    chunk_iterator = self.chunker.chunk(docling_doc)
    chunks = list(chunk_iterator)
    
    # 2. Format for RAG pipeline
    formatted_chunks = []
    for i, chunk in enumerate(chunks):
        # ✅ DocChunk has .text and .meta attributes
        chunk_meta = chunk.meta if hasattr(chunk, 'meta') else {}
        
        formatted_chunk = {
            "index": i,
            "text": chunk.text,  # ✅ NOT chunk["text"]
            "metadata": {
                "filename": filename,
                "upload_id": upload_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "headings": getattr(chunk_meta, "headings", []),
                "doc_items": [str(item) for item in getattr(chunk_meta, "doc_items", [])],
                "origin": str(getattr(chunk_meta, "origin", "")),
            }
        }
        formatted_chunks.append(formatted_chunk)
    
    return formatted_chunks
```

### Chunk Structure

```python
DocChunk:                      # ✅ Object (not dict!)
  .text: str                   # Chunk content
  .meta: DocMeta               # Metadata object
    .doc_items: List[Item]     # Provenance (page, bbox)
    .headings: List[str]       # Parent headings
    .captions: List[str]       # Figure/table captions
    .origin: DocumentOrigin    # Source document
```

### Example Output

**Input:** `Niveau 4 GP.pdf` (35 pages)  
**Output:** 436 chunks

```json
{
  "index": 0,
  "text": "FÉDÉRATION FRANÇAISE D'ÉTUDES ET DE SPORTS SOUS-MARINS\nCommission Technique Nationale\n\nMANUEL DE FORMATION TECHNIQUE\n\nGUIDE DE PALANQUÉE\nNIVEAU 4\n...",
  "metadata": {
    "filename": "Niveau 4 GP.pdf",
    "upload_id": "abc123",
    "chunk_index": 0,
    "total_chunks": 436,
    "headings": [],
    "doc_items": ["TextItem(self_ref='#/texts/0', ...)"],
    "origin": "DocumentOrigin(mimetype='application/pdf', ...)"
  }
}
```

**Stats:**
- Avg tokens: ~127/chunk
- Min tokens: 64
- Max tokens: 512
- Total chunks: 436

---

## Performance Optimization

### 1. Singleton Pattern ✅

**Impact:** -90% startup time (après premier usage)

```python
# First call: ~10s (model loading)
DoclingSingleton.get_converter()

# Subsequent calls: ~0.001s (cached)
DoclingSingleton.get_converter()
```

### 2. Timeout Management ✅

**Évite blocages:**
```python
result = await asyncio.wait_for(
    loop.run_in_executor(None, _convert_sync, file_path),
    timeout=300  # 5 minutes
)
```

### 3. Validation Précoce ✅

**Fail fast avant conversion:**
```python
class DocumentValidator:
    def validate(file_path: str, max_size_mb: int = 50):
        # 1. Existence
        if not path.exists():
            return False, "File does not exist"
        
        # 2. Extension
        if path.suffix not in {'.pdf', '.docx', '.pptx'}:
            return False, "Unsupported format"
        
        # 3. Taille
        if size_mb > max_size_mb:
            return False, f"File too large: {size_mb}MB"
        
        # 4. Corruption
        try:
            with open(file_path, 'rb') as f:
                f.read(1024)
        except Exception:
            return False, "File corrupted"
        
        return True, "Valid"
```

### 4. Async Processing ✅

**Non-blocking uploads:**
```python
# FastAPI background task
background_tasks.add_task(
    process_document,
    file_path,
    upload_id,
    metadata
)
```

### Performance Benchmarks

**Mac M1 Max (32GB):**

| Document | Pages | Conversion | Chunking | Total |
|----------|-------|------------|----------|-------|
| Niveau 4 GP.pdf | 35 | 280s | 5s | 285s |
| Nitrox.pdf | 42 | 320s | 6s | 326s |

**Bottleneck:** Docling conversion (OCR + TableFormer)

**Optimizations futures:**
- Batch processing (parallel PDFs)
- Skip OCR si pas nécessaire (`do_ocr=False`)
- Mode FAST pour non-critical docs

---

## Troubleshooting

### Error: `'DoclingDocument' object has no attribute 'metadata'`

**Cause:** Tentative d'accès `doc.metadata`

**Solution:**
```python
# ❌ Incorrect
metadata = {
    "title": doc.metadata.title,
    "authors": doc.metadata.authors,
}

# ✅ Correct
metadata = {
    "name": doc.name,
    "origin": str(doc.origin),
    "num_pages": doc.num_pages,
}
```

### Error: `'DocChunk' object is not subscriptable`

**Cause:** Tentative d'accès `chunk["text"]`

**Solution:**
```python
# ❌ Incorrect
for chunk in chunks:
    text = chunk["text"]
    meta = chunk["meta"]

# ✅ Correct
for chunk in chunks:
    text = chunk.text       # Attribute access
    meta = chunk.meta       # Attribute access
```

### Error: `AttributeError: '_tqdm' object has no attribute '_lock'`

**Cause:** Version incompatible de `tqdm`

**Solution:**
```bash
# requirements.txt
tqdm==4.66.0  # ✅ Version compatible

# Rebuild Docker
docker compose build backend --no-cache
```

### Error: `TimeoutError: Conversion timeout after 120s`

**Cause:** PDF trop gros ou timeout trop court

**Solution:**
```python
# env.template
DOCLING_TIMEOUT=300  # ✅ Augmenter à 5 min

# Ou passer directement
doc = await convert_document_to_docling(file_path, timeout=600)
```

### Error: `Pure virtual function called!` (C++ crash)

**Cause:** Docker image `python:3.11-slim` manque libs ML

**Solution:**
```dockerfile
# Dockerfile - Option 1: Installer libs ML
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Dockerfile - Option 2: Utiliser image full
FROM python:3.11  # Pas -slim
```

### Warning: `Neither CUDA nor MPS are available`

**Cause:** Pas de GPU disponible (normal en Docker local)

**Impact:** Conversion plus lente (CPU only)

**Solution:** Ignorer si acceptable, ou utiliser DigitalOcean GPU (production)

---

## Examples

### Example 1: Basic Conversion

```python
import asyncio
from app.integrations.dockling import convert_document_to_docling, extract_document_metadata

async def main():
    # Convert PDF
    doc = await convert_document_to_docling("Niveau 4 GP.pdf", timeout=300)
    
    # Extract metadata
    meta = extract_document_metadata(doc)
    print(f"Pages: {meta['num_pages']}")
    print(f"Tables: {meta['num_tables']}")
    
    # Export to markdown
    markdown = doc.export_to_markdown()
    print(f"Markdown length: {len(markdown)} chars")

asyncio.run(main())
```

**Output:**
```
Pages: 35
Tables: 22
Markdown length: 117250 chars
```

### Example 2: Full Pipeline (Convert + Chunk)

```python
import asyncio
from app.integrations.dockling import convert_document_to_docling, extract_document_metadata
from app.services.document_chunker import get_chunker

async def full_pipeline():
    # 1. Convert
    doc = await convert_document_to_docling("Niveau 4 GP.pdf", timeout=300)
    meta = extract_document_metadata(doc)
    print(f"✅ Conversion: {meta['num_pages']} pages")
    
    # 2. Chunk
    chunker = get_chunker()
    chunks = chunker.chunk_document(doc, "Niveau 4 GP.pdf", "test-001")
    print(f"✅ Chunking: {len(chunks)} chunks")
    
    # 3. Inspect first chunk
    chunk0 = chunks[0]
    print(f"Chunk 0 text: {chunk0['text'][:100]}...")
    print(f"Chunk 0 metadata: {chunk0['metadata'].keys()}")

asyncio.run(full_pipeline())
```

**Output:**
```
✅ Conversion: 35 pages
✅ Chunking: 436 chunks
Chunk 0 text: FÉDÉRATION FRANÇAISE D'ÉTUDES ET DE SPORTS SOUS-MARINS...
Chunk 0 metadata: dict_keys(['filename', 'upload_id', 'chunk_index', 'total_chunks', 'headings', 'doc_items', 'origin'])
```

### Example 3: Validation Before Conversion

```python
from app.services.document_validator import DocumentValidator

# Validate before conversion
is_valid, error_msg = DocumentValidator.validate(
    "Niveau 4 GP.pdf",
    max_size_mb=50
)

if not is_valid:
    print(f"❌ Validation failed: {error_msg}")
else:
    print("✅ File is valid, proceeding with conversion...")
    doc = await convert_document_to_docling("Niveau 4 GP.pdf")
```

---

## Warm-up System (Production Pattern) ✅ **ENHANCED (Oct 29, 2025)**

### Overview

Pour éviter les timeouts lors du premier upload (téléchargement modèles ~10-15 min), un système de warm-up **avec conversion de test** est implémenté.

**🎯 Key Enhancement (Fix #8):** Le warmup effectue maintenant une **vraie conversion de test** pour télécharger **TOUS** les modèles (Docling + EasyOCR) au démarrage, pas juste l'initialisation!

**Performance Impact:**
- **Avant:** Premier upload = 98s conversion (80s download OCR + 18s processing)
- **Après:** Premier upload = ~18s conversion (NO DOWNLOAD!)
- **Gain:** +80 secondes économisées sur le premier upload ✅

### Architecture

**1. `DoclingSingleton.warmup()` Method - Enhanced Version**

```python
# backend/app/integrations/dockling.py
class DoclingSingleton:
    @classmethod
    def warmup(cls) -> bool:
        """
        Warm-up: Initialize singleton and download ALL models (including OCR).
        
        This method:
        1. Pre-downloads Docling models from HuggingFace
        2. Pre-downloads EasyOCR models (triggered by test conversion)
        3. Validates the setup with a real conversion
        
        Returns True if successful, False otherwise.
        """
        try:
            logger.info("🔥 WARMING UP DOCLING MODELS")
            
            # Initialize singleton (downloads Docling models)
            converter = cls.get_converter()
            logger.info("✅ DoclingSingleton initialized successfully!")
            
            # 🔥 CRITICAL: Perform test conversion to download OCR models
            logger.info("🧪 Performing test conversion to download OCR models...")
            logger.info("   This ensures EasyOCR models are cached BEFORE first upload")
            
            import io
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import tempfile
            import os
            
            # Create minimal test PDF in memory
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Warmup Test - DiveTeacher RAG")
            c.save()
            buffer.seek(0)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp:
                tmp.write(buffer.read())
                tmp_path = tmp.name
            
            try:
                # Perform test conversion (triggers OCR model download)
                result = converter.convert(tmp_path)
                
                logger.info("✅ Test conversion successful!")
                logger.info("✅ OCR models downloaded and cached")
                
            finally:
                # Cleanup temp file
                os.unlink(tmp_path)
            
            logger.info("🎉 DOCLING WARM-UP COMPLETE!")
            logger.info("ℹ️  ALL models (Docling + EasyOCR) are now cached")
            
            # Validation
            if cls._instance is None:
                logger.error("❌ Warm-up validation FAILED: _instance is None")
                return False
            
            logger.info("✅ VALIDATION: Singleton instance confirmed")
            return True
            
        except Exception as e:
            logger.error(f"❌ WARM-UP FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
```

**Dependencies Required:**
```python
# backend/requirements.txt
reportlab==4.2.5  # PDF generation for warmup test
```

**2. `app/warmup.py` Module**

```python
# backend/app/warmup.py (inside package)
from app.integrations.dockling import DoclingSingleton

def main() -> int:
    """Warm-up entry point"""
    success = DoclingSingleton.warmup()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

**3. Docker Entrypoint**

```bash
# backend/docker-entrypoint.sh
if [ "${SKIP_WARMUP}" != "true" ]; then
    echo "🔥 Step 1: Warming up Docling models..."
    python3 -m app.warmup || {
        echo "⚠️  Warm-up failed or skipped"
    }
fi

# Start FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Benefits

✅ **All models (Docling + EasyOCR) ready before any upload**  
✅ **First upload as fast as subsequent ones** (+80s improvement!)  
✅ **Test conversion validates entire pipeline**  
✅ **Reusable method** (can test with `docker exec rag-backend python3 -m app.warmup`)  
✅ **Validation built-in**  
✅ **Production-ready architecture**

### Expected Logs (Enhanced Version)

```
🔥 Step 1: Warming up Docling models...
🚀 Starting Docling Model Warm-up...
🔥 WARMING UP DOCLING MODELS
📦 Initializing DoclingSingleton...
📝 Config: OCR=True, Tables=True, Mode=ACCURATE
⏳ This may take 10-15 minutes on first run...

✅ DocumentConverter initialized (ACCURATE mode + OCR)
✅ DoclingSingleton initialized successfully!

🧪 Performing test conversion to download OCR models...
   This ensures EasyOCR models are cached BEFORE first upload

Progress: |██████████████████████████████████████████████████| 100% Complete
Download complete.

✅ Test conversion successful!
✅ OCR models downloaded and cached

🎉 DOCLING WARM-UP COMPLETE!
ℹ️  ALL models (Docling + EasyOCR) are now cached
ℹ️  Subsequent document processing will be FAST

✅ VALIDATION: Singleton instance confirmed
✅ VALIDATION: Instance type = DocumentConverter

🎯 Warm-up completed successfully!
✅ Warm-up phase complete
```

### Performance Comparison

| Stage | Before Enhancement | After Enhancement | Improvement |
|-------|-------------------|-------------------|-------------|
| First Conversion | 98s (80s download + 18s processing) | ~18s (all cached!) | **-80s** ✅ |
| Subsequent Conversions | ~18s | ~18s | Same |
| Total Processing (test.pdf) | ~7 min | ~3-4 min | **-50%** ✅ |

**Reference:** 
- See [TIMEOUT-FIX-GUIDE.md](TIMEOUT-FIX-GUIDE.md) for original warmup implementation
- See [FIXES-LOG.md](FIXES-LOG.md#warmup-ocr-incomplete---models-downloaded-on-first-upload---résolu) for Fix #8 complete details

---

## Best Practices

### ✅ DO

1. **Use singleton pattern** pour DocumentConverter
2. **Validate files** avant conversion (extension, size, corruption)
3. **Set reasonable timeouts** (5min pour 35 pages)
4. **Use ACCURATE mode** pour documents critiques (tableaux)
5. **Log extensively** pour debugging
6. **Handle timeouts gracefully** (retry, skip, notify user)

### ❌ DON'T

1. **Don't recreate converter** à chaque requête (slow + memory leak)
2. **Don't ignore validation** (corrupted files crash Docling)
3. **Don't use fixed chunk sizes** (use semantic chunking)
4. **Don't access `.metadata`** on DoclingDocument (doesn't exist)
5. **Don't subscript DocChunk** (use `.text`, `.meta` attributes)

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Document processing pipeline overview
- **[NEO4J.md](NEO4J.md)** - Next step: Graphiti ingestion
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues solutions
- **[@resources/251027-docling-guide-ai-agent.md](../resources/251027-docling-guide-ai-agent.md)** - Detailed Docling guide

---

**🎯 Next Steps:** After chunking → [NEO4J.md](NEO4J.md) for Graphiti ingestion

