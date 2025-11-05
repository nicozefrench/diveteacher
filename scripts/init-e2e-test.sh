#!/bin/bash
# init-e2e-test.sh - Initialize system for End-to-End testing
#
# ⚠️  CRITICAL DIFFERENCE FROM WARMUP:
# - THIS SCRIPT: Cleans DB for TESTING (fresh start for E2E tests)
# - WARMUP: Prepares models for PRODUCTION (preserves DB for ingestion sessions)
#
# This script prepares the RAG system for a clean E2E test by:
# 1. Checking current Neo4j state
# 2. ⚠️  CLEANING Neo4j + Graphiti database (DEFAULT - can skip with --skip-cleanup)
# 3. Warming up Docling + ARIA Chunker models
# 4. Verifying all services are ready
#
# ══════════════════════════════════════════════════════════════════════
# USE CASES:
# ══════════════════════════════════════════════════════════════════════
#
# E2E TESTING (clean slate):
#   ./scripts/init-e2e-test.sh
#   → Cleans DB + Warms up models
#   → Ready for test with empty Neo4j
#
# PRODUCTION INGESTION (preserve DB):
#   docker-compose up -d
#   → Warmup runs automatically (models ready, DB untouched)
#   → Ready for multi-document ingestion sessions
#
# ══════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./scripts/init-e2e-test.sh [options]
#
# Options:
#   --skip-cleanup    Skip Neo4j cleanup (keep existing data) - USE FOR PRODUCTION
#   --force-cleanup   Force cleanup even if database is already empty
#   --skip-warmup     Skip Docling warm-up (models already cached)
#   --quiet           Minimal output
#   --help            Show this help message
#
# Examples:
#   ./scripts/init-e2e-test.sh                    # E2E TEST: Full cleanup + warmup
#   ./scripts/init-e2e-test.sh --skip-cleanup    # PRODUCTION: Only warmup, keep DB
#   ./scripts/init-e2e-test.sh --skip-warmup     # Only cleanup, skip warmup
#
# ⚠️  IMPORTANT:
# - Default behavior: CLEANS DATABASE (for E2E testing)
# - Production use: Add --skip-cleanup to preserve data
# - Warmup alone: Just restart backend (warmup runs automatically)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Default options
SKIP_CLEANUP=false
FORCE_CLEANUP=false
SKIP_WARMUP=false
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-cleanup)
      SKIP_CLEANUP=true
      shift
      ;;
    --force-cleanup)
      FORCE_CLEANUP=true
      shift
      ;;
    --skip-warmup)
      SKIP_WARMUP=true
      shift
      ;;
    --quiet)
      QUIET=true
      shift
      ;;
    --help)
      head -n 25 "$0" | tail -n 23
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Logging functions
log_header() {
  if [ "$QUIET" = false ]; then
    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║  $1${NC}"
    echo -e "${BOLD}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
  fi
}

log_section() {
  if [ "$QUIET" = false ]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  fi
}

