#!/bin/bash
#
# Neo4j Management CLI
# 
# Wrapper script for Neo4j management operations via REST API
# Provides easy command-line access to Neo4j stats, queries, exports, and cleanup
#
# Usage:
#   ./scripts/neo4j-cli.sh <command> [options]
#
# Commands:
#   stats       Get Neo4j statistics
#   query       Execute Cypher query
#   health      Check Neo4j health
#   export      Export graph data
#   clear       Clear all data (with confirmation)
#   download    Download export file
#

set -e  # Exit on error

# Configuration
API_BASE="${API_BASE:-http://localhost:8000/api/neo4j}"
TIMEOUT="${TIMEOUT:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if curl is available
if ! command -v curl &> /dev/null; then
    print_error "curl is required but not installed. Please install curl."
    exit 1
fi

# Check if jq is available (optional, for pretty JSON)
HAS_JQ=false
if command -v jq &> /dev/null; then
    HAS_JQ=true
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: stats
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_stats() {
    print_header "Neo4j Statistics"
    
    response=$(curl -s -X GET "${API_BASE}/stats" \
        -H "Content-Type: application/json" \
        --max-time "${TIMEOUT}")
    
    if [ $? -ne 0 ]; then
        print_error "Failed to fetch statistics"
        return 1
    fi
    
    if [ "$HAS_JQ" = true ]; then
        echo "$response" | jq '.'
        
        # Extract and display key metrics
        echo ""
        print_info "Summary:"
        total_nodes=$(echo "$response" | jq -r '.nodes.total')
        total_rels=$(echo "$response" | jq -r '.relationships.total')
        total_indexes=$(echo "$response" | jq -r '.indexes.total')
        
        echo "  • Nodes: $total_nodes"
        echo "  • Relationships: $total_rels"
        echo "  • Indexes: $total_indexes"
    else
        echo "$response"
        print_warning "Install 'jq' for pretty JSON output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: query
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_query() {
    if [ -z "$1" ]; then
        print_error "Cypher query required"
        echo "Usage: $0 query '<cypher_query>'"
        echo ""
        echo "Examples:"
        echo "  $0 query 'MATCH (n) RETURN count(n) as count'"
        echo "  $0 query 'MATCH (n:EntityNode) RETURN n.name LIMIT 10'"
        return 1
    fi
    
    cypher_query="$1"
    
    print_header "Executing Cypher Query"
    echo "Query: $cypher_query"
    echo ""
    
    payload=$(cat <<EOF
{
  "cypher": "$cypher_query",
  "params": {},
  "timeout": 30
}
EOF
)
    
    response=$(curl -s -X POST "${API_BASE}/query" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "${TIMEOUT}")
    
    if [ $? -ne 0 ]; then
        print_error "Query execution failed"
        return 1
    fi
    
    # Check for error
    if echo "$response" | grep -q '"detail"'; then
        print_error "Query failed:"
        if [ "$HAS_JQ" = true ]; then
            echo "$response" | jq -r '.detail'
        else
            echo "$response"
        fi
        return 1
    fi
    
    if [ "$HAS_JQ" = true ]; then
        echo "$response" | jq '.'
        
        # Extract summary
        echo ""
        print_info "Summary:"
        records_count=$(echo "$response" | jq -r '.summary.records_returned')
        exec_time=$(echo "$response" | jq -r '.summary.execution_time_ms')
        
        echo "  • Records returned: $records_count"
        echo "  • Execution time: ${exec_time}ms"
    else
        echo "$response"
        print_warning "Install 'jq' for pretty JSON output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_health() {
    print_header "Neo4j Health Check"
    
    response=$(curl -s -X GET "${API_BASE}/health" \
        -H "Content-Type: application/json" \
        --max-time "${TIMEOUT}")
    
    if [ $? -ne 0 ]; then
        print_error "Health check failed"
        return 1
    fi
    
    if [ "$HAS_JQ" = true ]; then
        status=$(echo "$response" | jq -r '.status')
        connection=$(echo "$response" | jq -r '.connection')
        latency=$(echo "$response" | jq -r '.latency_ms // "N/A"')
        
        if [ "$status" = "healthy" ]; then
            print_success "Neo4j is healthy"
            echo "  • Connection: $connection"
            echo "  • Latency: ${latency}ms"
        else
            print_error "Neo4j is unhealthy"
            echo "  • Connection: $connection"
            echo "  • Status: $status"
            
            issues=$(echo "$response" | jq -r '.issues[]' 2>/dev/null)
            if [ ! -z "$issues" ]; then
                echo "  • Issues:"
                echo "$issues" | while IFS= read -r issue; do
                    echo "    - $issue"
                done
            fi
        fi
    else
        echo "$response"
        print_warning "Install 'jq' for pretty JSON output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: export
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_export() {
    format="${1:-json}"
    
    if [[ ! "$format" =~ ^(json|cypher|graphml)$ ]]; then
        print_error "Invalid format: $format"
        echo "Supported formats: json, cypher, graphml"
        return 1
    fi
    
    print_header "Exporting Neo4j Data"
    echo "Format: $format"
    echo ""
    
    payload=$(cat <<EOF
{
  "format": "$format",
  "filters": {}
}
EOF
)
    
    response=$(curl -s -X POST "${API_BASE}/export" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "${TIMEOUT}")
    
    if [ $? -ne 0 ]; then
        print_error "Export failed"
        return 1
    fi
    
    if [ "$HAS_JQ" = true ]; then
        export_id=$(echo "$response" | jq -r '.export_id')
        download_url=$(echo "$response" | jq -r '.download_url')
        size_bytes=$(echo "$response" | jq -r '.size_bytes')
        record_count=$(echo "$response" | jq -r '.record_count')
        
        print_success "Export complete"
        echo "  • Export ID: $export_id"
        echo "  • Records: $record_count"
        echo "  • Size: $size_bytes bytes"
        echo "  • Download URL: ${API_BASE}${download_url}"
        echo ""
        print_info "To download: $0 download $export_id"
    else
        echo "$response"
        print_warning "Install 'jq' for pretty JSON output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: download
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_download() {
    if [ -z "$1" ]; then
        print_error "Export ID required"
        echo "Usage: $0 download <export_id>"
        return 1
    fi
    
    export_id="$1"
    output_file="${2:-neo4j_export_${export_id}}"
    
    print_header "Downloading Export"
    echo "Export ID: $export_id"
    echo "Output: $output_file"
    echo ""
    
    curl -L -X GET "${API_BASE}/export/${export_id}/download" \
        -o "$output_file" \
        --max-time "${TIMEOUT}"
    
    if [ $? -eq 0 ]; then
        file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        print_success "Download complete"
        echo "  • File: $output_file"
        echo "  • Size: $file_size bytes"
    else
        print_error "Download failed"
        return 1
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: clear
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_clear() {
    backup_first="${1:-true}"
    
    print_header "⚠️  CLEAR ALL NEO4J DATA ⚠️"
    echo ""
    print_warning "This will DELETE ALL nodes and relationships!"
    echo ""
    
    # Interactive confirmation
    echo -n "Are you sure? Type 'DELETE_ALL_DATA' to confirm: "
    read confirmation
    
    if [ "$confirmation" != "DELETE_ALL_DATA" ]; then
        print_info "Operation cancelled"
        return 0
    fi
    
    echo ""
    print_info "Proceeding with clear operation..."
    
    payload=$(cat <<EOF
{
  "confirm": true,
  "confirmation_code": "DELETE_ALL_DATA",
  "backup_first": $backup_first
}
EOF
)
    
    response=$(curl -s -X DELETE "${API_BASE}/clear" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time 60)
    
    if [ $? -ne 0 ]; then
        print_error "Clear operation failed"
        return 1
    fi
    
    # Check for error
    if echo "$response" | grep -q '"detail"'; then
        print_error "Clear failed:"
        if [ "$HAS_JQ" = true ]; then
            echo "$response" | jq -r '.detail'
        else
            echo "$response"
        fi
        return 1
    fi
    
    if [ "$HAS_JQ" = true ]; then
        status=$(echo "$response" | jq -r '.status')
        deleted_nodes=$(echo "$response" | jq -r '.deleted.nodes')
        deleted_rels=$(echo "$response" | jq -r '.deleted.relationships')
        backup_id=$(echo "$response" | jq -r '.backup_export_id // "none"')
        
        print_success "Database cleared"
        echo "  • Nodes deleted: $deleted_nodes"
        echo "  • Relationships deleted: $deleted_rels"
        echo "  • Backup ID: $backup_id"
        
        if [ "$backup_id" != "none" ]; then
            echo ""
            print_info "To restore backup: $0 download $backup_id"
        fi
    else
        echo "$response"
        print_warning "Install 'jq' for pretty JSON output"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command: help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cmd_help() {
    cat <<EOF

╔══════════════════════════════════════════════════════════════════════╗
║                       Neo4j Management CLI                          ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
  $0 <command> [options]

COMMANDS:
  stats                 Get Neo4j statistics (nodes, rels, indexes)
  query <cypher>        Execute Cypher query
  health                Check Neo4j connection health
  export [format]       Export graph data (json|cypher|graphml)
  download <id> [file]  Download exported file
  clear                 Clear all data (with confirmation & backup)
  help                  Show this help message

EXAMPLES:
  # Get statistics
  $0 stats

  # Check health
  $0 health

  # Execute query
  $0 query 'MATCH (n) RETURN count(n) as count'

  # Export data
  $0 export json

  # Download export
  $0 download abc-123-def export.json

  # Clear database (creates backup first)
  $0 clear

ENVIRONMENT:
  API_BASE    API base URL (default: http://localhost:8000/api/neo4j)
  TIMEOUT     Request timeout in seconds (default: 30)

REQUIREMENTS:
  • curl (required)
  • jq (optional, for pretty output)

NOTES:
  • Clear operation requires interactive confirmation
  • Backup is created by default before clearing
  • Exports are stored in backend/uploads/exports/

For more information, see docs/MONITORING.md

EOF
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

command="${1:-help}"

case "$command" in
    stats)
        cmd_stats
        ;;
    query)
        cmd_query "$2"
        ;;
    health)
        cmd_health
        ;;
    export)
        cmd_export "$2"
        ;;
    download)
        cmd_download "$2" "$3"
        ;;
    clear)
        cmd_clear "$2"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $command"
        echo ""
        cmd_help
        exit 1
        ;;
esac

exit $?

