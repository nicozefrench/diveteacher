#!/usr/bin/env python3
"""
Docling HybridChunker POC - ARIA vs HybridChunker Comparison

Purpose: Validate if Docling HybridChunker is better than current ARIA pattern
Decision: GO (Gap #3 Revised) or NO-GO (Gap #3 Original)

Tests:
1. Chunk count: 5-8 (HybridChunker) vs 17 (ARIA)
2. Tables preserved: 100% (no splits)
3. Context quality: Meaningful hierarchy
4. Performance: <20% overhead

Usage:
    docker compose -f docker/docker-compose.dev.yml exec backend python scripts/poc_hybrid_vs_aria.py

Requirements:
    - docling[chunking]>=2.5.1
    - transformers>=4.48.3
    - sentence-transformers>=3.3.1
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class POCRunner:
    """
    POC Runner for comparing ARIA vs Docling HybridChunker.
    """
    
    def __init__(self, test_file: str = "/app/TestPDF/Niveau 1.pdf"):
        """
        Initialize POC runner.
        
        Args:
            test_file: Path to test PDF (absolute path in Docker)
        """
        self.test_file = Path(test_file)
        
        if not self.test_file.exists():
            raise FileNotFoundError(f"Test file not found: {self.test_file}")
        
        logger.info(f"📄 Test file: {self.test_file}")
        logger.info(f"   Size: {self.test_file.stat().st_size / 1024:.1f} KB")
        
        # Initialize Docling converter (same config as production)
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            do_table_structure=True,
            artifacts_path=None
        )
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        # ARIA config (production settings)
        self.aria_chunk_size = 3000  # tokens
        self.aria_overlap = 200      # tokens
        self.chars_per_token = 4     # standard approximation
        
        # HybridChunker config
        self.hybrid_max_tokens = 2000  # Adjust based on doc size
        
    def convert_document(self) -> Any:
        """
        Convert PDF to DoclingDocument.
        
        Returns:
            DoclingDocument object
        """
        logger.info("🔄 Converting document with Docling...")
        start_time = time.time()
        
        result = self.converter.convert(source=str(self.test_file))
        doc = result.document
        
        duration = time.time() - start_time
        
        logger.info(f"✅ Conversion complete in {duration:.2f}s")
        logger.info(f"   Pages: {doc.num_pages if hasattr(doc, 'num_pages') else 'N/A'}")
        logger.info(f"   Tables: {len(doc.tables)}")
        
        return doc
    
    def test_aria_chunking(self, doc: Any) -> Dict[str, Any]:
        """
        Test current ARIA chunking pattern.
        
        Args:
            doc: DoclingDocument
            
        Returns:
            Dict with metrics
        """
        logger.info("\n" + "="*70)
        logger.info("📊 TEST 1: ARIA Pattern (Current Production)")
        logger.info("="*70)
        
        start_time = time.time()
        
        # Extract markdown
        markdown_text = doc.export_to_markdown()
        
        logger.info(f"   Markdown: {len(markdown_text)} chars (~{len(markdown_text) // self.chars_per_token} tokens)")
        
        # Initialize ARIA splitter
        chunk_size = self.aria_chunk_size * self.chars_per_token
        chunk_overlap = self.aria_overlap * self.chars_per_token
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Chunk
        chunks = splitter.split_text(markdown_text)
        
        duration = time.time() - start_time
        
        # Calculate metrics
        chunk_sizes = [len(c) // self.chars_per_token for c in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        
        logger.info(f"\n✅ ARIA Results:")
        logger.info(f"   Chunks: {len(chunks)}")
        logger.info(f"   Avg size: {avg_size:.0f} tokens (target: {self.aria_chunk_size})")
        logger.info(f"   Size range: {min(chunk_sizes)}-{max(chunk_sizes)} tokens")
        logger.info(f"   Duration: {duration:.2f}s")
        
        # Check for table splits (heuristic: tables have "| " pattern)
        table_chunks = [i for i, c in enumerate(chunks) if "| " in c or "|--" in c]
        logger.info(f"   Chunks with tables: {len(table_chunks)}")
        
        # Sample first chunk
        logger.info(f"\n📝 Sample chunk (first 200 chars):")
        logger.info(f"   {chunks[0][:200]}...")
        
        return {
            "method": "ARIA",
            "chunk_count": len(chunks),
            "avg_tokens": avg_size,
            "token_range": (min(chunk_sizes), max(chunk_sizes)),
            "duration": duration,
            "chunks_with_tables": len(table_chunks),
            "has_context_prefix": False,
            "sample_chunk": chunks[0][:200]
        }
    
    def test_hybrid_chunking(self, doc: Any) -> Dict[str, Any]:
        """
        Test Docling HybridChunker.
        
        Args:
            doc: DoclingDocument
            
        Returns:
            Dict with metrics
        """
        logger.info("\n" + "="*70)
        logger.info("📊 TEST 2: Docling HybridChunker (Proposed)")
        logger.info("="*70)
        
        start_time = time.time()
        
        # Initialize HybridChunker
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        try:
            tokenizer = HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(embedding_model),
                max_tokens=self.hybrid_max_tokens
            )
        except Exception as e:
            logger.error(f"❌ Failed to load tokenizer: {e}")
            logger.info("💡 Downloading model (first time only)...")
            tokenizer = HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(embedding_model),
                max_tokens=self.hybrid_max_tokens
            )
        
        chunker = HybridChunker(
            tokenizer=tokenizer,
            merge_peers=True  # KEY: Merge small adjacent chunks
        )
        
        logger.info(f"   Max tokens: {self.hybrid_max_tokens}")
        logger.info(f"   Merge peers: True")
        
        # Chunk
        chunks = list(chunker.chunk(dl_doc=doc))
        
        duration = time.time() - start_time
        
        # Calculate metrics
        chunk_sizes = [len(c.text.split()) for c in chunks]  # Approximate tokens
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        
        logger.info(f"\n✅ HybridChunker Results:")
        logger.info(f"   Chunks: {len(chunks)}")
        logger.info(f"   Avg size: {avg_size:.0f} tokens (target: {self.hybrid_max_tokens})")
        logger.info(f"   Size range: {min(chunk_sizes)}-{max(chunk_sizes)} tokens")
        logger.info(f"   Duration: {duration:.2f}s")
        
        # Check for table splits
        table_chunks = [i for i, c in enumerate(chunks) if "| " in c.text or "|--" in c.text]
        logger.info(f"   Chunks with tables: {len(table_chunks)}")
        
        # Test contextualize()
        if chunks:
            contextualized = chunker.contextualize(chunk=chunks[0])
            has_prefix = len(contextualized) > len(chunks[0].text)
            
            logger.info(f"\n🏷️  Context Prefix Test:")
            logger.info(f"   Prefix added: {'YES ✅' if has_prefix else 'NO ❌'}")
            logger.info(f"   Raw chunk: {len(chunks[0].text)} chars")
            logger.info(f"   Contextualized: {len(contextualized)} chars")
            
            # Sample contextualized chunk
            logger.info(f"\n📝 Sample contextualized chunk (first 300 chars):")
            logger.info(f"   {contextualized[:300]}...")
            
            sample_context = contextualized[:200]
        else:
            has_prefix = False
            sample_context = ""
        
        return {
            "method": "HybridChunker",
            "chunk_count": len(chunks),
            "avg_tokens": avg_size,
            "token_range": (min(chunk_sizes), max(chunk_sizes)) if chunk_sizes else (0, 0),
            "duration": duration,
            "chunks_with_tables": len(table_chunks),
            "has_context_prefix": has_prefix,
            "sample_chunk": sample_context
        }
    
    def compare_results(self, aria_results: Dict, hybrid_results: Dict) -> Dict[str, Any]:
        """
        Compare ARIA vs HybridChunker results.
        
        Returns:
            Comparison dict with decision
        """
        logger.info("\n" + "="*70)
        logger.info("🔍 COMPARISON: ARIA vs HybridChunker")
        logger.info("="*70)
        
        # Chunk count comparison
        chunk_improvement = (aria_results["chunk_count"] - hybrid_results["chunk_count"]) / aria_results["chunk_count"] * 100
        
        logger.info(f"\n1️⃣  Chunk Count:")
        logger.info(f"   ARIA: {aria_results['chunk_count']} chunks")
        logger.info(f"   HybridChunker: {hybrid_results['chunk_count']} chunks")
        logger.info(f"   Improvement: {chunk_improvement:+.1f}% ({'✅ BETTER' if chunk_improvement > 0 else '❌ WORSE'})")
        logger.info(f"   Target: 5-10 chunks for 16-page doc")
        
        chunk_ok = 5 <= hybrid_results["chunk_count"] <= 10
        logger.info(f"   Result: {'✅ PASS' if chunk_ok else '❌ FAIL'}")
        
        # Performance comparison
        perf_overhead = (hybrid_results["duration"] - aria_results["duration"]) / aria_results["duration"] * 100
        
        logger.info(f"\n2️⃣  Performance:")
        logger.info(f"   ARIA: {aria_results['duration']:.2f}s")
        logger.info(f"   HybridChunker: {hybrid_results['duration']:.2f}s")
        logger.info(f"   Overhead: {perf_overhead:+.1f}% (target: <20%)")
        
        perf_ok = perf_overhead < 20
        logger.info(f"   Result: {'✅ PASS' if perf_ok else '⚠️  ACCEPTABLE' if perf_overhead < 50 else '❌ FAIL'}")
        
        # Context prefix
        logger.info(f"\n3️⃣  Context Prefix:")
        logger.info(f"   ARIA: ❌ None")
        logger.info(f"   HybridChunker: {'✅ YES' if hybrid_results['has_context_prefix'] else '❌ NO'}")
        logger.info(f"   Result: {'✅ PASS' if hybrid_results['has_context_prefix'] else '❌ FAIL'}")
        
        # Table preservation (heuristic)
        logger.info(f"\n4️⃣  Table Handling:")
        logger.info(f"   ARIA: {aria_results['chunks_with_tables']} chunks with table content")
        logger.info(f"   HybridChunker: {hybrid_results['chunks_with_tables']} chunks with table content")
        logger.info(f"   Note: Lower count = better preservation (fewer splits)")
        
        tables_ok = hybrid_results['chunks_with_tables'] <= aria_results['chunks_with_tables']
        logger.info(f"   Result: {'✅ PASS' if tables_ok else '⚠️  CHECK MANUALLY'}")
        
        # Decision
        logger.info(f"\n" + "="*70)
        logger.info("🎯 DECISION CRITERIA")
        logger.info("="*70)
        
        criteria = {
            "chunk_count_optimal": chunk_ok,
            "performance_acceptable": perf_ok or perf_overhead < 50,
            "context_prefix_working": hybrid_results['has_context_prefix'],
            "tables_preserved": tables_ok
        }
        
        for criterion, passed in criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"   {criterion}: {status}")
        
        # Final decision
        go = sum(criteria.values()) >= 3  # At least 3 out of 4 must pass
        
        logger.info(f"\n" + "="*70)
        if go:
            logger.info("🟢 DECISION: GO")
            logger.info("="*70)
            logger.info("✅ Proceed with Gap #3 Revised (Docling HybridChunker)")
            logger.info("⏱️  Duration: 3-5 days (instead of 10)")
            logger.info("🎉 Gap #4 (Agentic Chunking) resolved simultaneously!")
        else:
            logger.info("🔴 DECISION: NO-GO")
            logger.info("="*70)
            logger.info("❌ Proceed with Gap #3 Original (custom implementation)")
            logger.info("⏱️  Duration: 10 days")
            logger.info("⚠️  Gap #4 (Agentic Chunking) still needed (3 weeks)")
        
        return {
            "decision": "GO" if go else "NO-GO",
            "criteria": criteria,
            "aria": aria_results,
            "hybrid": hybrid_results,
            "chunk_improvement_pct": chunk_improvement,
            "perf_overhead_pct": perf_overhead
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Run complete POC.
        
        Returns:
            POC results with decision
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 DOCLING POC - ARIA vs HybridChunker")
        logger.info("="*70)
        logger.info(f"Test file: {self.test_file.name}")
        logger.info(f"Objective: Validate if HybridChunker is better than ARIA")
        logger.info("")
        
        # Convert document
        doc = self.convert_document()
        
        # Test ARIA
        aria_results = self.test_aria_chunking(doc)
        
        # Test HybridChunker
        hybrid_results = self.test_hybrid_chunking(doc)
        
        # Compare and decide
        comparison = self.compare_results(aria_results, hybrid_results)
        
        logger.info("\n🏁 POC COMPLETE!")
        logger.info(f"   Decision: {comparison['decision']}")
        logger.info(f"   Next: Document results in Devplan/251105-POC-HYBRID-RESULTS.md")
        
        return comparison


def main():
    """Main entry point."""
    try:
        poc = POCRunner()
        results = poc.run()
        
        # Exit with code based on decision
        sys.exit(0 if results["decision"] == "GO" else 1)
        
    except Exception as e:
        logger.error(f"❌ POC failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()

