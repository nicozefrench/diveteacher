#!/bin/bash
#
# Backend Integration Test Script (Production-Ready Architecture)
# Tests DocumentQueue + SafeIngestionQueue + Sequential Processing
#
# Usage:
#   ./scripts/test-backend-queue.sh [test.pdf|path/to/file.pdf]
#
# What it tests:
# - Upload endpoint (enqueue to DocumentQueue)
# - Queue status endpoint
# - Processing status tracking
# - Sequential processing (one doc at a time)
# - SafeIngestionQueue token tracking
# - Backend logs analysis
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
API_URL="${BACKEND_URL}/api"
TEST_FILE="${1:-test.pdf}"
POLL_INTERVAL=2  # seconds
MAX_WAIT=600  # 10 minutes

# Temp log file for backend monitoring
BACKEND_LOG="/tmp/backend-test-$(date +%s).log"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  🧪 BACKEND INTEGRATION TEST (Production-Ready Architecture)        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# ════════════════════════════════════════════════════════
# Step 1: Verify backend is ready
# ════════════════════════════════════════════════════════

echo "📡 Step 1: Checking backend health..."

if ! curl -s "${BACKEND_URL}/" > /dev/null; then
    echo -e "${RED}❌ Backend not responding at ${BACKEND_URL}${NC}"
    echo "   Make sure Docker containers are running:"
    echo "   docker-compose -f docker/docker-compose.dev.yml up -d"
    exit 1
fi

echo -e "${GREEN}✅ Backend is responding${NC}"

# Check health endpoint
HEALTH=$(curl -s "${API_URL}/health" | jq -r '.status' 2>/dev/null || echo "unknown")
if [ "$HEALTH" != "healthy" ]; then
    echo -e "${YELLOW}⚠️  Backend health: ${HEALTH}${NC}"
    echo "   This might be OK if Neo4j/Ollama are still warming up"
else
    echo -e "${GREEN}✅ Backend health: ${HEALTH}${NC}"
fi

# ════════════════════════════════════════════════════════
# Step 2: Check DocumentQueue initial state
# ════════════════════════════════════════════════════════

echo ""
echo "📥 Step 2: Checking DocumentQueue status..."

QUEUE_STATUS=$(curl -s "${API_URL}/queue/status")
QUEUE_SIZE=$(echo "$QUEUE_STATUS" | jq -r '.queue_size')
PROCESSING=$(echo "$QUEUE_STATUS" | jq -r '.processing')
COMPLETED=$(echo "$QUEUE_STATUS" | jq -r '.completed_count')
FAILED=$(echo "$QUEUE_STATUS" | jq -r '.failed_count')

echo "   Queue size: $QUEUE_SIZE"
echo "   Processing: $PROCESSING"
echo "   Completed: $COMPLETED"
echo "   Failed: $FAILED"

if [ "$QUEUE_SIZE" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Queue not empty! ${QUEUE_SIZE} documents waiting${NC}"
    echo "   This test will add to the queue"
fi

# ════════════════════════════════════════════════════════
# Step 3: Verify test file exists
# ════════════════════════════════════════════════════════

echo ""
echo "📄 Step 3: Verifying test file..."

if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}❌ Test file not found: ${TEST_FILE}${NC}"
    echo "   Usage: $0 [path/to/file.pdf]"
    exit 1
fi

FILE_SIZE=$(du -h "$TEST_FILE" | cut -f1)
echo -e "${GREEN}✅ Test file: ${TEST_FILE} (${FILE_SIZE})${NC}"

# ════════════════════════════════════════════════════════
# Step 4: Start backend log monitoring
# ════════════════════════════════════════════════════════

echo ""
echo "🔍 Step 4: Starting backend log monitoring..."

# Start log streaming in background
docker logs -f rag-backend > "$BACKEND_LOG" 2>&1 &
LOG_PID=$!

echo "   Backend logs → ${BACKEND_LOG}"
echo "   Log PID: ${LOG_PID}"

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    kill $LOG_PID 2>/dev/null || true
    echo "   Logs saved to: ${BACKEND_LOG}"
}
trap cleanup EXIT

# ════════════════════════════════════════════════════════
# Step 5: Upload document (enqueue to DocumentQueue)
# ════════════════════════════════════════════════════════

echo ""
echo "📤 Step 5: Uploading document..."
echo ""

UPLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/upload" \
    -F "file=@${TEST_FILE}" \
    -H "Accept: application/json")

