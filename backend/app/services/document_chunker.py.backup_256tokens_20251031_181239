"""
Document Chunking avec Docling HybridChunker

Ce module utilise HybridChunker de Docling pour créer des chunks
sémantiquement cohérents, optimisés pour RAG avec embedding models.
"""
import logging
from typing import List, Dict, Any, Optional
from docling.datamodel.document import DoclingDocument
from docling_core.transforms.chunker import HierarchicalChunker

logger = logging.getLogger('diveteacher.chunker')


class DocumentChunker:
    """
    Wrapper pour HybridChunker avec configuration DiveTeacher
    
    HybridChunker combine:
    - Structure du document (sections, paragraphes, listes)
    - Token limits (max_tokens pour embedding models)
    - Semantic coherence (garder idées ensemble)
    """
    
    def __init__(
        self,
        tokenizer: str = "BAAI/bge-small-en-v1.5",
        max_tokens: int = 256,  # ✅ Réduit à 256 pour éviter output overflow dans Graphiti (OpenAI 8K limit)
        min_tokens: int = 64,
        merge_peers: bool = True
    ):
        """
        Initialize HybridChunker
        
        Args:
            tokenizer: HuggingFace tokenizer model ID
            max_tokens: Maximum tokens per chunk (embedding model limit)
            min_tokens: Minimum tokens per chunk (éviter micro-chunks)
            merge_peers: Merge small adjacent chunks (optimisation)
        """
        logger.info(f"🔧 Initializing HierarchicalChunker...")
        logger.info(f"   Tokenizer: {tokenizer}")
        logger.info(f"   Token limits: {min_tokens}-{max_tokens}")
        
        self.chunker = HierarchicalChunker(
            tokenizer=tokenizer,
            max_tokens=max_tokens,
            min_tokens=min_tokens,
            merge_peers=merge_peers
        )
        
        logger.info("✅ HierarchicalChunker initialized")
    
    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        filename: str,
        upload_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a DoclingDocument with semantic boundaries
        
        Args:
            docling_doc: DoclingDocument from converter
            filename: Original filename (for metadata)
            upload_id: Upload ID (for tracking)
            
        Returns:
            List of chunks with text + metadata
            
        Format de chunk:
        {
            "index": 0,
            "text": "Full chunk text with headers...",
            "metadata": {
                "filename": "...",
                "upload_id": "...",
                "chunk_index": 0,
                "total_chunks": 10,
                "headings": ["Section Title"],
                "doc_items": [...],  # Provenance (page, bbox)
                "origin": {...}
            }
        }
        """
        logger.info(f"[{upload_id}] 🔪 Starting chunking: {filename}")
        
        # Chunking avec HybridChunker
        chunk_iterator = self.chunker.chunk(docling_doc)
        chunks = list(chunk_iterator)
        
        logger.info(f"[{upload_id}] ✅ Created {len(chunks)} semantic chunks")
        
        # Format chunks pour RAG pipeline
        # Note: chunk is DocChunk object (not dict), use .text and .meta attributes
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            # Extract metadata from DocChunk.meta
            chunk_meta = chunk.meta if hasattr(chunk, 'meta') else {}
            
            formatted_chunk = {
                "index": i,
                "text": chunk.text if hasattr(chunk, 'text') else str(chunk),
                "metadata": {
                    "filename": filename,
                    "upload_id": upload_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "headings": getattr(chunk_meta, "headings", []) if chunk_meta else [],
                    "doc_items": [str(item) for item in getattr(chunk_meta, "doc_items", [])] if chunk_meta else [],
                    "origin": str(getattr(chunk_meta, "origin", "")) if chunk_meta else "",
                }
            }
            formatted_chunks.append(formatted_chunk)
        
        # Log statistiques
        token_counts = [len(c["text"].split()) for c in formatted_chunks]
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)
            
            logger.info(f"[{upload_id}] 📊 Chunking stats:")
            logger.info(f"   Average tokens: {avg_tokens:.0f}")
            logger.info(f"   Token range: {min_tokens}-{max_tokens}")
        
        return formatted_chunks


# Singleton instance pour réutilisation
_chunker_instance: Optional[DocumentChunker] = None


def get_chunker() -> DocumentChunker:
    """
    Get or create singleton chunker
    
    Singleton car HybridChunker charge un tokenizer (coûteux).
    """
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = DocumentChunker()
    return _chunker_instance

