#!/bin/bash
# Monitor Graphiti Ingestion in Real-Time
# Usage: ./monitor_ingestion.sh [upload_id]

UPLOAD_ID=$1
CONTAINER="rag-backend"

echo "🔍 Starting Real-Time Ingestion Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -n "$UPLOAD_ID" ]; then
    echo "📌 Filtering for upload_id: $UPLOAD_ID"
    echo ""
fi

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "📊 Monitoring Graphiti ingestion logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Follow logs with filters
if [ -n "$UPLOAD_ID" ]; then
    # Filter by specific upload_id
    docker logs -f "$CONTAINER" 2>&1 | grep --line-buffered -E "\[$UPLOAD_ID\]|diveteacher\.graphiti|diveteacher\.processor|Starting Graphiti|Initializing Graphiti|Claude Haiku|Episode|Entity|✅|❌|📊|🔧|📥|📝|Step [0-9]/[0-9]|Progress:" | while read line; do
        if echo "$line" | grep -q "✅"; then
            echo -e "${GREEN}${line}${NC}"
        elif echo "$line" | grep -q "❌"; then
            echo -e "${RED}${line}${NC}"
        elif echo "$line" | grep -q "Step"; then
            echo -e "${BLUE}${line}${NC}"
        elif echo "$line" | grep -q "Graphiti\|Claude"; then
            echo -e "${YELLOW}${line}${NC}"
        else
            echo "$line"
        fi
    done
else
    # Monitor all Graphiti activity
    docker logs -f "$CONTAINER" 2>&1 | grep --line-buffered -E "diveteacher\.graphiti|diveteacher\.processor|Starting Graphiti|Initializing Graphiti|Claude Haiku|Episode|Entity|✅|❌|📊|🔧|📥|📝|Step [0-9]/[0-9]|Chunk [0-9]|Ingestion" | while read line; do
        if echo "$line" | grep -q "✅"; then
            echo -e "${GREEN}${line}${NC}"
        elif echo "$line" | grep -q "❌"; then
            echo -e "${RED}${line}${NC}"
        elif echo "$line" | grep -q "Step"; then
            echo -e "${BLUE}${line}${NC}"
        elif echo "$line" | grep -q "Graphiti\|Claude"; then
            echo -e "${YELLOW}${line}${NC}"
        else
            echo "$line"
        fi
    done
fi

