"""
Knowledge Graph Visualization Endpoint
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.integrations.neo4j import neo4j_client
from app.integrations.graphiti import build_communities as graphiti_build_communities

logger = logging.getLogger('diveteacher.api.graph')

router = APIRouter()


@router.post("/graph/build-communities")
async def build_communities_endpoint(background_tasks: BackgroundTasks):
    """
    Build communities in knowledge graph
    
    Note:
        - Runs in background task (async)
        - Expensive operation (minutes for large graphs)
        - Recommended frequency:
          * Dev: After every 5-10 documents
          * Prod: Daily cron job
    """
    
    async def run_community_building():
        success = await graphiti_build_communities()
        if success:
            logger.info("✅ Background community building completed")
        else:
            logger.error("❌ Background community building failed")
    
    background_tasks.add_task(run_community_building)
    
    return JSONResponse(content={
        "status": "started",
        "message": "Community building started in background"
    })


@router.get("/graph/stats")
async def get_graph_stats():
    """
    Get knowledge graph statistics
    
    Returns:
        Graph statistics (episodes, entities, relationships)
    """
    
    neo4j_client.connect()
    
    # Query pour stats complètes (Episodes, Entities, Relations)
    query = """
    MATCH (e:Episode)
    WITH count(e) AS episode_count
    MATCH (n:Entity)
    WITH episode_count, count(n) AS entity_count
    MATCH ()-[r:RELATES_TO]->()
    RETURN 
        episode_count,
        entity_count,
        count(r) AS relationship_count
    """
    
    try:
        records, summary, keys = neo4j_client.driver.execute_query(
            query,
            database_=neo4j_client.database
        )
        
        if records:
            data = dict(records[0])
            return JSONResponse(content={
                "episodes": data.get("episode_count", 0),
                "entities": data.get("entity_count", 0),
                "relationships": data.get("relationship_count", 0)
            })
        else:
            return JSONResponse(content={
                "episodes": 0,
                "entities": 0,
                "relationships": 0
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/document/{document_id}")
async def get_document_graph(document_id: str):
    """
    Get knowledge graph for a specific document
    
    Args:
        document_id: Document/upload ID
        
    Returns:
        Graph data for visualization (nodes + links)
    """
    
    neo4j_client.connect()
    
    # Query for document-specific subgraph
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.upload_id = $document_id OR m.upload_id = $document_id
    RETURN n, r, m
    LIMIT 100
    """
    
    try:
        records, summary, keys = neo4j_client.driver.execute_query(
            query, 
            document_id=document_id,
            database_=neo4j_client.database
        )
        
        # Format for graph visualization libraries (e.g., react-force-graph)
        nodes_map = {}
        links = []
        
        for record in records:
            record_dict = dict(record)
            source = record_dict.get("n")
            target = record_dict.get("m")
            relationship = record_dict.get("r")
            
            # Add nodes
            if source and hasattr(source, 'element_id'):
                source_id = source.element_id
                if source_id not in nodes_map:
                    nodes_map[source_id] = {
                        "id": source_id,
                        "label": dict(source).get("text", dict(source).get("content", ""))[:50],
                        "type": list(source.labels)[0] if source.labels else "Entity"
                    }
            
            if target and hasattr(target, 'element_id'):
                target_id = target.element_id
                if target_id not in nodes_map:
                    nodes_map[target_id] = {
                        "id": target_id,
                        "label": dict(target).get("text", dict(target).get("content", ""))[:50],
                        "type": list(target.labels)[0] if target.labels else "Entity"
                    }
            
            # Add link
            if relationship and source and target:
                links.append({
                    "source": source.element_id,
                    "target": target.element_id,
                    "type": relationship.type
                })
        
        return JSONResponse(content={
            "nodes": list(nodes_map.values()),
            "links": links
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

