# DiveTeacher Monitoring Suite

Professional monitoring and management tools for the RAG Knowledge Graph system.

## 📋 Overview

The monitoring suite provides a unified command-line interface (CLI) and Python modules for managing and monitoring all aspects of the DiveTeacher RAG system:

- **Neo4j**: Graph database management (stats, query, export, cleanup)
- **Graphiti**: Ingestion status and validation
- **Docling**: Document processing performance
- **System**: Overall health and resource monitoring

## 🚀 Quick Start

### Installation

```bash
# From project root
cd scripts/monitoring
pip install -e .
```

This installs the `diveteacher-monitor` command globally.

### Basic Usage

```bash
# System health check
diveteacher-monitor system health

# Neo4j statistics
diveteacher-monitor neo4j stats

# Verify Docling warm-up
diveteacher-monitor docling verify

# Check ingestion status
diveteacher-monitor graphiti status <upload_id>
```

## 📚 Complete Command Reference

### Neo4j Commands

#### `neo4j stats`
Display comprehensive graph statistics.

```bash
diveteacher-monitor neo4j stats
```

**Output:**
- Node counts by label
- Relationship counts by type
- Index information
- Storage size
- Database version

#### `neo4j query <cypher>`
Execute Cypher queries.

```bash
diveteacher-monitor neo4j query "MATCH (n) RETURN count(n)"
diveteacher-monitor neo4j query "MATCH (e:EntityNode) RETURN e.name LIMIT 10"
```

#### `neo4j export [--format json|cypher|graphml]`
Export graph data.

```bash
diveteacher-monitor neo4j export
diveteacher-monitor neo4j export --format cypher
```

#### `neo4j health`
Check Neo4j connection health.

```bash
diveteacher-monitor neo4j health
```

#### `neo4j clear [--confirm]`
Clear all graph data (with automatic backup).

```bash
# Interactive (prompts for confirmation)
diveteacher-monitor neo4j clear

# Skip confirmation
diveteacher-monitor neo4j clear --confirm
```

### Graphiti Commands

#### `graphiti status <upload_id>`
Show document processing status.

```bash
diveteacher-monitor graphiti status abc-123-def-456
```

**Output:**
- Current status (pending/processing/completed/failed)
- Processing stage and sub-stage
- Progress percentage
- Detailed metrics
- Timestamps

#### `graphiti metrics <upload_id>`
Display ingestion metrics.

```bash
diveteacher-monitor graphiti metrics abc-123-def-456
```

**Output:**
- Document metrics (pages, size)
- Chunking progress
- Entities and relations extracted
- Neo4j nodes created
- Claude API usage

#### `graphiti validate <upload_id>`
Validate ingestion results.

```bash
diveteacher-monitor graphiti validate abc-123-def-456
```

**Checks:**
- Upload status completed
- Neo4j has nodes and relationships
- Entities extracted
- Relations extracted

### Docling Commands

#### `docling verify`
Verify Docling warm-up effectiveness.

```bash
diveteacher-monitor docling verify
```

**Checks:**
- Cache directory exists and size
- No "Fetching" messages in logs
- First conversion speed

#### `docling cache`
Show model cache information.

```bash
diveteacher-monitor docling cache
```

**Output:**
- Cache directory status
- Cache size in MB
- Model files cached

#### `docling performance <upload_id>`
Show conversion performance metrics.

```bash
diveteacher-monitor docling performance abc-123-def-456
```

**Output:**
- Conversion time
- Pages processed
- Processing speed (pages/second)
- Performance assessment

### System Commands

#### `system health`
Overall system health check.

```bash
diveteacher-monitor system health
```

**Checks:**
- Backend API
- Neo4j connection
- Ollama status

#### `system resources`
Display resource usage.

```bash
diveteacher-monitor system resources
```

**Output:**
- CPU usage per container
- Memory usage per container
- Memory percentage

#### `system docker`
Show Docker container status.

```bash
diveteacher-monitor system docker
```

**Output:**
- Container status (running/stopped)
- Images
- Ports

## 🐍 Python API

You can also use the monitoring modules directly in Python:

```python
from scripts.monitoring.neo4j import stats, query
from scripts.monitoring.graphiti import status, metrics
from scripts.monitoring.docling import warmup_verify
from scripts.monitoring.system import health

# Get Neo4j stats
neo4j_stats = stats.get_stats()
print(neo4j_stats)

# Execute query
results = query.execute_query("MATCH (n) RETURN count(n)")
print(results)

# Check system health
health_status = health.check_health()
print(health_status)

# Verify warm-up
exit_code = warmup_verify.verify_warmup()
```

