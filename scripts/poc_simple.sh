#!/bin/bash
# Simple POC: Compare ARIA vs Docling HybridChunker
# Run inside Docker backend container

set -e

echo "======================================================================"
echo "🚀 DOCLING POC - ARIA vs HybridChunker"
echo "======================================================================"
echo ""

# Python inline POC script
docker compose -f docker/docker-compose.dev.yml exec -T backend python3 << 'PYTHON_SCRIPT'
import sys
import time
from pathlib import Path

print("📄 Loading modules...")
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("✅ Modules loaded\n")

# Config
TEST_FILE = "/app/TestPDF/Niveau 1.pdf"
ARIA_CHUNK_SIZE = 3000
ARIA_OVERLAP = 200
CHARS_PER_TOKEN = 4
HYBRID_MAX_TOKENS = 2000

print("====================================================================")
print("STEP 1: Convert document with Docling")
print("====================================================================")

# Initialize converter
pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

start = time.time()
result = converter.convert(source=TEST_FILE)
doc = result.document
conversion_time = time.time() - start

print(f"✅ Conversion complete in {conversion_time:.2f}s")
print(f"   Pages: {getattr(doc, 'num_pages', 'N/A')}")
print(f"   Tables: {len(doc.tables)}")

# Extract markdown
markdown = doc.export_to_markdown()
print(f"   Markdown: {len(markdown)} chars (~{len(markdown)//CHARS_PER_TOKEN} tokens)\n")

print("====================================================================")
print("STEP 2: Test ARIA Pattern (Current Production)")
print("====================================================================")

start = time.time()
splitter = RecursiveCharacterTextSplitter(
    chunk_size=ARIA_CHUNK_SIZE * CHARS_PER_TOKEN,
    chunk_overlap=ARIA_OVERLAP * CHARS_PER_TOKEN,
    separators=["\n\n", "\n", ". ", " ", ""]
)
aria_chunks = splitter.split_text(markdown)
aria_time = time.time() - start

aria_sizes = [len(c)//CHARS_PER_TOKEN for c in aria_chunks]
aria_avg = sum(aria_sizes) / len(aria_sizes)

print(f"✅ ARIA Results:")
print(f"   Chunks: {len(aria_chunks)}")
print(f"   Avg size: {aria_avg:.0f} tokens")
print(f"   Range: {min(aria_sizes)}-{max(aria_sizes)} tokens")
print(f"   Duration: {aria_time:.2f}s")
print(f"   Sample (first 150 chars): {aria_chunks[0][:150]}...\n")

print("====================================================================")
print("STEP 3: Test Docling HybridChunker (Proposed)")
print("====================================================================")

start = time.time()
tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"),
    max_tokens=HYBRID_MAX_TOKENS
)
chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
hybrid_chunks = list(chunker.chunk(dl_doc=doc))
hybrid_time = time.time() - start

hybrid_sizes = [len(c.text.split()) for c in hybrid_chunks]
hybrid_avg = sum(hybrid_sizes) / len(hybrid_sizes) if hybrid_sizes else 0

print(f"✅ HybridChunker Results:")
print(f"   Chunks: {len(hybrid_chunks)}")
print(f"   Avg size: {hybrid_avg:.0f} tokens")
print(f"   Range: {min(hybrid_sizes) if hybrid_sizes else 0}-{max(hybrid_sizes) if hybrid_sizes else 0} tokens")
print(f"   Duration: {hybrid_time:.2f}s")

# Test contextualize()
if hybrid_chunks:
    contextualized = chunker.contextualize(chunk=hybrid_chunks[0])
    has_prefix = len(contextualized) > len(hybrid_chunks[0].text)
    print(f"   Context prefix: {'YES ✅' if has_prefix else 'NO ❌'}")
    print(f"   Sample (first 200 chars): {contextualized[:200]}...\n")
else:
    has_prefix = False
    print("   ⚠️  No chunks generated!\n")

print("====================================================================")
print("STEP 4: Comparison & Decision")
print("====================================================================")

# Calculate metrics
chunk_reduction = (len(aria_chunks) - len(hybrid_chunks)) / len(aria_chunks) * 100
perf_overhead = (hybrid_time - aria_time) / aria_time * 100

print(f"\n1️⃣  Chunk Count:")
print(f"   ARIA: {len(aria_chunks)} chunks")
print(f"   HybridChunker: {len(hybrid_chunks)} chunks")
print(f"   Improvement: {chunk_reduction:+.1f}% {'✅' if chunk_reduction > 0 else '❌'}")
print(f"   Target: 5-10 chunks")
chunk_ok = 5 <= len(hybrid_chunks) <= 10
print(f"   Status: {'✅ PASS' if chunk_ok else '❌ FAIL'}")

print(f"\n2️⃣  Performance:")
print(f"   ARIA: {aria_time:.2f}s")
print(f"   HybridChunker: {hybrid_time:.2f}s")
print(f"   Overhead: {perf_overhead:+.1f}%")
perf_ok = perf_overhead < 20
print(f"   Status: {'✅ PASS' if perf_ok else '⚠️  ACCEPTABLE' if perf_overhead < 50 else '❌ FAIL'}")

print(f"\n3️⃣  Context Prefix:")
print(f"   ARIA: ❌ None")
print(f"   HybridChunker: {'✅ YES' if has_prefix else '❌ NO'}")
print(f"   Status: {'✅ PASS' if has_prefix else '❌ FAIL'}")

print(f"\n====================================================================")
print("DECISION")
print("====================================================================")

criteria_pass = sum([chunk_ok, perf_ok or perf_overhead < 50, has_prefix])
go = criteria_pass >= 2

if go:
    print("🟢 DECISION: GO")
    print("✅ Proceed with Gap #3 Revised (Docling HybridChunker)")
    print("⏱️  Duration: 3-5 days (instead of 10)")
    print("🎉 Gap #4 resolved simultaneously!")
    sys.exit(0)
else:
    print("🔴 DECISION: NO-GO")
    print("❌ Proceed with Gap #3 Original (custom implementation)")
    print("⏱️  Duration: 10 days")
    sys.exit(1)

PYTHON_SCRIPT

EXIT_CODE=$?

echo ""
echo "======================================================================"
echo "POC COMPLETE!"
echo "======================================================================"

exit $EXIT_CODE

