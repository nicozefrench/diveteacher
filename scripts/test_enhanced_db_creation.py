#!/usr/bin/env python3
"""
GAP #3 DAY 2.3: Create Enhanced Database (Docling HybridChunker)

This script:
1. Uploads Niveau 1.pdf via the backend API
2. Monitors ingestion progress
3. Validates that chunks are contextualized
4. Creates a test database for A/B testing

Expected Results:
- 20-40 chunks created (Docling HybridChunker)
- Each chunk has contextualized_text with hierarchy
- Ingestion completes successfully
- Database ready for query testing (Day 2.4)
"""
import os
import sys
import time
import json
import requests
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
PDF_PATH = "/Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter/TestPDF/Niveau 1.pdf"
POLL_INTERVAL = 2  # seconds

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def upload_document(file_path: str) -> dict:
    """
    Upload document to backend API
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        dict with upload_id and status
    """
    print_header("STEP 1: Upload Niveau 1.pdf")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"📄 File: {Path(file_path).name}")
    print(f"📦 Size: {file_size_mb:.2f} MB")
    
    # Upload
    print(f"\n📤 Uploading to {BACKEND_URL}/api/upload...")
    
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f, 'application/pdf')}
        response = requests.post(f"{BACKEND_URL}/api/upload", files=files, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    result = response.json()
    upload_id = result['upload_id']
    status = result['status']
    
    print(f"✅ Upload successful!")
    print(f"   Upload ID: {upload_id}")
    print(f"   Status: {status}")
    
    return result

def monitor_processing(upload_id: str) -> dict:
    """
    Monitor document processing until complete
    
    Args:
        upload_id: Upload ID from upload_document()
        
    Returns:
        Final status dict
    """
    print_header("STEP 2: Monitor Processing")
    
    print(f"🔍 Monitoring upload_id: {upload_id}")
    print(f"   Polling every {POLL_INTERVAL}s...\n")
    
    start_time = time.time()
    last_stage = None
    last_progress = -1
    
    while True:
        # Get status
        response = requests.get(f"{BACKEND_URL}/api/upload/{upload_id}/status", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Status check failed: {response.status_code}")
            sys.exit(1)
        
        status = response.json()
        current_status = status.get('status', 'unknown')
        current_stage = status.get('stage', 'unknown')
        current_progress = status.get('progress', 0)
        
        # Print updates
        if current_stage != last_stage or current_progress != last_progress:
            elapsed = time.time() - start_time
            print(f"[{elapsed:6.1f}s] {current_status:12} | {current_stage:20} | {current_progress:3}%")
            
            # Print ingestion progress if available
            if 'ingestion_progress' in status and status['ingestion_progress']:
                ing_progress = status['ingestion_progress']
                chunks_completed = ing_progress.get('chunks_completed', 0)
                chunks_total = ing_progress.get('chunks_total', 0)
                if chunks_total > 0:
                    print(f"         └─ Chunks: {chunks_completed}/{chunks_total}")
            
            last_stage = current_stage
            last_progress = current_progress
        
        # Check if complete
        if current_status == 'completed':
            elapsed = time.time() - start_time
            print(f"\n✅ Processing complete in {elapsed:.1f}s!")
            return status
        
        # Check if failed
        if current_status == 'failed':
            print(f"\n❌ Processing failed!")
            print(json.dumps(status, indent=2))
            sys.exit(1)
        
        # Wait before next poll
        time.sleep(POLL_INTERVAL)

def validate_contextualization(upload_id: str, status: dict):
    """
    Validate that chunks are properly contextualized
    
    Args:
        upload_id: Upload ID
        status: Final status dict from monitor_processing()
    """
    print_header("STEP 3: Validate Contextualization")
    
    # Extract metrics
    metrics = status.get('metrics', {})
    
    # Check chunking metrics
    if 'chunking' in metrics:
        chunking = metrics['chunking']
        total_chunks = chunking.get('total_chunks', 0)
        chunking_method = chunking.get('chunking_method', 'unknown')
        has_context = chunking.get('has_context', False)
        
        print(f"📊 Chunking Metrics:")
        print(f"   Total chunks: {total_chunks}")
        print(f"   Chunking method: {chunking_method}")
        print(f"   Has context: {has_context}")
        
        # Validate
        if chunking_method != "Docling HybridChunker":
            print(f"❌ ERROR: Expected 'Docling HybridChunker', got '{chunking_method}'")
            sys.exit(1)
        
        if not has_context:
            print(f"❌ ERROR: Chunks do not have contextual enrichment!")
            sys.exit(1)
        
        if not (20 <= total_chunks <= 40):
            print(f"⚠️  WARNING: Chunk count {total_chunks} is outside optimal range (20-40)")
        
        print(f"✅ Chunking validation passed!")
    else:
        print(f"⚠️  WARNING: No chunking metrics found in status")
    
    # Check ingestion metrics
    if 'ingestion' in metrics:
        ingestion = metrics['ingestion']
        episodes_added = ingestion.get('episodes_added', 0)
        entities_found = ingestion.get('entities_found', 0)
        relations_found = ingestion.get('relations_found', 0)
        
        print(f"\n📊 Ingestion Metrics:")
        print(f"   Episodes added: {episodes_added}")
        print(f"   Entities found: {entities_found}")
        print(f"   Relations found: {relations_found}")
        
        if episodes_added == 0:
            print(f"❌ ERROR: No episodes added to Graphiti!")
            sys.exit(1)
        
        print(f"✅ Ingestion validation passed!")
    else:
        print(f"⚠️  WARNING: No ingestion metrics found in status")

def test_query(query: str):
    """
    Test a sample query to verify database is functional
    
    Args:
        query: Test query string
    """
    print_header("STEP 4: Test Query")
    
    print(f"🔍 Query: \"{query}\"")
    
    response = requests.post(
        f"{BACKEND_URL}/api/query",
        json={"query": query},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    result = response.json()
    answer = result.get('answer', '')
    sources = result.get('context', {}).get('sources', [])
    
    print(f"✅ Query successful!")
    print(f"\n📝 Answer (first 200 chars):")
    print(f"   {answer[:200]}...")
    print(f"\n📚 Sources: {len(sources)} chunks retrieved")
    
    if sources:
        first_source = sources[0]
        print(f"\n📄 First source (preview):")
        print(f"   Score: {first_source.get('score', 'N/A')}")
        print(f"   Text: {first_source.get('text', '')[:100]}...")

def main():
    """Main execution flow"""
    print_header("GAP #3 DAY 2.3: CREATE ENHANCED DATABASE")
    print("Using: Docling HybridChunker with Contextual Enrichment")
    print("File: Niveau 1.pdf")
    print("Expected: 20-40 contextualized chunks")
    
    # Step 1: Upload
    upload_result = upload_document(PDF_PATH)
    upload_id = upload_result['upload_id']
    
    # Step 2: Monitor
    final_status = monitor_processing(upload_id)
    
    # Step 3: Validate
    validate_contextualization(upload_id, final_status)
    
    # Step 4: Test query
    test_query("Quelle est la profondeur maximale pour un plongeur niveau 1?")
    
    # Final summary
    print_header("✅ DAY 2.3 COMPLETE!")
    print("Enhanced database created successfully with Docling HybridChunker")
    print("Database ready for A/B testing (Day 2.4)")
    print(f"\nUpload ID: {upload_id}")
    print("Next step: Run A/B test with 20 queries from niveau1_test_queries.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

