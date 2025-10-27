"""
Neo4j Indexes Management for RAG Queries

This module creates indexes optimized for RAG retrieval operations.
These indexes complement Graphiti's automatic indexes.
"""

from typing import List, Dict, Any
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from app.core.config import settings

logger = logging.getLogger('diveteacher.neo4j')


def create_rag_indexes(driver: GraphDatabase.driver) -> List[str]:
    """
    Create indexes optimized for RAG queries
    
    Args:
        driver: Neo4j driver instance
        
    Returns:
        List of index names successfully created
        
    Note:
        - These indexes complement Graphiti's automatic indexes
        - No conflicts with Graphiti schema
        - Uses IF NOT EXISTS to be idempotent
    """
    indexes_created = []
    
    logger.info("🔨 Creating RAG-optimized indexes...")
    
    # 1. Full-text index on Episode.content (CRITICAL for RAG)
    try:
        driver.execute_query(
            """
            CREATE FULLTEXT INDEX episode_content IF NOT EXISTS
            FOR (e:Episode) ON EACH [e.content]
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("episode_content")
        logger.info("✅ Full-text index 'episode_content' created")
    except Neo4jError as e:
        if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
            logger.info("⚠️  Index 'episode_content' already exists")
            indexes_created.append("episode_content")
        else:
            logger.error(f"❌ Failed to create 'episode_content': {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating 'episode_content': {e}")
    
    # 2. Index on Entity.name (fast entity lookup)
    try:
        driver.execute_query(
            """
            CREATE INDEX entity_name_idx IF NOT EXISTS
            FOR (e:Entity) ON (e.name)
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("entity_name_idx")
        logger.info("✅ Index 'entity_name_idx' created")
    except Neo4jError as e:
        if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
            logger.info("⚠️  Index 'entity_name_idx' already exists")
            indexes_created.append("entity_name_idx")
        else:
            logger.error(f"❌ Failed to create 'entity_name_idx': {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating 'entity_name_idx': {e}")
    
    # 3. Index on Episode.valid_at (filter by date if needed)
    try:
        driver.execute_query(
            """
            CREATE INDEX episode_date_idx IF NOT EXISTS
            FOR (e:Episode) ON (e.valid_at)
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("episode_date_idx")
        logger.info("✅ Index 'episode_date_idx' created")
    except Neo4jError as e:
        if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
            logger.info("⚠️  Index 'episode_date_idx' already exists")
            indexes_created.append("episode_date_idx")
        else:
            logger.error(f"❌ Failed to create 'episode_date_idx': {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating 'episode_date_idx': {e}")
    
    logger.info(f"✅ RAG indexes created: {len(indexes_created)}/{3}")
    
    return indexes_created


def verify_indexes(driver: GraphDatabase.driver) -> Dict[str, Any]:
    """
    Verify all indexes are created and ONLINE
    
    Args:
        driver: Neo4j driver instance
        
    Returns:
        Dictionary with index information
        
    Note:
        Uses SHOW INDEXES (Neo4j 5.x compatible)
    """
    try:
        records, summary, keys = driver.execute_query(
            "SHOW INDEXES",
            database_=settings.NEO4J_DATABASE
        )
        
        indexes = []
        rag_indexes = []
        graphiti_indexes = []
        
        for record in records:
            # Neo4j 5.x SHOW INDEXES returns different column names
            idx_name = record.get("name", "")
            idx_type = record.get("type", "")
            idx_state = record.get("state", "")
            idx_labels = record.get("labelsOrTypes", []) or record.get("entityType", [])
            idx_properties = record.get("properties", [])
            
            idx_info = {
                "name": idx_name,
                "type": idx_type,
                "state": idx_state,
                "labels": idx_labels,
                "properties": idx_properties
            }
            indexes.append(idx_info)
            
            # Categorize indexes
            if any(name in idx_name for name in ["episode_content", "entity_name", "episode_date"]):
                rag_indexes.append(idx_info)
            elif "Episode" in str(idx_labels) or "Entity" in str(idx_labels):
                graphiti_indexes.append(idx_info)
        
        result = {
            "total": len(indexes),
            "rag_indexes": len(rag_indexes),
            "graphiti_indexes": len(graphiti_indexes),
            "all_indexes": indexes,
            "rag_details": rag_indexes,
            "graphiti_details": graphiti_indexes
        }
        
        logger.info(f"📊 Index verification: {result['total']} total, "
                   f"{result['rag_indexes']} RAG, {result['graphiti_indexes']} Graphiti")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Index verification failed: {e}")
        return {
            "total": 0,
            "rag_indexes": 0,
            "graphiti_indexes": 0,
            "all_indexes": [],
            "error": str(e)
        }


def drop_rag_indexes(driver: GraphDatabase.driver) -> List[str]:
    """
    Drop RAG indexes (for testing or cleanup)
    
    Args:
        driver: Neo4j driver instance
        
    Returns:
        List of dropped index names
        
    Warning:
        This will impact RAG query performance until indexes are recreated
    """
    logger.warning("⚠️  Dropping RAG indexes...")
    
    dropped = []
    index_names = ["episode_content", "entity_name_idx", "episode_date_idx"]
    
    for idx_name in index_names:
        try:
            driver.execute_query(
                f"DROP INDEX {idx_name} IF EXISTS",
                database_=settings.NEO4J_DATABASE
            )
            dropped.append(idx_name)
            logger.info(f"🗑️  Dropped index '{idx_name}'")
        except Exception as e:
            logger.error(f"❌ Failed to drop '{idx_name}': {e}")
    
    logger.warning(f"⚠️  Dropped {len(dropped)} RAG indexes")
    
    return dropped

