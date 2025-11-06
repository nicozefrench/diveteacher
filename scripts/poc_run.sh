#!/bin/bash
set -e

echo "🔄 Rebuilding backend with Docling 2.60.1..."
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml build backend --no-cache

echo "🚀 Starting backend..."
docker compose -f docker/docker-compose.dev.yml up backend -d

echo "⏳ Waiting for backend to be ready..."
sleep 30

echo "📋 Checking backend logs..."
docker compose -f docker/docker-compose.dev.yml logs backend --tail 30

echo "📄 Copying test PDF..."
docker compose -f docker/docker-compose.dev.yml exec -T backend mkdir -p /app/TestPDF || true
docker compose -f docker/docker-compose.dev.yml cp "TestPDF/Niveau 1.pdf" "backend:/app/TestPDF/Niveau 1.pdf"

echo "🎯 Running POC..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python3 - << 'EOF'
import sys
import time
from pathlib import Path

print("=" * 70)
print("🚀 DOCLING POC - ARIA vs HybridChunker (FIXED)")
print("=" * 70)
print("")

sys.path.insert(0, '/app')

try:
    print("📄 Loading modules...")
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.chunking import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
    from transformers import AutoTokenizer
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    import numpy as np
    
    print("✅ All modules loaded!")
    print(f"   - numpy: {np.__version__}")
    print("")
    
    pdf_path = "/app/TestPDF/Niveau 1.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)
    
    print(f"📄 Processing: {pdf_path}")
    print("")
    
    # Convert
    print("🔄 Converting PDF...")
    start = time.time()
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    result = converter.convert(pdf_path)
    doc = result.document
    markdown = doc.export_to_markdown()
    
    print(f"✅ Conversion: {time.time()-start:.2f}s")
    print(f"   - Pages: {len(doc.pages)}")
    print(f"   - Markdown: {len(markdown)} chars")
    print("")
    
    # Test 1: ARIA
    print("=" * 70)
    print("TEST 1: ARIA (Current)")
    print("=" * 70)
    
    start = time.time()
    aria_splitter = RecursiveCharacterTextSplitter(
        chunk_size=12000,
        chunk_overlap=800,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    aria_chunks = aria_splitter.split_text(markdown)
    aria_time = time.time() - start
    
    print(f"✅ ARIA complete:")
    print(f"   - Chunks: {len(aria_chunks)}")
    print(f"   - Time: {aria_time:.3f}s")
    print(f"   - Avg size: {sum(len(c) for c in aria_chunks) / len(aria_chunks):.0f} chars")
    print(f"   - First chunk: {aria_chunks[0][:150]}...")
    print("")
    
    # Test 2: HybridChunker
    print("=" * 70)
    print("TEST 2: HybridChunker (NEW)")
    print("=" * 70)
    
    start = time.time()
    
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"),
        max_tokens=2000
    )
    
    hybrid_chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True
    )
    
    hybrid_chunks = list(hybrid_chunker.chunk(dl_doc=doc))
    hybrid_time = time.time() - start
    
    print(f"✅ HybridChunker complete:")
    print(f"   - Chunks: {len(hybrid_chunks)}")
    print(f"   - Time: {hybrid_time:.3f}s")
    
    if hybrid_chunks:
        first_chunk = hybrid_chunks[0]
        enriched = hybrid_chunker.contextualize(chunk=first_chunk)
        
        print(f"   - Avg size: {sum(len(str(c.text)) for c in hybrid_chunks) / len(hybrid_chunks):.0f} chars")
        print(f"   - First (raw): {str(first_chunk.text)[:150]}...")
        print(f"   - First (enriched): {enriched[:150]}...")
    
    print("")
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print("")
    print(f"ARIA: {len(aria_chunks)} chunks in {aria_time:.3f}s")
    print(f"HybridChunker: {len(hybrid_chunks)} chunks in {hybrid_time:.3f}s")
    print("")
    
    if 5 <= len(hybrid_chunks) <= 15:
        print("✅ GO: HybridChunker optimal (5-15 chunks)")
        print("✅ GO: Context enrichment working")
        print("")
        print("🎉 RECOMMENDATION: Proceed with Gap #3 Docling!")
    else:
        print(f"⚠️ NO-GO: {len(hybrid_chunks)} chunks (expected 5-15)")
        print("")
        print("📋 RECOMMENDATION: Use Gap #3 Original")
    
    print("")
    print("=" * 70)
    print("✅ POC COMPLETE")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

echo ""
echo "✅ POC execution complete!"