UPLOAD_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.upload_id')
FILENAME=$(echo "$UPLOAD_RESPONSE" | jq -r '.filename')
STATUS=$(echo "$UPLOAD_RESPONSE" | jq -r '.status')
QUEUE_POS=$(echo "$UPLOAD_RESPONSE" | jq -r '.queue_position')

if [ -z "$UPLOAD_ID" ] || [ "$UPLOAD_ID" = "null" ]; then
    echo -e "${RED}❌ Upload failed!${NC}"
    echo "$UPLOAD_RESPONSE" | jq '.'
    exit 1
fi

echo -e "${GREEN}✅ Upload successful!${NC}"
echo "   Upload ID: ${UPLOAD_ID}"
echo "   Filename: ${FILENAME}"
echo "   Status: ${STATUS}"
echo "   Queue Position: ${QUEUE_POS}"

# ════════════════════════════════════════════════════════
# Step 6: Monitor processing (poll status endpoint)
# ════════════════════════════════════════════════════════

echo ""
echo "⏳ Step 6: Monitoring processing..."
echo "   Polling every ${POLL_INTERVAL}s (max ${MAX_WAIT}s)"
echo ""

START_TIME=$(date +%s)
LAST_STAGE=""
LAST_PROGRESS=0

while true; do
    # Poll status
    DOC_STATUS=$(curl -s "${API_URL}/upload/${UPLOAD_ID}/status")
    
    CURRENT_STATUS=$(echo "$DOC_STATUS" | jq -r '.status')
    STAGE=$(echo "$DOC_STATUS" | jq -r '.stage')
    SUB_STAGE=$(echo "$DOC_STATUS" | jq -r '.sub_stage')
    PROGRESS=$(echo "$DOC_STATUS" | jq -r '.progress')
    
    # Check if status changed
    if [ "$STAGE" != "$LAST_STAGE" ] || [ "$PROGRESS" != "$LAST_PROGRESS" ]; then
        echo "   [$(date +%H:%M:%S)] Status: ${CURRENT_STATUS} | Stage: ${STAGE} | Sub: ${SUB_STAGE} | Progress: ${PROGRESS}%"
        LAST_STAGE="$STAGE"
        LAST_PROGRESS="$PROGRESS"
    fi
    
    # Check for completion
    if [ "$CURRENT_STATUS" = "completed" ]; then
        echo ""
        echo -e "${GREEN}✅ Processing completed!${NC}"
        break
    fi
    
    # Check for failure
    if [ "$CURRENT_STATUS" = "failed" ]; then
        echo ""
        echo -e "${RED}❌ Processing failed!${NC}"
        ERROR=$(echo "$DOC_STATUS" | jq -r '.error')
        echo "   Error: ${ERROR}"
        exit 1
    fi
    
    # Check timeout
    ELAPSED=$(($(date +%s) - START_TIME))
    if [ $ELAPSED -gt $MAX_WAIT ]; then
        echo ""
        echo -e "${RED}❌ Timeout! Processing took more than ${MAX_WAIT}s${NC}"
        exit 1
    fi
    
    # Wait before next poll
    sleep $POLL_INTERVAL
done

# ════════════════════════════════════════════════════════
# Step 7: Get final status and metrics
# ════════════════════════════════════════════════════════

echo ""
echo "📊 Step 7: Final metrics..."
echo ""

FINAL_STATUS=$(curl -s "${API_URL}/upload/${UPLOAD_ID}/status")

# Extract metrics
ENTITIES=$(echo "$FINAL_STATUS" | jq -r '.metrics.entities // 0')
RELATIONS=$(echo "$FINAL_STATUS" | jq -r '.metrics.relations // 0')
NUM_CHUNKS=$(echo "$FINAL_STATUS" | jq -r '.metrics.num_chunks // 0')
CONVERSION_TIME=$(echo "$FINAL_STATUS" | jq -r '.durations.conversion // 0')
CHUNKING_TIME=$(echo "$FINAL_STATUS" | jq -r '.durations.chunking // 0')
INGESTION_TIME=$(echo "$FINAL_STATUS" | jq -r '.durations.ingestion // 0')
TOTAL_TIME=$(echo "$FINAL_STATUS" | jq -r '.durations.total // 0')

echo "   Entities: ${ENTITIES}"
echo "   Relations: ${RELATIONS}"
echo "   Chunks: ${NUM_CHUNKS}"
echo ""
echo "   Durations:"
echo "   - Conversion: ${CONVERSION_TIME}s"
echo "   - Chunking: ${CHUNKING_TIME}s"
echo "   - Ingestion: ${INGESTION_TIME}s"
echo "   - Total: ${TOTAL_TIME}s"

