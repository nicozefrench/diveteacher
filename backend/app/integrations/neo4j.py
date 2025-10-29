"""
Neo4j Database Client

⚠️  DEPRECATED: Direct Neo4j queries for RAG
    → Use Graphiti search instead (backend/app/integrations/graphiti.py)
    
This client is kept for:
- Graph stats endpoints
- Direct Cypher queries (debugging)
- Fallback if Graphiti unavailable

For RAG queries, use: graphiti.search_knowledge_graph()

TODO: Migrate to AsyncGraphDatabase for production (HIGH PRIORITY)
      See FIXES-LOG.md - "Neo4j Async Migration Roadmap"
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    CypherSyntaxError,
    ConstraintError,
    Neo4jError
)
import sentry_sdk

from app.core.config import settings

logger = logging.getLogger('diveteacher.neo4j')


class Neo4jClient:
    """
    Neo4j database client for RAG queries
    
    Note:
        - Uses GraphDatabase.driver() (sync API recommended by Neo4j 2025)
        - Graphiti handles WRITE operations (ingestion)
        - This client handles READ operations (RAG queries)
    """
    
    def __init__(self):
        self.driver = None
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
    
    def connect(self):
        """
        Establish connection to Neo4j
        
        Note:
            - Connection pool configured for optimal performance
            - Driver handles async operations internally
        """
        if not self.driver:
            logger.info(f"Connecting to Neo4j at {self.uri}")
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_pool_size=50,
                max_connection_lifetime=3600,
                connection_acquisition_timeout=60
            )
            self.driver.verify_connectivity()
            logger.info("✅ Neo4j connected")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            logger.info("Closing Neo4j connection")
            self.driver.close()
            self.driver = None
            logger.info("✅ Neo4j connection closed")
    
    async def verify_connection(self) -> bool:
        """
        Verify Neo4j connection (async wrapper)
        
        Note:
            Uses asyncio.to_thread() to run sync Neo4j call in thread pool
            This prevents blocking the FastAPI event loop
            
            TODO: Replace with native AsyncGraphDatabase in production
                  See FIXES-LOG.md for migration plan
        
        Returns:
            True if connected, raises exception otherwise
        """
        def _sync_verify() -> bool:
            """Synchronous verification (runs in thread pool)"""
            self.connect()
            try:
                records, summary, keys = self.driver.execute_query(
                    "RETURN 1 AS test",
                    database_=self.database,
                    routing_=RoutingControl.READ
                )
                logger.info("✅ Neo4j connection verified")
                return True
            except ServiceUnavailable as e:
                logger.error(f"❌ Neo4j unavailable: {e}")
                raise
            except AuthError as e:
                logger.error(f"❌ Neo4j authentication failed: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Neo4j connection verification failed: {e}")
                raise
        
        # Run sync function in thread pool to avoid blocking event loop
        return await asyncio.to_thread(_sync_verify)
    
    def query_context_fulltext(
        self, 
        question: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Full-text search on Episodes (chunks) using Neo4j full-text index
        
        Args:
            question: User question
            top_k: Number of results to return
            
        Returns:
            List of context chunks with scores
            
        Note:
            - Requires 'episode_content' full-text index to be created
            - Returns empty list on error (graceful degradation)
        """
        self.connect()
        
        logger.info(f"Full-text search: '{question}' (top_k={top_k})")
        
        try:
            records, summary, keys = self.driver.execute_query(
                """
                CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
                YIELD node, score
                RETURN 
                  node.content AS text,
                  node.source_description AS source,
                  node.name AS chunk_name,
                  node.created_at AS created_at,
                  score
                ORDER BY score DESC
                LIMIT $top_k
                """,
                search_text=question,
                top_k=top_k,
                database_=self.database,
                routing_=RoutingControl.READ
            )
            
            context = []
            for record in records:
                context.append({
                    "text": record["text"],
                    "source": record["source"] or "Unknown",
                    "chunk_name": record["chunk_name"],
                    "score": record["score"],
                    "created_at": str(record["created_at"]) if record.get("created_at") else None
                })
            
            logger.info(f"✅ Full-text search returned {len(context)} results")
            return context
            
        except Neo4jError as e:
            logger.error(f"❌ Full-text search failed: {e.message if hasattr(e, 'message') else str(e)}")
            sentry_sdk.capture_exception(e)
            return []
        except Exception as e:
            logger.error(f"❌ Full-text search error: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            return []
    
    def query_entities_related(
        self, 
        entity_name: str, 
        depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Search entities and their related entities via RELATES_TO relationships
        
        Args:
            entity_name: Entity to search (partial match)
            depth: Relationship traversal depth (1-3)
            
        Returns:
            List of entities with relationships
            
        Note:
            - Searches in Entity.name and Entity.summary
            - Traverses RELATES_TO relationships
            - Returns empty list on error
        """
        self.connect()
        
        logger.info(f"Entity search: '{entity_name}' (depth={depth})")
        
        # Limit depth to avoid performance issues
        depth = min(max(depth, 1), 3)
        
        try:
            records, summary, keys = self.driver.execute_query(
                f"""
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($entity_name)
                   OR toLower(e.summary) CONTAINS toLower($entity_name)
                OPTIONAL MATCH (e)-[r:RELATES_TO*1..{depth}]-(related:Entity)
                RETURN 
                  e.name AS entity,
                  e.summary AS description,
                  e.entity_type AS type,
                  collect(DISTINCT {{
                    name: related.name,
                    type: related.entity_type,
                    relationship: [rel IN r | rel.fact][0]
                  }}) AS related_entities
                LIMIT 10
                """,
                entity_name=entity_name,
                database_=self.database,
                routing_=RoutingControl.READ
            )
            
            entities = []
            for record in records:
                # Filter out null related entities
                related = [r for r in record["related_entities"] if r.get("name")]
                
                entities.append({
                    "entity": record["entity"],
                    "description": record["description"] or "",
                    "type": record["type"] or "Unknown",
                    "related": related[:5]  # Limit to 5 related entities
                })
            
            logger.info(f"✅ Entity search found {len(entities)} entities")
            return entities
            
        except Neo4jError as e:
            logger.error(f"❌ Entity search failed: {e.message if hasattr(e, 'message') else str(e)}")
            sentry_sdk.capture_exception(e)
            return []
        except Exception as e:
            logger.error(f"❌ Entity search error: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            return []
    
    def query_context_hybrid(
        self, 
        question: str, 
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Hybrid search: Combines full-text Episodes + Entity search
        
        Args:
            question: User question
            top_k: Number of results per type
            
        Returns:
            {
                "episodes": List[Dict],  # Text chunks
                "entities": List[Dict],  # Related entities
                "total": int
            }
            
        Note:
            - Best search method for RAG (combines text and graph)
            - Extracts keywords from question for entity search
        """
        self.connect()
        
        logger.info(f"Hybrid search: '{question}' (top_k={top_k})")
        
        # 1. Full-text search on chunks
        episodes = self.query_context_fulltext(question, top_k=top_k)
        
        # 2. Extract potential entity names from question
        # Simple keyword extraction (words > 3 chars, excluding common words)
        stop_words = {'dans', 'pour', 'avec', 'sans', 'sous', 'quel', 'quels', 'quelle', 'quelles',
                      'what', 'where', 'when', 'which', 'that', 'this', 'these', 'those'}
        keywords = [w.strip('?.,!;:') for w in question.split() if len(w) > 3 and w.lower() not in stop_words]
        
        # 3. Search entities for each keyword
        entities = []
        unique_entity_names = set()
        
        for keyword in keywords[:3]:  # Limit to 3 keywords
            entity_results = self.query_entities_related(keyword, depth=1)
            for entity in entity_results:
                entity_name = entity.get("entity", "")
                if entity_name and entity_name not in unique_entity_names:
                    entities.append(entity)
                    unique_entity_names.add(entity_name)
        
        # Limit entities to top_k
        entities = entities[:top_k]
        
        result = {
            "episodes": episodes,
            "entities": entities,
            "total": len(episodes) + len(entities)
        }
        
        logger.info(f"✅ Hybrid search: {len(episodes)} episodes, {len(entities)} entities")
        
        return result


# Global client instance
neo4j_client = Neo4jClient()

