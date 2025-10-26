"""
Graphiti Integration

Handles knowledge graph extraction from documents using Graphiti.
"""

from typing import Dict, Any
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from app.core.config import settings
from app.integrations.neo4j import neo4j_client


# Initialize Graphiti client
graphiti_client = None

def get_graphiti_client():
    """Get or create Graphiti client"""
    global graphiti_client
    if graphiti_client is None and settings.GRAPHITI_ENABLED:
        graphiti_client = Graphiti(
            neo4j_uri=settings.NEO4J_URI,
            neo4j_user=settings.NEO4J_USER,
            neo4j_password=settings.NEO4J_PASSWORD
        )
    return graphiti_client


async def ingest_document_to_graph(
    markdown_content: str, 
    metadata: Dict[str, Any]
) -> None:
    """
    Ingest document markdown into knowledge graph using Graphiti
    
    Args:
        markdown_content: Markdown text from Dockling
        metadata: Document metadata (filename, upload_id, etc.)
    """
    
    if not settings.GRAPHITI_ENABLED:
        print("⚠️  Graphiti disabled - skipping knowledge graph ingestion")
        return
    
    client = get_graphiti_client()
    
    # Add document as an episode to Graphiti
    # Graphiti will automatically extract entities and relationships
    await client.add_episode(
        name=metadata.get("filename", "unknown"),
        episode_body=markdown_content,
        source_description=f"Uploaded document: {metadata.get('filename')}",
        reference_time=metadata.get("processed_at"),
        episode_type=EpisodeType.text
    )
    
    print(f"✅ Ingested document to knowledge graph: {metadata.get('filename')}")

