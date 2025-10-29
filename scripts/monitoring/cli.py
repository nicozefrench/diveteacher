#!/usr/bin/env python3
"""
DiveTeacher Monitoring CLI

Unified command-line interface for all monitoring tools.

Usage:
    diveteacher-monitor neo4j stats
    diveteacher-monitor graphiti status <upload_id>
    diveteacher-monitor docling verify
    diveteacher-monitor system health
"""

import click
import sys


@click.group()
def cli():
    """DiveTeacher RAG System Monitoring Suite"""
    pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Neo4j Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@cli.group()
def neo4j():
    """Neo4j graph database management"""
    pass


@neo4j.command('stats')
def neo4j_stats():
    """Show graph statistics"""
    from scripts.monitoring.neo4j.stats import show_stats
    sys.exit(show_stats())


@neo4j.command('query')
@click.argument('cypher')
def neo4j_query(cypher):
    """Execute Cypher query"""
    from scripts.monitoring.neo4j.query import show_query_results
    sys.exit(show_query_results(cypher))


@neo4j.command('export')
@click.option('--format', default='json', help='Export format (json|cypher|graphml)')
def neo4j_export(format):
    """Export graph data"""
    from scripts.monitoring.neo4j.export import show_export_info
    sys.exit(show_export_info(format))


@neo4j.command('health')
def neo4j_health():
    """Check Neo4j health"""
    from scripts.monitoring.neo4j.health import show_health
    sys.exit(show_health())


@neo4j.command('clear')
@click.option('--confirm', is_flag=True, help='Skip confirmation')
def neo4j_clear(confirm):
    """Clear graph (with backup)"""
    from scripts.monitoring.neo4j.cleanup import show_clear_result
    sys.exit(show_clear_result(confirm))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Graphiti Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@cli.group()
def graphiti():
    """Graphiti ingestion monitoring"""
    pass


@graphiti.command('status')
@click.argument('upload_id')
def graphiti_status(upload_id):
    """Show ingestion status"""
    from scripts.monitoring.graphiti.status import show_status
    sys.exit(show_status(upload_id))


@graphiti.command('metrics')
@click.argument('upload_id')
def graphiti_metrics(upload_id):
    """Show ingestion metrics"""
    from scripts.monitoring.graphiti.metrics import show_metrics
    sys.exit(show_metrics(upload_id))


@graphiti.command('validate')
@click.argument('upload_id')
def graphiti_validate(upload_id):
    """Validate ingestion results"""
    from scripts.monitoring.graphiti.validate import show_validation
    sys.exit(show_validation(upload_id))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Docling Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@cli.group()
def docling():
    """Docling document processing monitoring"""
    pass


@docling.command('verify')
def docling_verify():
    """Verify warm-up effectiveness"""
    from scripts.monitoring.docling.warmup_verify import verify_warmup
    sys.exit(verify_warmup())


@docling.command('cache')
def docling_cache():
    """Show cache information"""
    from scripts.monitoring.docling.cache_info import show_cache_info
    sys.exit(show_cache_info())


@docling.command('performance')
@click.argument('upload_id')
def docling_performance(upload_id):
    """Show conversion performance"""
    from scripts.monitoring.docling.performance import show_performance
    sys.exit(show_performance(upload_id))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# System Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@cli.group()
def system():
    """System-wide monitoring"""
    pass


@system.command('health')
def system_health():
    """Overall system health check"""
    from scripts.monitoring.system.health import show_health
    sys.exit(show_health())


@system.command('resources')
def system_resources():
    """Show resource usage"""
    from scripts.monitoring.system.resources import show_resources
    sys.exit(show_resources())


@system.command('docker')
def system_docker():
    """Show Docker container status"""
    from scripts.monitoring.system.docker import show_docker_stats
    sys.exit(show_docker_stats())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Entry Point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    cli()

