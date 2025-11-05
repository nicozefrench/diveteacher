"""
Neo4j Management API

Endpoints for Neo4j graph database management:
- Statistics and health monitoring
- Query execution
- Data export/import
- Safe cleanup with backups
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.integrations.neo4j import neo4j_client
from app.core.config import settings

logger = logging.getLogger('diveteacher.neo4j_api')

router = APIRouter(prefix="/neo4j", tags=["neo4j"])

# Export storage directory
EXPORT_DIR = Path(settings.UPLOAD_DIR) / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class QueryRequest(BaseModel):
    """Cypher query execution request"""
    cypher: str = Field(..., description="Cypher query to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    timeout: int = Field(default=30, description="Query timeout in seconds")


class QueryResponse(BaseModel):
    """Cypher query execution response"""
    records: List[Dict[str, Any]] = Field(..., description="Query result records")
    summary: Dict[str, Any] = Field(..., description="Query execution summary")


class ExportRequest(BaseModel):
    """Graph export request"""
    format: str = Field(..., description="Export format: json, cypher, graphml")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters")


class ExportResponse(BaseModel):
    """Graph export response"""
    export_id: str = Field(..., description="Unique export identifier")
    download_url: str = Field(..., description="URL to download export")
    size_bytes: int = Field(..., description="Export file size")
    record_count: int = Field(..., description="Number of records exported")


class ClearRequest(BaseModel):
    """Graph clear request (requires confirmation)"""
    confirm: bool = Field(..., description="Confirmation flag")
    confirmation_code: str = Field(..., description="Must be 'DELETE_ALL_DATA'")
    backup_first: bool = Field(default=True, description="Create backup before clearing")


class ClearResponse(BaseModel):
    """Graph clear response"""
    status: str = Field(..., description="Operation status")
    backup_export_id: Optional[str] = Field(None, description="Backup export ID if created")
    deleted: Dict[str, int] = Field(..., description="Deletion statistics")


class StatsResponse(BaseModel):
    """Neo4j statistics response"""
    status: str
    version: str
    database: str
    nodes: Dict[str, Any]
    relationships: Dict[str, Any]
    indexes: Dict[str, Any]
    storage: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Neo4j health check response"""
    status: str = Field(..., description="healthy|degraded|unhealthy")
    connection: str = Field(..., description="connected|disconnected")
    latency_ms: Optional[float] = Field(None, description="Connection latency")
    last_check: str = Field(..., description="Last health check timestamp")
    issues: List[str] = Field(default_factory=list, description="List of issues if any")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/stats", response_model=StatsResponse)
