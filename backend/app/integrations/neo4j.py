"""
Neo4j Database Client

Handles connection to Neo4j and provides query methods for RAG.
"""

from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable
import sentry_sdk

from app.core.config import settings


class Neo4jClient:
    """Neo4j database client"""
    
    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
    
    async def connect(self):
        """Establish connection to Neo4j"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    async def verify_connection(self) -> bool:
        """
        Verify Neo4j connection
        
        Returns:
            True if connected, raises exception otherwise
        """
        await self.connect()
        async with self.driver.session(database=self.database) as session:
            result = await session.run("RETURN 1")
            await result.single()
        return True
    
    async def query_context(
        self, 
        question: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query Neo4j for relevant context based on user question
        
        This is a simplified version. In production, you would:
        1. Use vector embeddings for semantic search
        2. Implement graph traversal for related entities
        3. Use Neo4j's APOC procedures for advanced queries
        
        Args:
            question: User's question
            top_k: Number of context nodes to retrieve
            
        Returns:
            List of context dictionaries
        """
        await self.connect()
        
        # Extract keywords from question (simplified)
        keywords = [word.lower() for word in question.split() if len(word) > 3]
        
        # Query for nodes containing keywords
        # This is a basic implementation - enhance with:
        # - Vector similarity search
        # - Graph traversal (MATCH patterns)
        # - Ranking algorithms
        query = """
        MATCH (n)
        WHERE ANY(keyword IN $keywords WHERE toLower(n.text) CONTAINS keyword)
        RETURN n.text AS text, n.source AS source, n.metadata AS metadata
        LIMIT $top_k
        """
        
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run(
                    query,
                    keywords=keywords,
                    top_k=top_k
                )
                
                records = await result.data()
                
                context = [
                    {
                        "text": record.get("text", ""),
                        "source": record.get("source", "Unknown"),
                        "metadata": record.get("metadata", {})
                    }
                    for record in records
                ]
                
                return context
                
        except Exception as e:
            sentry_sdk.capture_exception(e)
            # Return empty context on error (don't crash)
            return []
    
    async def ingest_nodes(
        self, 
        nodes: List[Dict[str, Any]]
    ) -> int:
        """
        Ingest multiple nodes into Neo4j
        
        Args:
            nodes: List of node dictionaries with properties
            
        Returns:
            Number of nodes created
        """
        await self.connect()
        
        query = """
        UNWIND $nodes AS node
        CREATE (n:Entity)
        SET n = node
        """
        
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, nodes=nodes)
            summary = await result.consume()
            return summary.counters.nodes_created
    
    async def ingest_relationships(
        self, 
        relationships: List[Dict[str, Any]]
    ) -> int:
        """
        Ingest relationships into Neo4j
        
        Args:
            relationships: List of relationship dictionaries
            
        Returns:
            Number of relationships created
        """
        await self.connect()
        
        # Simplified - in production, match existing nodes by ID
        query = """
        UNWIND $relationships AS rel
        MATCH (source:Entity {id: rel.source_id})
        MATCH (target:Entity {id: rel.target_id})
        CREATE (source)-[r:RELATED_TO {type: rel.type}]->(target)
        SET r = rel.properties
        """
        
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, relationships=relationships)
            summary = await result.consume()
            return summary.counters.relationships_created


# Global client instance
neo4j_client = Neo4jClient()

