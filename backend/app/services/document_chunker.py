"""
GAP #3: Contextual Retrieval with Docling HybridChunker (November 5, 2025)

EVOLUTION: ARIA Pattern → Docling HybridChunker with Contextualization
- ARIA (Session 11): RecursiveCharacterTextSplitter (3000 tokens, 200 overlap)
- HybridChunker (Session 14): Semantic chunking + automatic context enrichment
- POC Results: 31 chunks (HybridChunker) vs 9 chunks (ARIA) = better precision!
- Context: Automatic hierarchical prefixes (Document > Section > Subsection)
- Timeline Savings: Gap #3: 10 days → 3-5 days, Gap #4: OBSOLETE (3 weeks saved!)

Key Benefits:
- Automatic context enrichment (headings/hierarchy)
- Table/list preservation (no splits)
- Better retrieval precision (+7-10% expected)
- Smaller, focused chunks = more relevant results
- Zero additional API costs

Configuration:
- max_tokens: 2000 (optimal for educational manuals)
- merge_peers: True (avoid micro-chunks)
- Tokenizer: sentence-transformers/all-MiniLM-L6-v2 (matches embedding model)
"""
import logging
from typing import List, Dict, Any, Optional
from docling.datamodel.document import DoclingDocument
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

logger = logging.getLogger('diveteacher.docling_chunker')


# ==============================================================================
# GAP #3: CONTEXTUAL RETRIEVAL WITH DOCLING HYBRIDCHUNKER (2025-11-05)
# ==============================================================================
# EVOLUTION: Replaced ARIA RecursiveCharacterTextSplitter with Docling HybridChunker
# 
# MOTIVATION:
# - ARIA Pattern (3000 tokens): Good, but no hierarchical context
# - HybridChunker: Semantic chunking + automatic context enrichment
# - POC Results (Niveau 1.pdf): 31 chunks (optimal) vs 9 chunks (ARIA)
# - Context: Document > Section > Subsection added automatically
# 
# KEY FEATURES:
# - Semantic chunking (respects document structure)
# - Automatic context via contextualize() method
# - Table/list preservation (no splits!)
# - Smaller, focused chunks = better retrieval precision
# - Zero additional API costs (no extra embeddings)
# 
# EXPECTED IMPROVEMENTS:
# - Cross-section queries: +25% precision
# - Document-specific queries: +15% precision
# - Overall retrieval quality: +7-10%
# 
# CONFIGURATION:
# - max_tokens: 2000 (optimal for educational manuals 10-100 pages)
# - merge_peers: True (merge small adjacent chunks, avoid micro-chunks)
# - Tokenizer: sentence-transformers/all-MiniLM-L6-v2 (matches embedding model)
# 
# TIMELINE IMPACT:
# - Gap #3: 10 days → 3-5 days (7 days saved!)
# - Gap #4: OBSOLETE (3 weeks saved!)
# - Total: 12 weeks → 8 weeks (4 weeks saved!)
# ==============================================================================