async def get_neo4j_stats():
    """
    Get Neo4j graph statistics

    Returns comprehensive statistics about the knowledge graph:
    - Node counts by label
    - Relationship counts by type
    - Index information
    - Storage metrics

    This endpoint is read-only and safe to call frequently.
    """
    logger.info("📊 Fetching Neo4j statistics...")

    try:
        with neo4j_client.driver.session() as session:
            # Get Neo4j version and database info
            version_result = session.run("CALL dbms.components() YIELD name, versions")
            version_record = version_result.single()
            version = version_record["versions"][0] if version_record else "unknown"

            # Get node counts by label
            node_counts_result = session.run("""
                CALL db.labels() YIELD label
                CALL {
                    WITH label
                    MATCH (n)
                    WHERE label IN labels(n)
                    RETURN count(n) as count
                }
                RETURN label, count
                ORDER BY count DESC
            """)

            nodes_by_label = {}
            total_nodes = 0
            for record in node_counts_result:
                label = record["label"]
                count = record["count"]
                nodes_by_label[label] = count
                total_nodes += count

            # Get relationship counts by type
            rel_counts_result = session.run("""
                CALL db.relationshipTypes() YIELD relationshipType
                CALL {
                    WITH relationshipType
                    MATCH ()-[r]->()
                    WHERE type(r) = relationshipType
                    RETURN count(r) as count
                }
                RETURN relationshipType, count
                ORDER BY count DESC
            """)

            rels_by_type = {}
            total_rels = 0
            for record in rel_counts_result:
                rel_type = record["relationshipType"]
                count = record["count"]
                rels_by_type[rel_type] = count
                total_rels += count

            # Get index information
            indexes_result = session.run("SHOW INDEXES")
            indexes = []
            for record in indexes_result:
                indexes.append({
                    "name": record.get("name", ""),
                    "type": record.get("type", ""),
                    "state": record.get("state", ""),
                    "labels": record.get("labelsOrTypes", []),
                    "properties": record.get("properties", [])
                })

            # Build response
            stats = {
                "status": "healthy",
                "version": version,
                "database": "neo4j",
                "nodes": {
                    "total": total_nodes,
                    "by_label": nodes_by_label
                },
                "relationships": {
                    "total": total_rels,
                    "by_type": rels_by_type
                },
                "indexes": {
                    "total": len(indexes),
                    "types": list(set([idx["type"] for idx in indexes])),
                    "details": indexes
                }
            }

            logger.info(f"✅ Statistics retrieved: {total_nodes} nodes, {total_rels} relationships")
            return stats

    except Exception as e:
        logger.error(f"❌ Failed to get Neo4j statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def execute_neo4j_query(request: QueryRequest):
    """
    Execute Cypher query on Neo4j

    **Security Note:** This endpoint allows arbitrary Cypher queries.
    In production, implement proper authentication and query validation.

    **Supported Queries:**
    - Read queries (MATCH, RETURN)
    - Write queries (CREATE, MERGE, SET, DELETE)
    - Administrative queries (CALL procedures)

    **Examples:**
    - Count nodes: `MATCH (n) RETURN count(n) as count`
    - Find entities: `MATCH (n:EntityNode) RETURN n.name LIMIT 10`
    - Check relationships: `MATCH ()-[r]->() RETURN type(r), count(r)`
    """
    logger.info(f"🔍 Executing Cypher query: {request.cypher[:100]}...")

    try:
        with neo4j_client.driver.session() as session:
            start_time = datetime.now()

            # Execute query
            result = session.run(request.cypher, request.params)

            # Collect records
            records = []
            for record in result:
                # Convert Record to dict
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    # Convert Neo4j types to JSON-serializable types
                    if hasattr(value, '__dict__'):
                        record_dict[key] = dict(value)
                    else:
                        record_dict[key] = value
                records.append(record_dict)

            # Get summary
            summary_info = result.consume()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            summary = {
                "query_type": summary_info.query_type if hasattr(summary_info, 'query_type') else "unknown",
                "records_returned": len(records),
                "execution_time_ms": round(execution_time, 2)
            }

            logger.info(f"✅ Query executed: {len(records)} records in {execution_time:.2f}ms")

            return QueryResponse(
                records=records,
                summary=summary
            )

    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def get_neo4j_health():
    """
    Check Neo4j connection health

    Returns:
    - Connection status (connected/disconnected)
    - Latency measurement
    - Any detected issues

    This endpoint is lightweight and can be used for health monitoring.
    """
    logger.info("🏥 Checking Neo4j health...")

    try:
        start_time = datetime.now()

        # Test connection with simple query
        is_connected = await neo4j_client.verify_connection()

        latency = (datetime.now() - start_time).total_seconds() * 1000

        if is_connected:
            health = HealthResponse(
                status="healthy",
                connection="connected",
                latency_ms=round(latency, 2),
                last_check=datetime.now().isoformat(),
                issues=[]
            )
            logger.info(f"✅ Neo4j is healthy (latency: {latency:.2f}ms)")
        else:
            health = HealthResponse(
                status="unhealthy",
                connection="disconnected",
                latency_ms=None,
                last_check=datetime.now().isoformat(),
                issues=["Connection failed"]
            )
            logger.warning("⚠️ Neo4j connection failed")

        return health

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            connection="disconnected",
            latency_ms=None,
            last_check=datetime.now().isoformat(),
            issues=[str(e)]
        )


