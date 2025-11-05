"""
ARIA-Pattern Text Chunker
Based on production-validated RecursiveCharacterTextSplitter.

Replaces Docling's HierarchicalChunker (which doesn't support configurable token limits)
with LangChain's RecursiveCharacterTextSplitter (ARIA production-proven).

ARIA Production Evidence:
- 3 days continuous operation
- 100% success rate
- ~50 documents processed
- Average 20 chunks per document (vs 204 with HierarchicalChunker)
- 2-5 minutes per document (vs 36 min)
- Excellent quality
- Zero embedding model errors

Configuration:
- 3000 tokens per chunk (12000 chars)
- 200 token overlap (800 chars)
- Recursive splitting on semantic boundaries
"""
import logging
from typing import List, Dict, Any, Optional
from docling.datamodel.document import DoclingDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger('diveteacher.aria_chunker')


# ==============================================================================
# ARIA CHUNKING PATTERN (2025-10-31)
# ==============================================================================
# CRITICAL FIX: Replaced HierarchicalChunker with RecursiveCharacterTextSplitter
#
# ROOT CAUSE:
# - HierarchicalChunker (Docling) does NOT support configurable max_tokens/min_tokens
# - It has internal hierarchical logic that creates 204 micro-chunks
# - Parameters we set (256→3000) were IGNORED by HierarchicalChunker
#
# SOLUTION:
# - Use ARIA's exact production pattern: RecursiveCharacterTextSplitter (LangChain)
# - 3000 tokens per chunk (12000 chars)
# - 200 token overlap (800 chars)
# - Proven in ARIA production: 3 days, 100% success rate
#
# Expected Results (Niveau 1.pdf = ~52,000 tokens):
# - Chunks: 17 (vs 204 with HierarchicalChunker)
# - Time: 3 min (vs 36 min)
# - Speedup: 12× faster
# - Quality: Better (more context per chunk)
# ==============================================================================

class DocumentChunker:
    """
    ARIA-validated chunking strategy using RecursiveCharacterTextSplitter.

    Production-proven configuration:
    - 3000 tokens per chunk (12000 chars)
    - 200 token overlap (800 chars)
    - Recursive splitting on semantic boundaries

    Based on ARIA production:
    - 3 days runtime, 100% success rate
    - ~50 documents, ~20 chunks per document
    - 2-5 minutes per document
    - Excellent quality (better than micro-chunks)
    - Proven with Graphiti + Claude + OpenAI embeddings

    Replaces HierarchicalChunker which:
    - Does NOT support configurable token limits
    - Creates 204 micro-chunks (internal logic)
    - Results in 36 min processing (unacceptable)
    """

    # ARIA production-validated constants
    CHARS_PER_TOKEN = 4          # Standard approximation
    CHUNK_SIZE_TOKENS = 3000     # ARIA production standard
    CHUNK_OVERLAP_TOKENS = 200   # ARIA production standard

    def __init__(
        self,
        chunk_tokens: int = 3000,      # ARIA production standard
        overlap_tokens: int = 200,     # ARIA production standard
        chars_per_token: int = 4       # Standard approximation
    ):
        """
        Initialize RecursiveCharacterTextSplitter with ARIA production config.

        Args:
            chunk_tokens: Target tokens per chunk (ARIA: 3000)
            overlap_tokens: Token overlap between chunks (ARIA: 200)
            chars_per_token: Character-to-token ratio (standard: 4)
        """
        chunk_size = chunk_tokens * chars_per_token     # 3000 × 4 = 12000 chars
        chunk_overlap = overlap_tokens * chars_per_token  # 200 × 4 = 800 chars

        logger.info("🔧 Initializing RecursiveCharacterTextSplitter (ARIA Pattern)...")
        logger.info(f"   Chunk size: {chunk_tokens} tokens ({chunk_size} chars)")
        logger.info(f"   Overlap: {overlap_tokens} tokens ({chunk_overlap} chars)")
        logger.info("   Expected for Niveau 1.pdf: ~17 chunks (was 204 with HierarchicalChunker)")

        # Initialize LangChain splitter (ARIA exact pattern)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # ARIA standard
        )

        self.chunk_tokens = chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.chars_per_token = chars_per_token

        logger.info("✅ RecursiveCharacterTextSplitter initialized (ARIA Pattern)")

    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        filename: str,
        upload_id: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a DoclingDocument using ARIA's production-validated strategy.

        Args:
            docling_doc: DoclingDocument from converter
            filename: Original filename
            upload_id: Upload ID for tracking

        Returns:
            List of chunks with text + metadata

        Format (compatible with existing pipeline):
        {
            "index": 0,
            "text": "Full chunk text...",
            "metadata": {
                "filename": "...",
                "upload_id": "...",
                "chunk_index": 0,
                "total_chunks": 17,
                "num_tokens": 3000,
                "chunking_strategy": "ARIA RecursiveCharacterTextSplitter"
            }
        }
        """
        logger.info(f"[{upload_id}] 🔪 Starting chunking (ARIA Pattern): {filename}")

        # Extract text from DoclingDocument (markdown format)
        doc_text = docling_doc.export_to_markdown()

        logger.info(f"[{upload_id}] 📄 Document text: {len(doc_text)} chars (~{len(doc_text) // self.chars_per_token} tokens)")

        # Split using RecursiveCharacterTextSplitter (ARIA exact pattern)
        chunk_texts = self.splitter.split_text(doc_text)

        logger.info(f"[{upload_id}] ✅ Created {len(chunk_texts)} semantic chunks (ARIA Pattern)")

        # Format chunks for RAG pipeline
        formatted_chunks = []
        for i, chunk_text in enumerate(chunk_texts):
            formatted_chunk = {
                "index": i,
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "upload_id": upload_id,
                    "chunk_index": i,
                    "total_chunks": len(chunk_texts),
                    "num_tokens": len(chunk_text) // self.chars_per_token,  # Estimated
                    "chunking_strategy": "ARIA RecursiveCharacterTextSplitter",
                    "chunk_size_config": self.chunk_tokens,
                    "overlap_config": self.overlap_tokens
                }
            }
            formatted_chunks.append(formatted_chunk)

        # Log statistics (ARIA pattern)
        token_counts = [c["metadata"]["num_tokens"] for c in formatted_chunks]
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)

            logger.info(f"[{upload_id}] 📊 Chunking stats (ARIA Pattern):")
            logger.info(f"   Average tokens: {avg_tokens:.0f} (expected: ~{self.chunk_tokens})")
            logger.info(f"   Token range: {min_tokens}-{max_tokens}")
            logger.info(f"   Total chunks: {len(formatted_chunks)}")

            # Validation check
            if len(formatted_chunks) > 100:
                logger.warning(f"⚠️  Chunk count ({len(formatted_chunks)}) unexpectedly high!")
                logger.warning("   Expected: ~17 chunks for Niveau 1.pdf (208KB, 16 pages)")
                logger.warning(f"   Actual chunk_size: {self.chunk_tokens} tokens")

        return formatted_chunks


# Singleton instance pour réutilisation
_chunker_instance: Optional[DocumentChunker] = None


def get_chunker() -> DocumentChunker:
    """
    Get or create singleton DocumentChunker instance (ARIA Pattern).

    Returns:
        Global DocumentChunker instance with ARIA production-validated configuration
    """
    global _chunker_instance
    if _chunker_instance is None:
        logger.info("🏗️  Creating DocumentChunker singleton (ARIA Pattern)...")
        _chunker_instance = DocumentChunker()
    return _chunker_instance

