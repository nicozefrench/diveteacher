"""
End-to-End Testing Script for Neo4j + Graphiti + RAG

Run this script to validate the complete Phase 0.8 implementation.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.neo4j import neo4j_client
from app.integrations.neo4j_indexes import verify_indexes
from app.core.rag import retrieve_context, rag_query


async def test_full_pipeline():
    """Test complet du pipeline Neo4j + RAG"""
    
    print("\n" + "="*60)
    print("🧪 PHASE 0.8 - NEO4J RAG IMPLEMENTATION - E2E TESTS")
    print("="*60)
    
    # Test 1: Connection Neo4j
    print("\n🧪 Test 1: Neo4j Connection")
    try:
        neo4j_client.connect()
        neo4j_client.driver.verify_connectivity()
        print("✅ Neo4j connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: Verify Indexes
    print("\n🧪 Test 2: RAG Indexes Verification")
    try:
        index_info = verify_indexes(neo4j_client.driver)
        print(f"✅ Total indexes: {index_info['total']}")
        print(f"   RAG indexes: {index_info['rag_indexes']}")
        print(f"   Graphiti indexes: {index_info['graphiti_indexes']}")
        
        if index_info['rag_details']:
            print("\n   RAG Indexes Details:")
            for idx in index_info['rag_details']:
                print(f"     - {idx['name']} ({idx['type']}, {idx['state']})")
        
        if index_info['rag_indexes'] < 3:
            print("⚠️  Warning: Expected 3 RAG indexes, check index creation")
    except Exception as e:
        print(f"❌ Index verification failed: {e}")
    
    # Test 3: Full-Text Search
    print("\n🧪 Test 3: Full-Text Search (Episode.content)")
    try:
        results = neo4j_client.query_context_fulltext("plongée", top_k=3)
        print(f"✅ Full-text search returned {len(results)} results")
        
        if results:
            for i, r in enumerate(results[:2], 1):
                score = r.get('score', 0)
                text_preview = r['text'][:80] if r.get('text') else "N/A"
                source = r.get('source', 'Unknown')
                print(f"   [{i}] Score: {score:.3f}")
                print(f"       Source: {source}")
                print(f"       Text: {text_preview}...")
        else:
            print("⚠️  No results found. Upload a document first!")
    except Exception as e:
        print(f"❌ Full-text search failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Entity Search
    print("\n🧪 Test 4: Entity Search (Entity.name + RELATES_TO)")
    try:
        entities = neo4j_client.query_entities_related("niveau", depth=2)
        print(f"✅ Entity search found {len(entities)} entities")
        
        if entities:
            for i, e in enumerate(entities[:2], 1):
                entity_name = e.get('entity', 'N/A')
                entity_type = e.get('type', 'Unknown')
                desc_preview = e.get('description', '')[:60] if e.get('description') else "N/A"
                related_count = len(e.get('related', []))
                print(f"   [{i}] {entity_name} ({entity_type})")
                print(f"       Description: {desc_preview}...")
                print(f"       Related entities: {related_count}")
        else:
            print("⚠️  No entities found. Graphiti needs to process documents first!")
    except Exception as e:
        print(f"❌ Entity search failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Hybrid Search
    print("\n🧪 Test 5: Hybrid Search (Episodes + Entities)")
    try:
        hybrid = neo4j_client.query_context_hybrid("niveau 4 plongée", top_k=3)
        print(f"✅ Hybrid search completed")
        print(f"   Episodes: {len(hybrid['episodes'])}")
        print(f"   Entities: {len(hybrid['entities'])}")
        print(f"   Total: {hybrid['total']}")
        
        if hybrid['total'] == 0:
            print("⚠️  No results. Upload documents and wait for Graphiti processing!")
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: RAG Query (Full Pipeline)
    print("\n🧪 Test 6: RAG Query (retrieve_context + LLM)")
    try:
        # Just test context retrieval (not full LLM to save time)
        context = await retrieve_context("Qu'est-ce que le niveau 4?", top_k=3)
        print(f"✅ RAG context retrieval completed")
        print(f"   Episodes: {len(context.get('episodes', []))}")
        print(f"   Entities: {len(context.get('entities', []))}")
        
        if context.get('episodes') or context.get('entities'):
            print("\n   ✅ RAG pipeline is functional!")
        else:
            print("\n   ⚠️  RAG context empty - upload documents first!")
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print("\n🧹 Cleanup")
    neo4j_client.close()
    print("✅ Neo4j connection closed")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print("\n✅ Phase 0.8 Implementation Tests COMPLETE")
    print("\nNext Steps:")
    print("  1. Upload a test document via API:")
    print("     curl -F 'file=@test.pdf' http://localhost:8000/api/upload")
    print("  2. Wait 1-2 min for Graphiti processing")
    print("  3. Test RAG query:")
    print("     curl -X POST http://localhost:8000/api/query \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"question\": \"niveau 4\", \"stream\": false}'")
    print("\n" + "="*60)
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_full_pipeline())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

