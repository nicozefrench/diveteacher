"""
Graphiti Integration avec OpenAI GPT-5-nano

Architecture:
- Graphiti: OpenAI GPT-5-nano (entity extraction) + text-embedding-3-small (embeddings)
- RAG/User: Mistral 7b sur Ollama (séparé, pas de mélange!)
"""
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from openai import AsyncOpenAI
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.llm_client import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.search.search_config_recipes import EDGE_HYBRID_SEARCH_RRF
from graphiti_core.search.search_config import SearchConfig

from app.core.config import settings
from app.integrations.custom_llm_client import Gpt5NanoClient

logger = logging.getLogger('diveteacher.graphiti')


# Global Graphiti client (singleton pattern)
_graphiti_client: Optional[Graphiti] = None
_indices_built: bool = False


async def get_graphiti_client() -> Graphiti:
    """
    Get or create Graphiti client singleton avec OpenAI GPT-5-nano explicite
    
    Returns:
        Initialized Graphiti client
        
    Note:
        - Build indices only once on first call
        - Reuse same client for all operations
        - Uses explicit OpenAI config:
          * LLM: gpt-5-nano (entity extraction, 2M TPM)
          * Embedder: text-embedding-3-small (vectorization)
          * CrossEncoder: gpt-5-nano (reranking)
        - Requires OPENAI_API_KEY in environment
    """
    global _graphiti_client, _indices_built
    
    if _graphiti_client is None:
        if not settings.GRAPHITI_ENABLED:
            raise RuntimeError("Graphiti is disabled in settings")
        
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY required for Graphiti (not found in settings)")
        
        logger.info("🔧 Initializing Graphiti client with explicit OpenAI configuration...")
        logger.info(f"   LLM Model: {settings.OPENAI_MODEL}")
        logger.info(f"   Embedder: text-embedding-3-small")
        
        # ════════════════════════════════════════════════════════
        # Configuration OpenAI explicite pour Graphiti
        # ════════════════════════════════════════════════════════
        
        # Client OpenAI async (partagé entre LLM et Embedder)
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # LLM Config pour gpt-5-nano (entity extraction + relation detection)
        llm_config = LLMConfig(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,        # gpt-5-nano
            small_model=settings.OPENAI_MODEL,  # gpt-5-nano aussi
            max_tokens=4096  # ✅ Limite explicite pour éviter overflow (8K max)
        )
        
        # LLM Client CUSTOM pour gpt-5-nano (utilise max_completion_tokens)
        llm_client = Gpt5NanoClient(
            config=llm_config,
            client=openai_client
        )
        
        # Embedder Config pour text-embedding-3-small (vectorization)
        embedder_config = OpenAIEmbedderConfig(
            api_key=settings.OPENAI_API_KEY,
            embedding_model="text-embedding-3-small",
            embedding_dim=1536  # Dimension de text-embedding-3-small
        )
        
        embedder = OpenAIEmbedder(
            config=embedder_config,
            client=openai_client
        )
        
        # CrossEncoder pour reranking (utilise aussi gpt-5-nano)
        cross_encoder = OpenAIRerankerClient(
            config=llm_config,
            client=openai_client
        )
        
        # ════════════════════════════════════════════════════════
        # Initialisation Graphiti avec config explicite
        # ════════════════════════════════════════════════════════
        
        _graphiti_client = Graphiti(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            llm_client=llm_client,
            embedder=embedder,
            cross_encoder=cross_encoder
        )
        
        logger.info(f"✅ Graphiti client initialized:")
        logger.info(f"   • LLM: {settings.OPENAI_MODEL} (Gpt5NanoClient with max_completion_tokens: 4096)")
        logger.info(f"   • Embedder: text-embedding-3-small (dim: 1536)")
        logger.info(f"   • CrossEncoder: {settings.OPENAI_MODEL}")
    
    # Build indices and constraints (only once)
    if not _indices_built:
        logger.info("🔨 Building Neo4j indices and constraints (Graphiti)...")
        await _graphiti_client.build_indices_and_constraints()
        _indices_built = True
        logger.info("✅ Graphiti indices and constraints built")
    
    return _graphiti_client


async def close_graphiti_client():
    """Close Graphiti client connection"""
    global _graphiti_client, _indices_built
    
    if _graphiti_client is not None:
        logger.info("🔌 Closing Graphiti connection...")
        await _graphiti_client.close()
        _graphiti_client = None
        _indices_built = False
        logger.info("✅ Graphiti connection closed")