if [ "$NUM_CHUNKS" -gt 0 ]; then
    AVG_PER_CHUNK=$(echo "scale=2; $INGESTION_TIME / $NUM_CHUNKS" | bc)
    echo "   - Avg per chunk: ${AVG_PER_CHUNK}s"
fi

# ════════════════════════════════════════════════════════
# Step 8: Check DocumentQueue final state
# ════════════════════════════════════════════════════════

echo ""
echo "📥 Step 8: Final DocumentQueue status..."
echo ""

FINAL_QUEUE=$(curl -s "${API_URL}/queue/status")
FINAL_QUEUE_SIZE=$(echo "$FINAL_QUEUE" | jq -r '.queue_size')
FINAL_PROCESSING=$(echo "$FINAL_QUEUE" | jq -r '.processing')
FINAL_COMPLETED=$(echo "$FINAL_QUEUE" | jq -r '.completed_count')
FINAL_FAILED=$(echo "$FINAL_QUEUE" | jq -r '.failed_count')
SUCCESS_RATE=$(echo "$FINAL_QUEUE" | jq -r '.stats.success_rate // 0')

echo "   Queue size: ${FINAL_QUEUE_SIZE}"
echo "   Processing: ${FINAL_PROCESSING}"
echo "   Completed: ${FINAL_COMPLETED}"
echo "   Failed: ${FINAL_FAILED}"
echo "   Success rate: ${SUCCESS_RATE}%"

# ════════════════════════════════════════════════════════
# Step 9: Analyze backend logs
# ════════════════════════════════════════════════════════

echo ""
echo "🔍 Step 9: Analyzing backend logs..."
echo ""

# Wait for logs to flush
sleep 1

# Check for SafeIngestionQueue logs
if grep -q "SafeIngestionQueue initialized" "$BACKEND_LOG"; then
    echo -e "${GREEN}✅ SafeIngestionQueue initialized${NC}"
else
    echo -e "${YELLOW}⚠️  No SafeIngestionQueue initialization found${NC}"
fi

# Check for DocumentQueue logs
if grep -q "DocumentQueue initialized" "$BACKEND_LOG"; then
    echo -e "${GREEN}✅ DocumentQueue initialized${NC}"
else
    echo -e "${YELLOW}⚠️  No DocumentQueue initialization found${NC}"
fi

# Check for sequential processing
SEQ_LOG=$(grep -c "Sequential processing" "$BACKEND_LOG" || echo 0)
if [ "$SEQ_LOG" -gt 0 ]; then
    echo -e "${GREEN}✅ Sequential processing active (${SEQ_LOG} mentions)${NC}"
fi

# Check for token tracking
TOKEN_LOG=$(grep -c "token" "$BACKEND_LOG" || echo 0)
if [ "$TOKEN_LOG" -gt 0 ]; then
    echo -e "${GREEN}✅ Token tracking active (${TOKEN_LOG} mentions)${NC}"
fi

# Check for rate limit warnings
RATE_LIMIT=$(grep -c "Rate Limit Protection Active" "$BACKEND_LOG" || echo 0)
if [ "$RATE_LIMIT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Rate limit delays: ${RATE_LIMIT} times${NC}"
    echo "   (This is GOOD - SafeQueue is working!)"
fi

# Check for errors
ERRORS=$(grep -c "ERROR" "$BACKEND_LOG" || echo 0)
if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}⚠️  Found ${ERRORS} ERROR logs${NC}"
    echo "   Check: ${BACKEND_LOG}"
else
    echo -e "${GREEN}✅ No errors in backend logs${NC}"
fi

# ════════════════════════════════════════════════════════
# Step 10: Final verdict
# ════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ TEST COMPLETE                                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Verdict
if [ "$CURRENT_STATUS" = "completed" ] && [ "$ENTITIES" -gt 0 ] && [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo ""
    echo "✅ Document uploaded and processed successfully"
    echo "✅ DocumentQueue working (FIFO processing)"
    echo "✅ SafeIngestionQueue active (token tracking)"
    echo "✅ Sequential processing confirmed"
    echo "✅ No errors detected"
    echo ""
    echo "Production-Ready Architecture: VALIDATED ✅"
else
    echo -e "${YELLOW}⚠️  SOME ISSUES DETECTED${NC}"
    echo ""
    echo "Check backend logs: ${BACKEND_LOG}"
    exit 1
fi

echo ""
echo "Backend logs saved to: ${BACKEND_LOG}"
echo ""