## 📦 Package Structure

```
scripts/monitoring/
├── __init__.py                 # Package initialization
├── cli.py                      # Unified CLI (entry point)
├── setup.py                    # Installation configuration
├── README.md                   # This file
│
├── neo4j/                      # Neo4j management
│   ├── __init__.py
│   ├── stats.py                # Graph statistics
│   ├── query.py                # Query executor
│   ├── export.py               # Backup/export
│   ├── health.py               # Health checks
│   └── cleanup.py              # Safe cleanup
│
├── graphiti/                   # Graphiti monitoring
│   ├── __init__.py
│   ├── status.py               # Ingestion status
│   ├── metrics.py              # Entity/relation metrics
│   └── validate.py             # Validation checks
│
├── docling/                    # Docling monitoring
│   ├── __init__.py
│   ├── warmup_verify.py        # Verify warm-up
│   ├── cache_info.py           # Cache statistics
│   └── performance.py          # Conversion metrics
│
└── system/                     # System monitoring
    ├── __init__.py
    ├── health.py               # Overall health
    ├── resources.py            # CPU, memory, disk
    └── docker.py               # Container stats
```

## 🔧 Configuration

### API Base URLs

By default, the tools connect to:
- Backend API: `http://localhost:8000`
- Neo4j API: `http://localhost:8000/api/neo4j`

To use different URLs, set environment variables:

```bash
export API_BASE="http://your-server:8000/api"
diveteacher-monitor neo4j stats
```

### Timeouts

Default timeouts:
- Query operations: 30s
- Health checks: 10s
- Export operations: 120s

## 🐛 Troubleshooting

### Command not found

If `diveteacher-monitor` is not found after installation:

```bash
# Re-install
cd scripts/monitoring
pip install -e .

# Or use Python module syntax
python3 -m scripts.monitoring.cli system health
```

### Connection errors

If you get connection errors:

```bash
# Check backend is running
docker ps | grep rag-backend

# Check backend health
curl http://localhost:8000/api/health

# Check services are accessible
diveteacher-monitor system health
```

### Permission errors

If you get Docker permission errors:

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Or use sudo
sudo diveteacher-monitor system docker
```

## 📖 Related Documentation

- [Full Monitoring Guide](../../docs/MONITORING.md)
- [Production Readiness](../../docs/PRODUCTION-READINESS.md)
- [Testing Log](../../docs/TESTING-LOG.md)
- [Fixes Log](../../docs/FIXES-LOG.md)

## 💡 Examples

### Daily Monitoring Workflow

```bash
# 1. Check overall health
diveteacher-monitor system health

# 2. Check resource usage
diveteacher-monitor system resources

# 3. Check Neo4j stats
diveteacher-monitor neo4j stats

# 4. Verify warm-up
diveteacher-monitor docling verify
```

### After Document Upload

```bash
# Get upload_id from API response
UPLOAD_ID="abc-123-def-456"

# Monitor status
diveteacher-monitor graphiti status $UPLOAD_ID

# Check metrics
diveteacher-monitor graphiti metrics $UPLOAD_ID

# Validate results
diveteacher-monitor graphiti validate $UPLOAD_ID

# Check performance
diveteacher-monitor docling performance $UPLOAD_ID
```

### Before Testing

```bash
# Clear Neo4j (with backup)
diveteacher-monitor neo4j clear

# Verify it's empty
diveteacher-monitor neo4j stats

# Check system is healthy
diveteacher-monitor system health
```

### Debugging

```bash
# Check all Docker containers
diveteacher-monitor system docker

# Query specific data
diveteacher-monitor neo4j query "MATCH (n:EntityNode) RETURN n.name LIMIT 5"

# Check Neo4j health
diveteacher-monitor neo4j health

# Export for analysis
diveteacher-monitor neo4j export --format json
```

## 🎯 Best Practices

1. **Always check health first**: `diveteacher-monitor system health`
2. **Monitor resource usage**: `diveteacher-monitor system resources`
3. **Validate after ingestion**: `diveteacher-monitor graphiti validate <id>`
4. **Back up before clearing**: Automatic with `neo4j clear`
5. **Verify warm-up after rebuild**: `diveteacher-monitor docling verify`

## 🆘 Support

For issues or questions:
1. Check this README
2. Check [docs/MONITORING.md](../../docs/MONITORING.md)
3. Check [docs/TESTING-LOG.md](../../docs/TESTING-LOG.md)
4. Contact maintainer

---

**Version:** 1.0.0  
**Last Updated:** October 29, 2025  
**Maintainer:** DiveTeacher Team