async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> None:
    """
    Ingest semantic chunks to Graphiti knowledge graph avec logs détaillés et timeout
    
    Args:
        chunks: List of chunks from HierarchicalChunker
        metadata: Document-level metadata
        
    Raises:
        RuntimeError: If Graphiti is disabled
        
    Note:
        - Each chunk is ingested as an "episode" in Graphiti
        - Graphiti automatically extracts entities and relationships
        - Failed chunks are logged but don't block the pipeline
        - Timeout: 120s per chunk (configurable)
        - Community building is NOT called here (too expensive, call periodically)
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - skipping ingestion")
        return
    
    logger.info(f"📥 Starting Graphiti ingestion: {len(chunks)} chunks")
    logger.info(f"   Document: {metadata.get('filename', 'unknown')}")
    logger.info(f"   Group ID: {metadata.get('user_id', 'default')}")
    
    client = await get_graphiti_client()
    
    successful = 0
    failed = 0
    total_time = 0.0
    
    # Determine group_id for multi-tenant isolation
    group_id = metadata.get("user_id", "default")  # ✅ Phase 1+: real user IDs
    
    # Pour chaque chunk, appeler Graphiti avec logs détaillés et timeout
    for i, chunk in enumerate(chunks, start=1):
        chunk_text = chunk["text"]
        chunk_index = chunk["index"]
        chunk_tokens = len(chunk_text.split())  # Approximation
        
        logger.info(f"[{i}/{len(chunks)}] 📝 Processing chunk {chunk_index} (~{chunk_tokens} words)...")
        
        try:
            start_time = time.time()
            
            # IMPORTANT: Utiliser datetime avec timezone UTC
            reference_time = datetime.now(timezone.utc)
            
            # ════════════════════════════════════════════════════════
            # Ingest chunk avec TIMEOUT de 120s
            # ════════════════════════════════════════════════════════
            
            await asyncio.wait_for(
                client.add_episode(
                    name=f"{metadata['filename']} - Chunk {chunk_index}",
                    episode_body=chunk_text,
                    source=EpisodeType.text,
                    source_description=f"Document: {metadata['filename']}, "
                                     f"Chunk {chunk_index}/{chunk['metadata']['total_chunks']}",
                    reference_time=reference_time,
                    group_id=group_id,  # ✅ Multi-tenant isolation
                    # TODO Phase 1+: Ajouter entity_types et edge_types custom
                ),
                timeout=120.0  # ✅ Timeout de 2 minutes par chunk
            )
            
            elapsed = time.time() - start_time
            total_time += elapsed
            successful += 1
            
            logger.info(f"[{i}/{len(chunks)}] ✅ Chunk {chunk_index} ingested in {elapsed:.2f}s")
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logger.error(f"[{i}/{len(chunks)}] ⏱️  TIMEOUT after {elapsed:.2f}s for chunk {chunk_index}")
            failed += 1
            # Continue avec chunks suivants (ne pas fail tout le pipeline)
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{i}/{len(chunks)}] ❌ Failed chunk {chunk_index} after {elapsed:.2f}s: {e}", exc_info=True)
            failed += 1
            # Continue avec chunks suivants (ne pas fail tout le pipeline)
    
    # ════════════════════════════════════════════════════════
    # Résumé final de l'ingestion
    # ════════════════════════════════════════════════════════
    
    avg_time = total_time / successful if successful > 0 else 0
    
    logger.info(f"")
    logger.info(f"📊 Ingestion Summary:")
    logger.info(f"   • Total chunks: {len(chunks)}")
    logger.info(f"   • Successful: {successful}")
    logger.info(f"   • Failed: {failed}")
    logger.info(f"   • Total time: {total_time:.2f}s")
    logger.info(f"   • Avg time/chunk: {avg_time:.2f}s")
    
    if failed > 0:
        logger.warning(f"⚠️  Ingestion completed with {failed} failures")
    else:
        logger.info(f"✅ All chunks ingested successfully!")
    
    # ❌ NE PAS appeler build_communities() ici (trop coûteux)
    # À appeler manuellement via endpoint dédié ou cron job


async def search_knowledge_graph(
    query: str,
    num_results: int = 10,
    group_ids: Optional[List[str]] = None,
    search_config: Optional[SearchConfig] = None
) -> List[Dict[str, Any]]:
    """
    Search knowledge graph using Graphiti's native hybrid search
    
    Args:
        query: User's search query
        num_results: Number of results to return
        group_ids: Filter by group_ids (multi-tenant)
        search_config: Custom search configuration (default: EDGE_HYBRID_SEARCH_RRF)
        
    Returns:
        List of dicts with fact, source_entity, target_entity, score, etc.
        
    Note:
        - Uses Graphiti's hybrid search (semantic + BM25 + RRF)
        - Returns EntityEdges (facts/relations) not just Episodes
        - Much more powerful than manual Neo4j queries
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - returning empty results")
        return []
    
    logger.info(f"🔍 Graphiti search: '{query}' (num_results={num_results})")
    
    client = await get_graphiti_client()
    
    try:
        # Use Graphiti's native search (hybrid: semantic + BM25 + RRF)
        edge_results = await client.search(
            query=query,
            num_results=num_results,
            group_ids=group_ids,
            search_config=search_config or EDGE_HYBRID_SEARCH_RRF
        )
        
        # Format results pour RAG pipeline
        formatted_results = []
        for edge in edge_results:
            formatted_results.append({
                "fact": edge.fact,
                "source_entity": edge.source_node_uuid,
                "target_entity": edge.target_node_uuid,
                "relation_type": edge.name,
                "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
                "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
                "episodes": edge.episodes,  # Source episodes UUIDs
                # Note: Pour récupérer noms entities, faire requête Neo4j séparée
            })
        
        logger.info(f"✅ Graphiti search returned {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        logger.error(f"❌ Graphiti search failed: {e}", exc_info=True)
        return []


async def build_communities() -> bool:
    """
    Build communities in knowledge graph
    
    Returns:
        True if successful, False otherwise
        
    Note:
        - Expensive operation (Louvain algorithm)
        - Call periodically (not after every upload):
          * Dev: Every 5-10 documents
          * Prod: Daily cron job
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - skipping community building")
        return False
    
    logger.info("🏘️  Building communities (this may take a while)...")
    
    client = await get_graphiti_client()
    
    try:
        await client.build_communities()
        logger.info("✅ Communities built successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Community building failed: {e}", exc_info=True)
        return False
