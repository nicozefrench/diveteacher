"""
Knowledge Graph Visualization Endpoint
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.integrations.neo4j import neo4j_client

router = APIRouter()


@router.get("/graph/stats")
async def get_graph_stats():
    """
    Get knowledge graph statistics
    
    Returns:
        Graph statistics (node count, relationship count, etc.)
    """
    
    await neo4j_client.connect()
    
    query = """
    MATCH (n)
    WITH count(n) AS node_count
    MATCH ()-[r]->()
    RETURN node_count, count(r) AS relationship_count
    """
    
    try:
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            result = await session.run(query)
            data = await result.single()
            
            return JSONResponse(content={
                "nodes": data["node_count"],
                "relationships": data["relationship_count"]
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
    
    await neo4j_client.connect()
    
    # Query for document-specific subgraph
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.upload_id = $document_id OR m.upload_id = $document_id
    RETURN n, r, m
    LIMIT 100
    """
    
    try:
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            result = await session.run(query, document_id=document_id)
            records = await result.data()
            
            # Format for graph visualization libraries (e.g., react-force-graph)
            nodes_map = {}
            links = []
            
            for record in records:
                source = record.get("n")
                target = record.get("m")
                relationship = record.get("r")
                
                # Add nodes
                if source and source.id not in nodes_map:
                    nodes_map[source.id] = {
                        "id": source.id,
                        "label": source.get("text", "")[:50],  # Truncate
                        "type": list(source.labels)[0] if source.labels else "Entity"
                    }
                
                if target and target.id not in nodes_map:
                    nodes_map[target.id] = {
                        "id": target.id,
                        "label": target.get("text", "")[:50],
                        "type": list(target.labels)[0] if target.labels else "Entity"
                    }
                
                # Add link
                if relationship:
                    links.append({
                        "source": source.id,
                        "target": target.id,
                        "type": relationship.type
                    })
            
            return JSONResponse(content={
                "nodes": list(nodes_map.values()),
                "links": links
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