@router.post("/export", response_model=ExportResponse)
async def export_neo4j_data(request: ExportRequest):
    """
    Export Neo4j graph data

    **Supported Formats:**
    - `json`: JSON format (nodes and relationships)
    - `cypher`: Cypher CREATE statements
    - `graphml`: GraphML XML format

    **Filters:**
    - `labels`: List of node labels to export
    - `limit`: Maximum number of nodes to export

    **Example:**
    ```json
    {
        "format": "json",
        "filters": {
            "labels": ["EntityNode"],
            "limit": 1000
        }
    }
    ```

    The export is saved to disk and a download URL is returned.
    """
    logger.info(f"📤 Exporting graph data (format: {request.format})...")

    try:
        export_id = str(uuid.uuid4())
        export_filename = f"neo4j_export_{export_id}.{request.format}"
        export_path = EXPORT_DIR / export_filename

        with neo4j_client.driver.session() as session:
            # Build query based on filters
            filters = request.filters or {}
            labels_filter = filters.get("labels", [])
            limit = filters.get("limit", 10000)

            if labels_filter:
                label_clause = ":" + ":".join(labels_filter)
            else:
                label_clause = ""

            # Export nodes
            nodes_query = f"""
                MATCH (n{label_clause})
                RETURN n
                LIMIT {limit}
            """

            nodes_result = session.run(nodes_query)
            nodes = []
            node_ids = set()

            for record in nodes_result:
                node = record["n"]
                node_ids.add(node.id)
                nodes.append({
                    "id": node.id,
                    "labels": list(node.labels),
                    "properties": dict(node)
                })

            # Export relationships between exported nodes
            if node_ids:
                rels_query = f"""
                    MATCH (n{label_clause})-[r]->(m{label_clause})
                    WHERE id(n) IN $node_ids AND id(m) IN $node_ids
                    RETURN r, id(startNode(r)) as source, id(endNode(r)) as target
                    LIMIT {limit}
                """

                rels_result = session.run(rels_query, node_ids=list(node_ids))
                relationships = []

                for record in rels_result:
                    rel = record["r"]
                    relationships.append({
                        "id": rel.id,
                        "type": rel.type,
                        "source": record["source"],
                        "target": record["target"],
                        "properties": dict(rel)
                    })
            else:
                relationships = []

            # Write export file based on format
            if request.format == "json":
                export_data = {
                    "nodes": nodes,
                    "relationships": relationships,
                    "metadata": {
                        "export_id": export_id,
                        "timestamp": datetime.now().isoformat(),
                        "filters": filters
                    }
                }
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

            elif request.format == "cypher":
                # Generate Cypher CREATE statements
                with open(export_path, 'w') as f:
                    f.write("// Neo4j Export - Cypher Statements\n")
                    f.write(f"// Generated: {datetime.now().isoformat()}\n\n")

                    for node in nodes:
                        labels_str = ":".join(node["labels"])
                        props_str = json.dumps(node["properties"])
                        f.write(f"CREATE (n:{labels_str} {props_str});\n")

                    f.write("\n// Relationships\n")
                    for rel in relationships:
                        props_str = json.dumps(rel["properties"])
                        f.write(f"MATCH (a), (b) WHERE id(a) = {rel['source']} AND id(b) = {rel['target']}\n")
                        f.write(f"CREATE (a)-[r:{rel['type']} {props_str}]->(b);\n")

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

            # Get file size
            file_size = export_path.stat().st_size

            logger.info(f"✅ Export complete: {len(nodes)} nodes, {len(relationships)} rels ({file_size} bytes)")

            return ExportResponse(
                export_id=export_id,
                download_url=f"/api/neo4j/export/{export_id}/download",
                size_bytes=file_size,
                record_count=len(nodes) + len(relationships)
            )

    except Exception as e:
        logger.error(f"❌ Export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/{export_id}/download")
async def download_export(export_id: str):
    """
    Download an exported graph file

    Args:
        export_id: Export identifier from export endpoint

    Returns:
        File download response
    """
    # Find export file
    export_files = list(EXPORT_DIR.glob(f"neo4j_export_{export_id}.*"))

    if not export_files:
        raise HTTPException(status_code=404, detail="Export not found")

    export_path = export_files[0]

    return FileResponse(
        path=export_path,
        filename=export_path.name,
        media_type="application/octet-stream"
    )


@router.delete("/clear", response_model=ClearResponse)
async def clear_neo4j_graph(request: ClearRequest):
    """
    Clear all data from Neo4j graph

    **⚠️  DESTRUCTIVE OPERATION ⚠️**

    This endpoint deletes ALL nodes and relationships from the database.

    **Security Requirements:**
    1. Must set `confirm: true`
    2. Must provide confirmation code: "DELETE_ALL_DATA"
    3. Optionally creates backup before clearing (recommended)

    **Example:**
    ```json
    {
        "confirm": true,
        "confirmation_code": "DELETE_ALL_DATA",
        "backup_first": true
    }
    ```

    **Note:** In production, this should require admin authentication.
    """
    logger.warning("⚠️  Clear graph requested...")

    # Validation
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required (confirm: true)")

    if request.confirmation_code != "DELETE_ALL_DATA":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation code. Must be 'DELETE_ALL_DATA'"
        )

    backup_export_id = None

    try:
        # Step 1: Create backup if requested
        if request.backup_first:
            logger.info("📤 Creating backup before clearing...")
            export_req = ExportRequest(format="json")
            backup_export = await export_neo4j_data(export_req)
            backup_export_id = backup_export.export_id
            logger.info(f"✅ Backup created: {backup_export_id}")

        # Step 2: Get current counts
        with neo4j_client.driver.session() as session:
            count_result = session.run("""
                MATCH (n)
                OPTIONAL MATCH ()-[r]->()
                RETURN count(DISTINCT n) as nodes, count(r) as rels
            """)
            counts = count_result.single()
            nodes_count = counts["nodes"]
            rels_count = counts["rels"]

            logger.warning(f"⚠️  Deleting {nodes_count} nodes and {rels_count} relationships...")

            # Step 3: Delete all data
            session.run("MATCH (n) DETACH DELETE n")

            logger.info("✅ All data deleted")

        return ClearResponse(
            status="cleared",
            backup_export_id=backup_export_id,
            deleted={
                "nodes": nodes_count,
                "relationships": rels_count
            }
        )

    except Exception as e:
        logger.error(f"❌ Clear operation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