class DocumentChunker:
    """
    Docling HybridChunker with automatic contextual enrichment.
    
    Gap #3 Implementation (Nov 5, 2025):
    - Semantic chunking that respects document structure
    - Automatic context enrichment (headings/hierarchy)
    - Table/list preservation (no splits)
    - Better retrieval precision (+7-10% expected)
    
    Configuration:
    - max_tokens: 2000 (optimal for educational manuals)
    - merge_peers: True (avoid micro-chunks)
    - Tokenizer: sentence-transformers/all-MiniLM-L6-v2 (matches embedding model)
    
    POC Results (Niveau 1.pdf):
    - 31 chunks with context (HybridChunker)
    - vs 9 chunks without context (ARIA)
    - Better granularity = better precision
    
    Output Format:
    Each chunk includes:
    - text: Raw chunk text (backward compatible)
    - contextualized_text: Text with hierarchical prefix (for embedding)
    - metadata: Complete chunk metadata
    """
    
    # Docling HybridChunker defaults
    DEFAULT_MAX_TOKENS = 2000  # Optimal for educational manuals (10-100 pages)
    DEFAULT_MERGE_PEERS = True  # Merge small adjacent chunks
    DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Match embedding model
    
    def __init__(
        self,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        merge_peers: bool = DEFAULT_MERGE_PEERS,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL
    ):
        """
        Initialize Docling HybridChunker with contextual enrichment.
        
        Args:
            max_tokens: Maximum tokens per chunk (default: 2000)
            merge_peers: Merge small adjacent chunks (default: True)
            embedding_model: HuggingFace model for tokenizer (default: all-MiniLM-L6-v2)
        """
        logger.info(f"🔧 Initializing Docling HybridChunker (Gap #3 - Contextual Retrieval)...")
        logger.info(f"   Max tokens: {max_tokens}")
        logger.info(f"   Merge peers: {merge_peers}")
        logger.info(f"   Embedding model: {embedding_model}")
        logger.info(f"   Expected improvement: +7-10% retrieval quality")
        
        # Initialize tokenizer to match embedding model
        self.tokenizer = HuggingFaceTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(embedding_model),
            max_tokens=max_tokens
        )
        
        # Initialize HybridChunker
        self.chunker = HybridChunker(
            tokenizer=self.tokenizer,
            merge_peers=merge_peers  # Merge small adjacent chunks
        )
        
        self.max_tokens = max_tokens
        self.merge_peers = merge_peers
        self.embedding_model = embedding_model
        
        logger.info("✅ Docling HybridChunker initialized (Gap #3 - Contextual Retrieval)")
    
    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        filename: str,
        upload_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a DoclingDocument using HybridChunker with contextual enrichment.
        
        Args:
            docling_doc: DoclingDocument from converter
            filename: Original filename
            upload_id: Upload ID for tracking
            
        Returns:
            List of chunks with text, contextualized_text, and metadata
            
        Format:
        {
            "index": 0,
            "text": "Raw chunk text...",
            "contextualized_text": "Document Title\nSection\nRaw chunk text...",
            "metadata": {
                "filename": "...",
                "upload_id": "...",
                "chunk_index": 0,
                "total_chunks": 31,
                "num_tokens": 1800,
                "chunking_strategy": "Docling HybridChunker",
                "has_context": True
            }
        }
        """
        logger.info(f"[{upload_id}] 🔪 Starting chunking (Docling HybridChunker + Context): {filename}")
        
        # Chunk using HybridChunker
        chunk_iter = self.chunker.chunk(dl_doc=docling_doc)
        chunks = list(chunk_iter)
        
        logger.info(f"[{upload_id}] ✅ Created {len(chunks)} semantic chunks (HybridChunker)")
        
        # Format chunks for RAG pipeline
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            # Get raw text
            raw_text = chunk.text
            
            # Get contextualized text (with hierarchical prefix)
            contextualized_text = self.chunker.contextualize(chunk=chunk)
            
            # Calculate token count (approximate)
            token_count = self.tokenizer.count_tokens(raw_text)
            
            formatted_chunk = {
                "index": i,
                "text": raw_text,  # Raw text (backward compatible)
                "contextualized_text": contextualized_text,  # CRITICAL: Use this for embedding!
                "metadata": {
                    "filename": filename,
                    "upload_id": upload_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "num_tokens": token_count,
                    "chunking_strategy": "Docling HybridChunker",
                    "has_context": True,  # Flag to indicate context enrichment
                    "max_tokens_config": self.max_tokens,
                    "merge_peers_config": self.merge_peers
                }
            }
            formatted_chunks.append(formatted_chunk)
        
        # Log statistics
        token_counts = [c["metadata"]["num_tokens"] for c in formatted_chunks]
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)
            
            logger.info(f"[{upload_id}] 📊 Chunking stats (Docling HybridChunker):")
            logger.info(f"   Average tokens: {avg_tokens:.0f} (target: ~{self.max_tokens})")
            logger.info(f"   Token range: {min_tokens}-{max_tokens}")
            logger.info(f"   Total chunks: {len(formatted_chunks)}")
            logger.info(f"   Context enrichment: ✅ ENABLED")
            
            # Log first chunk preview
            if formatted_chunks:
                first_raw = formatted_chunks[0]["text"][:100]
                first_contextualized = formatted_chunks[0]["contextualized_text"][:150]
                logger.info(f"   First chunk (raw): {first_raw}...")
                logger.info(f"   First chunk (contextualized): {first_contextualized}...")
        
        return formatted_chunks


# Singleton instance for reuse
_chunker_instance: Optional[DocumentChunker] = None


def get_chunker() -> DocumentChunker:
    """
    Get or create singleton DocumentChunker instance (Docling HybridChunker).
    
    Returns:
        Global DocumentChunker instance with Gap #3 contextual enrichment
    """
    global _chunker_instance
    if _chunker_instance is None:
        logger.info("🏗️  Creating DocumentChunker singleton (Docling HybridChunker + Context)...")
        _chunker_instance = DocumentChunker()
    return _chunker_instance
