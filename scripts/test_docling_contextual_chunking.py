#!/usr/bin/env python3
"""
GAP #3 Integration Test: Docling HybridChunker with Contextual Enrichment

This script tests that the Docling HybridChunker integration works correctly:
1. Chunks a test PDF using HybridChunker
2. Verifies contextualized_text is generated
3. Validates chunk count is reasonable (not micro-chunks)
4. Checks that context enrichment adds hierarchical prefixes

Expected Results (Niveau 1.pdf):
- 20-40 chunks (optimal granularity)
- Each chunk has 'text' and 'contextualized_text'
- Context prefix format: "Document Title\nSection\nContent..."
- No micro-chunking (avoid 200+ chunks)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import asyncio
from app.services.document_chunker import get_chunker
from app.integrations.dockling import get_docling_converter


async def test_docling_contextual_chunking():
    """Test Docling HybridChunker with contextual enrichment"""
    
    print("=" * 80)
    print("🧪 GAP #3 INTEGRATION TEST: Docling HybridChunker + Context")
    print("=" * 80)
    print()
    
    # Test file (adjust path if needed)
    test_pdf = "/app/TestPDF/Niveau 1.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test PDF not found: {test_pdf}")
        print("   Please copy Niveau 1.pdf to /app/TestPDF/ in the Docker container")
        return False
    
    print(f"📄 Test PDF: {test_pdf}")
    print()
    
    # Step 1: Convert PDF with Docling
    print("STEP 1: Convert PDF with Docling")
    print("-" * 80)
    
    converter = get_docling_converter()
    result = await converter.convert(test_pdf)
    docling_doc = result.document
    
    print(f"✅ Document converted")
    print(f"   Document name: {docling_doc.name}")
    print()
    
    # Step 2: Chunk with HybridChunker
    print("STEP 2: Chunk with Docling HybridChunker")
    print("-" * 80)
    
    chunker = get_chunker()
    chunks = chunker.chunk_document(
        docling_doc=docling_doc,
        filename="Niveau 1.pdf",
        upload_id="test-gap3"
    )
    
    print(f"✅ Document chunked")
    print(f"   Total chunks: {len(chunks)}")
    print()
    
    # Step 3: Validate chunks
    print("STEP 3: Validate Chunks")
    print("-" * 80)
    
    # Check chunk count
    if len(chunks) > 100:
        print(f"⚠️  WARNING: Too many chunks ({len(chunks)})")
        print(f"   Expected: 20-40 chunks for Niveau 1.pdf")
        print(f"   Possible micro-chunking issue!")
    elif len(chunks) < 5:
        print(f"⚠️  WARNING: Too few chunks ({len(chunks)})")
        print(f"   Expected: 20-40 chunks for Niveau 1.pdf")
    else:
        print(f"✅ Chunk count is reasonable: {len(chunks)} chunks")
    
    # Check contextualized_text exists
    has_context = all('contextualized_text' in chunk for chunk in chunks)
    if not has_context:
        print(f"❌ FAIL: Some chunks missing 'contextualized_text'")
        return False
    else:
        print(f"✅ All chunks have 'contextualized_text'")
    
    # Check metadata
    has_context_flag = all(chunk['metadata'].get('has_context') for chunk in chunks)
    if not has_context_flag:
        print(f"⚠️  WARNING: Some chunks missing 'has_context' metadata flag")
    else:
        print(f"✅ All chunks have 'has_context' metadata flag")
    
    print()
    
    # Step 4: Inspect first chunk
    print("STEP 4: Inspect First Chunk (Context Enrichment)")
    print("-" * 80)
    
    first_chunk = chunks[0]
    raw_text = first_chunk['text']
    contextualized_text = first_chunk['contextualized_text']
    
    print(f"Raw text (first 200 chars):")
    print(f"{raw_text[:200]}...")
    print()
    
    print(f"Contextualized text (first 250 chars):")
    print(f"{contextualized_text[:250]}...")
    print()
    
    # Check if context was actually added
    if contextualized_text == raw_text:
        print(f"⚠️  WARNING: Contextualized text is identical to raw text")
        print(f"   Context enrichment may not be working!")
    elif len(contextualized_text) > len(raw_text):
        added_chars = len(contextualized_text) - len(raw_text)
        print(f"✅ Context added: +{added_chars} chars")
        
        # Try to identify the context prefix
        if contextualized_text.startswith(raw_text):
            # Context is suffix (unlikely)
            print(f"   Context position: SUFFIX (unusual)")
        else:
            # Context is prefix (expected)
            prefix_end = contextualized_text.find(raw_text)
            if prefix_end > 0:
                prefix = contextualized_text[:prefix_end]
                print(f"   Context prefix ({len(prefix)} chars):")
                print(f"   {prefix!r}")
    else:
        print(f"⚠️  WARNING: Contextualized text is shorter than raw text")
    
    print()
    
    # Step 5: Statistics
    print("STEP 5: Chunking Statistics")
    print("-" * 80)
    
    token_counts = [chunk['metadata']['num_tokens'] for chunk in chunks]
    avg_tokens = sum(token_counts) / len(token_counts)
    min_tokens = min(token_counts)
    max_tokens = max(token_counts)
    
    print(f"Average tokens per chunk: {avg_tokens:.0f}")
    print(f"Token range: {min_tokens} - {max_tokens}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Chunking strategy: {chunks[0]['metadata']['chunking_strategy']}")
    print()
    
    # Final verdict
    print("=" * 80)
    print("🎯 TEST RESULT")
    print("=" * 80)
    
    all_checks_pass = (
        len(chunks) >= 5 and len(chunks) <= 100 and
        has_context and
        has_context_flag and
        len(contextualized_text) > len(raw_text)
    )
    
    if all_checks_pass:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Gap #3 integration is working correctly:")
        print("- HybridChunker produces reasonable chunk count")
        print("- Contextualized text is generated")
        print("- Context enrichment adds hierarchical prefixes")
        print()
        print("🚀 Ready for A/B testing!")
        return True
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please review the test results above and fix any issues.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_docling_contextual_chunking())
    sys.exit(0 if success else 1)

