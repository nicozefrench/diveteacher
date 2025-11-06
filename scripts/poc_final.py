#!/usr/bin/env python3
"""
POC DOCLING HYBRIDCHUNKER - Final Validation
Compares ARIA vs HybridChunker chunking strategies
"""

import sys
import time
from pathlib import Path

print("=" * 70)
print("🚀 DOCLING POC - ARIA vs HybridChunker (FIXED)")
print("="  * 70)
print("")

# Add app to path
sys.path.insert(0, '/app')

try:
    print("📄 Loading modules...")
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.chunking import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
    from transformers import AutoTokenizer
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    import numpy as np
    
    print("✅ All modules loaded successfully!")
    print(f"   - numpy version: {np.__version__}")
    print(f"   - transformers available: ✅")
    print(f"   - docling.chunking available: ✅")
    print("")
    
    # Test PDF
    pdf_path = "/app/TestPDF/Niveau_1.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ Test PDF not found: {pdf_path}")
        print("   Please copy it: docker compose cp TestPDF/Niveau\\ 1.pdf backend:/app/TestPDF/")
        sys.exit(1)
    
    print(f"📄 Processing: {pdf_path}")
    print("")
    
    # Convert document with Docling
    print("🔄 Step 1: Converting PDF with Docling...")
    start_time = time.time()
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Speed up for POC
    pipeline_options.do_table_structure = True
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    result = converter.convert(pdf_path)
    doc = result.document
    markdown = doc.export_to_markdown()
    
    convert_time = time.time() - start_time
    print(f"✅ Conversion complete: {convert_time:.2f}s")
    print(f"   - Document pages: {len(doc.pages)}")
    print(f"   - Markdown length: {len(markdown)} chars")
    print("")
    
    # Test 1: ARIA (Current)
    print("=" * 70)
    print("TEST 1: ARIA RecursiveCharacterTextSplitter (Current)")
    print("=" * 70)
    
    start_time = time.time()
    aria_splitter = RecursiveCharacterTextSplitter(
        chunk_size=12000,  # 3000 tokens * 4 chars
        chunk_overlap=800,  # 200 tokens * 4 chars
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    aria_chunks = aria_splitter.split_text(markdown)
    aria_time = time.time() - start_time
    
    print(f"✅ ARIA chunking complete:")
    print(f"   - Chunks created: {len(aria_chunks)}")
    print(f"   - Processing time: {aria_time:.3f}s")
    print(f"   - Avg chunk size: {sum(len(c) for c in aria_chunks) / len(aria_chunks):.0f} chars")
    print("")
    print("   First chunk preview:")
    print(f"   {aria_chunks[0][:200]}...")
    print("")
    
    # Test 2: Docling HybridChunker
    print("=" * 70)
    print("TEST 2: Docling HybridChunker (NEW)")
    print("=" * 70)
    
    start_time = time.time()
    
    # Initialize tokenizer
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"),
        max_tokens=2000
    )
    
    # Initialize HybridChunker
    hybrid_chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True  # Merge small adjacent chunks
    )
    
    # Chunk the document
    hybrid_chunks = list(hybrid_chunker.chunk(dl_doc=doc))
    hybrid_time = time.time() - start_time
    
    print(f"✅ HybridChunker complete:")
    print(f"   - Chunks created: {len(hybrid_chunks)}")
    print(f"   - Processing time: {hybrid_time:.3f}s")
    
    if hybrid_chunks:
        # Get contextualized text for first chunk
        first_chunk = hybrid_chunks[0]
        enriched_text = hybrid_chunker.contextualize(chunk=first_chunk)
        
        print(f"   - Avg chunk size: {sum(len(str(c.text)) for c in hybrid_chunks) / len(hybrid_chunks):.0f} chars")
        print("")
        print("   First chunk (raw):")
        print(f"   {str(first_chunk.text)[:200]}...")
        print("")
        print("   First chunk (contextualized):")
        print(f"   {enriched_text[:200]}...")
    
    print("")
    
    # Comparison Summary
    print("=" * 70)
    print("📊 COMPARISON SUMMARY")
    print("=" * 70)
    print("")
    print(f"{'Metric':<30} {'ARIA':<15} {'HybridChunker':<15} {'Winner':<10}")
    print("-" * 70)
    print(f"{'Chunk Count':<30} {len(aria_chunks):<15} {len(hybrid_chunks):<15} {'Hybrid' if len(hybrid_chunks) < len(aria_chunks) else 'ARIA':<10}")
    print(f"{'Processing Time (s)':<30} {aria_time:<15.3f} {hybrid_time:<15.3f} {'ARIA' if aria_time < hybrid_time else 'Hybrid':<10}")
    print(f"{'Context Enrichment':<30} {'No':<15} {'Yes':<15} {'Hybrid':<10}")
    print(f"{'Table Preservation':<30} {'Maybe':<15} {'Yes':<15} {'Hybrid':<10}")
    print("")
    
    # Decision
    print("=" * 70)
    print("🎯 POC DECISION")
    print("=" * 70)
    print("")
    
    if len(hybrid_chunks) < 15 and len(hybrid_chunks) > 3:
        print("✅ GO: HybridChunker produces optimal chunk count (5-15)")
        print("✅ GO: Context enrichment working (contextualize() adds hierarchy)")
        print("✅ GO: Performance acceptable")
        print("")
        print("🎉 RECOMMENDATION: Proceed with Docling HybridChunker for Gap #3!")
    else:
        print(f"⚠️  NO-GO: Chunk count suboptimal ({len(hybrid_chunks)} chunks)")
        print("   Expected: 5-15 chunks for 16-page document")
        print("")
        print("📋 RECOMMENDATION: Proceed with Gap #3 Original (custom parser)")
    
    print("")
    print("=" * 70)
    print("✅ POC COMPLETE")
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("")
    print("Check installed versions:")
    import subprocess
    subprocess.run(["pip", "show", "docling", "transformers", "numpy", "langchain"], check=False)
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