log_info() {
  if [ "$QUIET" = false ]; then
    echo -e "${BLUE}ℹ️  $1${NC}"
  fi
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

log_step() {
  if [ "$QUIET" = false ]; then
    echo ""
    echo -e "${BOLD}Step $1: $2${NC}"
    echo -e "─────────────────────────────────────"
  fi
}

# Check if required commands exist
check_dependencies() {
  local missing=()
  
  command -v docker >/dev/null 2>&1 || missing+=("docker")
  command -v curl >/dev/null 2>&1 || missing+=("curl")
  command -v jq >/dev/null 2>&1 || missing+=("jq")
  
  if [ ${#missing[@]} -ne 0 ]; then
    log_error "Missing required commands: ${missing[*]}"
    echo "Please install them and try again."
    exit 1
  fi
}

# Check if Docker containers are running
check_containers() {
  log_step 1 "Checking Docker containers"
  
  # NOTE: rag-ollama removed - Ollama now runs natively on Mac host (Metal GPU)
  # See: Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md
  local required_containers=("rag-backend" "rag-neo4j")
  local missing=()
  
  for container in "${required_containers[@]}"; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
      missing+=("$container")
    fi
  done
  
  if [ ${#missing[@]} -ne 0 ]; then
    log_error "Required containers not running: ${missing[*]}"
    echo ""
    echo "Please start the containers with:"
    echo "  docker compose -f docker/docker-compose.dev.yml up -d"
    exit 1
  fi
  
  log_success "All required containers are running"
  
  if [ "$QUIET" = false ]; then
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(NAMES|rag-)"
  fi
}

# Check and optionally clean Neo4j
handle_neo4j_cleanup() {
  log_step 2 "Neo4j Database Cleanup"
  
  # Get current state
  log_info "Checking current Neo4j state..."
  
  NEO4J_STATS=$(curl -s http://localhost:8000/api/neo4j/stats 2>/dev/null)
  
  if [ $? -ne 0 ] || [ -z "$NEO4J_STATS" ]; then
    log_error "Failed to fetch Neo4j stats. Is the backend running?"
    exit 1
  fi
  
  TOTAL_NODES=$(echo "$NEO4J_STATS" | jq -r '.nodes.total' 2>/dev/null || echo "0")
  TOTAL_RELS=$(echo "$NEO4J_STATS" | jq -r '.relationships.total' 2>/dev/null || echo "0")
  
  log_info "Current state: $TOTAL_NODES nodes, $TOTAL_RELS relationships"
  
  # Decide if cleanup is needed
  NEEDS_CLEANUP=false
  
  if [ "$SKIP_CLEANUP" = true ]; then
    log_warning "Cleanup skipped (--skip-cleanup flag)"
    return 0
  fi
  
  if [ "$TOTAL_NODES" -eq 0 ] && [ "$TOTAL_RELS" -eq 0 ]; then
    if [ "$FORCE_CLEANUP" = true ]; then
      log_info "Database is already empty, but forcing cleanup (--force-cleanup)"
      NEEDS_CLEANUP=true
    else
      log_success "Database is already clean (0 nodes, 0 relationships)"
      return 0
    fi
  else
    log_warning "Database contains data: $TOTAL_NODES nodes, $TOTAL_RELS relationships"
    NEEDS_CLEANUP=true
  fi
  
  # Perform cleanup if needed
  if [ "$NEEDS_CLEANUP" = true ]; then
    log_info "Cleaning Neo4j + Graphiti database..."
    
    CLEANUP_RESPONSE=$(curl -s -X DELETE "http://localhost:8000/api/neo4j/clear" \
      -H "Content-Type: application/json" \
      -d '{
        "confirm": true,
        "confirmation_code": "DELETE_ALL_DATA",
        "backup_first": false
      }' 2>/dev/null)
    
    if [ $? -ne 0 ]; then
      log_error "Failed to clean database"
      exit 1
    fi
    
    # Check if cleanup was successful
    # API returns {"status": "cleared", "deleted": {"nodes": X, "relationships": Y}}
    STATUS=$(echo "$CLEANUP_RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")
    
    if [ "$STATUS" = "cleared" ]; then
      DELETED_NODES=$(echo "$CLEANUP_RESPONSE" | jq -r '.deleted.nodes' 2>/dev/null || echo "N/A")
      DELETED_RELS=$(echo "$CLEANUP_RESPONSE" | jq -r '.deleted.relationships' 2>/dev/null || echo "N/A")
      log_success "Database cleaned: $DELETED_NODES nodes and $DELETED_RELS relationships deleted"
    else
      log_error "Cleanup failed. Status: $STATUS, Response: $CLEANUP_RESPONSE"
      exit 1
    fi
    
    # Verify cleanup
    sleep 2
    NEO4J_STATS=$(curl -s http://localhost:8000/api/neo4j/stats 2>/dev/null)
    FINAL_NODES=$(echo "$NEO4J_STATS" | jq -r '.nodes.total' 2>/dev/null || echo "?")
    FINAL_RELS=$(echo "$NEO4J_STATS" | jq -r '.relationships.total' 2>/dev/null || echo "?")
    
    if [ "$FINAL_NODES" = "0" ] && [ "$FINAL_RELS" = "0" ]; then
      log_success "Verification: Database is now clean (0 nodes, 0 relationships)"
    else
      log_warning "Verification: $FINAL_NODES nodes, $FINAL_RELS relationships remaining"
    fi
  fi
}

# Warm-up Docling models
warmup_docling() {
  log_step 3 "Docling Model Warm-up"
  
  if [ "$SKIP_WARMUP" = true ]; then
    log_warning "Warm-up skipped (--skip-warmup flag)"
    return 0
  fi
  
  log_info "Running Docling warm-up script..."
  log_info "This ensures models are cached and ready for conversion"
  
  if [ "$QUIET" = false ]; then
    echo ""
    echo -e "${YELLOW}⏱️  Expected duration: 5-10 seconds (if models already cached)${NC}"
    echo -e "${YELLOW}⏱️  First-time run: 2-3 minutes (downloading ~200MB)${NC}"
    echo ""
  fi
  
  # Run warmup and capture output
  WARMUP_OUTPUT=$(docker exec rag-backend python3 -m app.warmup 2>&1)
  WARMUP_EXIT=$?
  
  if [ $WARMUP_EXIT -ne 0 ]; then
    log_error "Warm-up script failed with exit code $WARMUP_EXIT"
    if [ "$QUIET" = false ]; then
      echo "$WARMUP_OUTPUT"
    fi
    exit 1
  fi
  
  # Check if warm-up was successful
  if echo "$WARMUP_OUTPUT" | grep -q "COMPLETE WARM-UP FINISHED"; then
    log_success "Docling warm-up completed successfully"
    
    # Check for ARIA Chunker warmup
    if echo "$WARMUP_OUTPUT" | grep -q "ARIA Chunker initialized successfully"; then
      log_success "ARIA Chunker (RecursiveCharacterTextSplitter) warmed up"
    else
      log_warning "ARIA Chunker warmup not confirmed (will init on first upload)"
    fi
    
    # Check for System nominal status
    if echo "$WARMUP_OUTPUT" | grep -q "System 100% nominal"; then
      log_success "System 100% nominal for ingestion sessions"
    fi
    
    # Verify DB preservation message
    if echo "$WARMUP_OUTPUT" | grep -q "does NOT touch database"; then
      if [ "$QUIET" = false ]; then
        echo ""
        echo -e "${CYAN}ℹ️  Warmup preserved database (as designed)${NC}"
      fi
    fi
    
    if [ "$QUIET" = false ]; then
      echo ""
      echo "Key events:"
      echo "$WARMUP_OUTPUT" | grep -E "(Starting|Warming|Initialized|Complete|VALIDATION|ARIA Chunker)" | head -12
    fi
  else
    log_warning "Warm-up completed but validation unclear"
    if [ "$QUIET" = false ]; then
      echo ""
      echo "Output:"
      echo "$WARMUP_OUTPUT" | tail -15
    fi
  fi
}

# Verify all services are ready
verify_services() {
  log_step 4 "Verifying Services"
  
  local all_healthy=true
  
  # Check Backend
  log_info "Checking backend API..."
  BACKEND_HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null)
  if [ $? -eq 0 ] && [ -n "$BACKEND_HEALTH" ]; then
    log_success "Backend API: Healthy"
  else
    log_error "Backend API: Not responding"
    all_healthy=false
  fi
  
  # Check Ollama (native baremetal, not Docker)
  log_info "Checking Ollama LLM (native baremetal)..."
  OLLAMA_MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null)
  if [ -n "$OLLAMA_MODELS" ]; then
    log_success "Ollama LLM (Metal GPU): $(echo "$OLLAMA_MODELS" | head -1)"
  else
    log_error "Ollama LLM: Not responding or no models loaded"
    log_error "Make sure 'ollama serve' is running in Terminal 1"
    log_error "See: Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md"
    all_healthy=false
  fi
  
  # Check Neo4j
  log_info "Checking Neo4j database..."
  NEO4J_STATS=$(curl -s http://localhost:8000/api/neo4j/stats 2>/dev/null)
  NEO4J_STATUS=$(echo "$NEO4J_STATS" | jq -r '.status' 2>/dev/null)
  if [ "$NEO4J_STATUS" = "healthy" ]; then
    NEO4J_VERSION=$(echo "$NEO4J_STATS" | jq -r '.version' 2>/dev/null)
    log_success "Neo4j: Online (version $NEO4J_VERSION)"
  else
    log_warning "Neo4j: Status unclear (status: $NEO4J_STATUS)"
  fi
  
  # Check DocumentQueue (ARIA v2.0.0)
  log_info "Checking DocumentQueue status..."
  QUEUE_STATUS=$(curl -s http://localhost:8000/api/queue/status 2>/dev/null)
  if [ -n "$QUEUE_STATUS" ]; then
    QUEUE_SIZE=$(echo "$QUEUE_STATUS" | jq -r '.queue_size // "?"')
    PROCESSING=$(echo "$QUEUE_STATUS" | jq -r '.processing // "?"')
    COMPLETED=$(echo "$QUEUE_STATUS" | jq -r '.completed_count // "?"')
    
    if [ "$QUEUE_SIZE" = "0" ] && [ "$PROCESSING" = "false" ]; then
      log_success "DocumentQueue: Ready (empty, idle)"
    else
      log_warning "DocumentQueue: Active (${QUEUE_SIZE} queued, processing: ${PROCESSING}, completed: ${COMPLETED})"
      if [ "$QUIET" = false ]; then
        echo ""
        echo -e "${YELLOW}   ⚠️  Queue is not empty or currently processing${NC}"
        echo -e "${YELLOW}   This may affect E2E test results${NC}"
        echo -e "${YELLOW}   Consider waiting for queue to finish${NC}"
      fi
    fi
  else
    log_warning "DocumentQueue: Cannot check status (endpoint not responding)"
  fi
  
  # Check Frontend (optional)
  if docker ps --format '{{.Names}}' | grep -q "^rag-frontend$"; then
    log_info "Checking frontend..."
    if curl -s http://localhost:5173/ >/dev/null 2>&1; then
      log_success "Frontend UI: Accessible (http://localhost:5173/)"
    else
      log_warning "Frontend UI: Not responding (may still be starting)"
    fi
  fi
  
  if [ "$all_healthy" = false ]; then
    log_error "Some services are not healthy. Please check logs."
    exit 1
  fi
}

# Display final summary
display_summary() {
  log_section "📊 INITIALIZATION SUMMARY"
  
  # Get final Neo4j state
  NEO4J_STATS=$(curl -s http://localhost:8000/api/neo4j/stats 2>/dev/null)
  FINAL_NODES=$(echo "$NEO4J_STATS" | jq -r '.nodes.total' 2>/dev/null || echo "?")
  FINAL_RELS=$(echo "$NEO4J_STATS" | jq -r '.relationships.total' 2>/dev/null || echo "?")
  
  # Get DocumentQueue status
  QUEUE_DATA=$(curl -s http://localhost:8000/api/queue/status 2>/dev/null)
  QUEUE_SIZE=$(echo "$QUEUE_DATA" | jq -r '.queue_size // "?"')
  QUEUE_COMPLETED=$(echo "$QUEUE_DATA" | jq -r '.completed_count // "?"')
  
  echo ""
  echo -e "${BOLD}System Status:${NC}"
  echo "  • Neo4j Database: $FINAL_NODES nodes, $FINAL_RELS relationships"
  echo "  • Docling Models: $([ "$SKIP_WARMUP" = true ] && echo "Not warmed up" || echo "Warmed up and ready")"
  echo "  • ARIA Chunker: $([ "$SKIP_WARMUP" = true ] && echo "Not warmed up" || echo "RecursiveCharacterTextSplitter ready (3000 tokens/chunk)")"
  echo "  • DocumentQueue: ${QUEUE_SIZE} queued, ${QUEUE_COMPLETED} completed"
  echo "  • Backend API: Healthy"
  echo "  • Ollama LLM: Ready"
  echo ""
  
  if docker ps --format '{{.Names}}' | grep -q "^rag-frontend$"; then
    echo -e "${BOLD}Frontend URL:${NC} ${CYAN}http://localhost:5173/${NC}"
    echo ""
  fi
  
  log_section "🎯 READY FOR E2E TEST"
  
  echo ""
  echo -e "${BOLD}Next Steps:${NC}"
  echo "  1. Open browser: http://localhost:5173/"
  echo "  2. Navigate to 'Document Upload' tab"
  echo "  3. Upload a test document (e.g., TestPDF/test.pdf)"
  echo "  4. Monitor progress in real-time"
  echo "  5. Verify completion and check Neo4j stats"
  echo ""
  echo -e "${BOLD}Monitoring Commands (ARIA v2.0.0):${NC}"
  echo "  • Queue status:  ./scripts/monitor-queue.sh"
  echo "  • Backend logs:  ./scripts/monitor_ingestion.sh [upload_id]"
  echo "  • Upload status: ./scripts/monitor-upload.sh <upload_id>"
  echo "  • Neo4j stats:   curl -s http://localhost:8000/api/neo4j/stats | jq"
  echo ""
  
  if [ "$SKIP_CLEANUP" = true ]; then
    echo -e "${YELLOW}⚠️  DATABASE NOT CLEANED (--skip-cleanup flag used)${NC}"
    echo -e "${YELLOW}   • Current data: ${FINAL_NODES} nodes, ${FINAL_RELS} relationships${NC}"
    echo -e "${YELLOW}   • Mode: PRODUCTION INGESTION (additive)${NC}"
    echo -e "${YELLOW}   • New uploads will ADD to existing knowledge graph${NC}"
    echo ""
  else
    echo -e "${GREEN}✅ DATABASE CLEANED for E2E testing${NC}"
    echo -e "${GREEN}   • Fresh start: 0 nodes, 0 relationships${NC}"
    echo -e "${GREEN}   • Mode: E2E TESTING${NC}"
    echo -e "${GREEN}   • Ready for clean test run${NC}"
    echo ""
  fi
  
  log_success "System initialized and ready for E2E testing!"
}

# Main execution
main() {
  log_header "🧪 E2E TEST INITIALIZATION"
  
  if [ "$QUIET" = false ]; then
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Purpose: Prepare system for End-to-End testing"
    echo ""
  fi
  
  check_dependencies
  check_containers
  handle_neo4j_cleanup
  warmup_docling
  verify_services
  display_summary
}

# Run main function
main

exit 0

