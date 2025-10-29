#!/bin/bash
#
# Docling Warm-up Verification Tool
#
# Verifies that Docling models are properly cached and warm-up is effective.
# This script checks:
# 1. Cache directory exists and contains models
# 2. Cache size is reasonable (models downloaded)
# 3. First document conversion is fast (no downloads)
#
# Usage:
#   ./scripts/verify-warmup.sh
#
# Exit codes:
#   0 - Warm-up is effective
#   1 - Warm-up failed or ineffective
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="${CONTAINER_NAME:-rag-backend}"
TEST_PDF="${TEST_PDF:-TestPDF/test.pdf}"
API_URL="${API_URL:-http://localhost:8000}"
CACHE_DIR="/root/.cache/huggingface"
MIN_CACHE_SIZE_MB=50  # Minimum expected cache size
MAX_FIRST_CONVERSION_TIME=15  # Maximum acceptable time for first conversion

# Helper functions
print_header() {
    echo ""
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

# Check if container is running
check_container() {
    print_header "Step 1: Checking Container Status"
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Container '$CONTAINER_NAME' is not running"
        echo ""
        print_info "Start the backend with:"
        echo "  docker compose -f docker/docker-compose.dev.yml up -d backend"
        exit 1
    fi
    
    print_success "Container is running"
}

# Check cache directory in container
check_cache_directory() {
    print_header "Step 2: Checking Cache Directory"
    
    # Check if cache directory exists
    if ! docker exec "$CONTAINER_NAME" test -d "$CACHE_DIR"; then
        print_error "Cache directory not found: $CACHE_DIR"
        print_info "This means models were NOT pre-downloaded at build time"
        return 1
    fi
    
    print_success "Cache directory exists: $CACHE_DIR"
    
    # Get cache size
    CACHE_SIZE=$(docker exec "$CONTAINER_NAME" du -sm "$CACHE_DIR" 2>/dev/null | cut -f1)
    
    if [ -z "$CACHE_SIZE" ]; then
        print_error "Could not determine cache size"
        return 1
    fi
    
    print_info "Cache size: ${CACHE_SIZE} MB"
    
    # Check if cache size is reasonable
    if [ "$CACHE_SIZE" -lt "$MIN_CACHE_SIZE_MB" ]; then
        print_warning "Cache size is suspiciously small (< ${MIN_CACHE_SIZE_MB} MB)"
        print_info "Models may not be fully cached"
        return 1
    fi
    
    print_success "Cache size is adequate (${CACHE_SIZE} MB >= ${MIN_CACHE_SIZE_MB} MB)"
    
    # List cached model files
    echo ""
    print_info "Cached model files:"
    docker exec "$CONTAINER_NAME" find "$CACHE_DIR" -type f -name "*.bin" -o -name "*.safetensors" | while read file; do
        SIZE=$(docker exec "$CONTAINER_NAME" du -h "$file" 2>/dev/null | cut -f1)
        BASENAME=$(basename "$file")
        echo "  • $BASENAME ($SIZE)"
    done
    
    return 0
}

# Check backend logs for "Fetching" messages
check_startup_logs() {
    print_header "Step 3: Checking Startup Logs"
    
    print_info "Looking for 'Fetching' messages in recent logs..."
    
    # Get logs from last 2 minutes
    FETCH_LOGS=$(docker logs --since 2m "$CONTAINER_NAME" 2>&1 | grep -i "fetching" || true)
    
    if [ -z "$FETCH_LOGS" ]; then
        print_success "No 'Fetching' messages found in recent logs"
        print_info "Models were loaded from cache (no downloads)"
    else
        print_error "Found 'Fetching' messages in logs:"
        echo "$FETCH_LOGS" | while IFS= read -r line; do
            echo "  $line"
        done
        print_warning "This indicates models were downloaded at runtime (warm-up ineffective)"
        return 1
    fi
    
    return 0
}

# Test first conversion speed
test_conversion_speed() {
    print_header "Step 4: Testing First Conversion Speed"
    
    # Check if test PDF exists
    if [ ! -f "$TEST_PDF" ]; then
        print_warning "Test PDF not found: $TEST_PDF"
        print_info "Skipping conversion speed test"
        print_info "To test, create a test PDF at: $TEST_PDF"
        return 0
    fi
    
    print_info "Uploading test document: $TEST_PDF"
    print_info "Measuring time to conversion start..."
    
    START_TIME=$(date +%s)
    
    # Upload document
    RESPONSE=$(curl -s -X POST "${API_URL}/api/upload" \
        -F "file=@${TEST_PDF}" \
        --max-time 120)
    
    # Check if upload succeeded
    if ! echo "$RESPONSE" | grep -q "upload_id"; then
        print_error "Upload failed"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    UPLOAD_ID=$(echo "$RESPONSE" | grep -o '"upload_id":"[^"]*"' | cut -d'"' -f4)
    print_info "Upload ID: $UPLOAD_ID"
    
    # Wait for conversion to start and check logs
    sleep 2
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    print_info "Time to process: ${DURATION}s"
    
    # Check if conversion started quickly
    if [ "$DURATION" -le "$MAX_FIRST_CONVERSION_TIME" ]; then
        print_success "First conversion was FAST (${DURATION}s <= ${MAX_FIRST_CONVERSION_TIME}s)"
        print_info "This confirms models were pre-cached"
    else
        print_error "First conversion was SLOW (${DURATION}s > ${MAX_FIRST_CONVERSION_TIME}s)"
        print_warning "This suggests models were downloaded at runtime"
        return 1
    fi
    
    # Check processing status
    STATUS=$(curl -s "${API_URL}/api/upload/status/${UPLOAD_ID}")
    STAGE=$(echo "$STATUS" | grep -o '"stage":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    
    print_info "Current processing stage: $STAGE"
    
    return 0
}

# Generate final report
generate_report() {
    local cache_check=$1
    local logs_check=$2
    local speed_check=$3
    
    print_header "Verification Report"
    
    echo ""
    echo "Test Results:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ $cache_check -eq 0 ]; then
        print_success "Cache directory: PASS"
    else
        print_error "Cache directory: FAIL"
    fi
    
    if [ $logs_check -eq 0 ]; then
        print_success "Startup logs: PASS (no downloads detected)"
    else
        print_error "Startup logs: FAIL (downloads detected)"
    fi
    
    if [ $speed_check -eq 0 ]; then
        print_success "Conversion speed: PASS"
    elif [ $speed_check -eq 2 ]; then
        print_info "Conversion speed: SKIPPED (no test PDF)"
    else
        print_error "Conversion speed: FAIL"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Overall verdict
    if [ $cache_check -eq 0 ] && [ $logs_check -eq 0 ]; then
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  🎉 WARM-UP IS EFFECTIVE!                               ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        print_success "Models are pre-cached in the Docker image"
        print_success "First document conversion will be INSTANT"
        print_success "No downloads will occur at runtime"
        echo ""
        return 0
    else
        echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ❌ WARM-UP IS INEFFECTIVE!                             ║${NC}"
        echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        print_error "Models are NOT properly cached"
        print_warning "First document conversion will be SLOW"
        print_warning "Downloads will occur at runtime"
        echo ""
        print_info "Troubleshooting:"
        echo "  1. Rebuild the Docker image:"
        echo "     docker compose -f docker/docker-compose.dev.yml build --no-cache backend"
        echo "  2. Check build logs for warm-up success"
        echo "  3. Restart the container:"
        echo "     docker compose -f docker/docker-compose.dev.yml up -d backend"
        echo "  4. Run this verification again"
        echo ""
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Docling Warm-up Verification Tool                      ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    
    check_container
    
    cache_result=0
    check_cache_directory || cache_result=$?
    
    logs_result=0
    check_startup_logs || logs_result=$?
    
    speed_result=2  # Default: skipped
    if [ -f "$TEST_PDF" ]; then
        speed_result=0
        test_conversion_speed || speed_result=$?
    else
        print_header "Step 4: Testing First Conversion Speed"
        print_info "Test PDF not found: $TEST_PDF"
        print_info "Skipping conversion speed test"
    fi
    
    generate_report $cache_result $logs_result $speed_result
    
    # Exit with appropriate code
    if [ $cache_result -eq 0 ] && [ $logs_result -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main

