#!/bin/bash
# Monitor Graphiti Ingestion in Real-Time
# 
# UPDATED for ARIA v2.0.0 Architecture:
# - ARIA RecursiveCharacterTextSplitter (3000 tokens/chunk)
# - SafeIngestionQueue (token-aware rate limiting)
# - DocumentQueue (sequential FIFO processing)
#
# Usage: ./monitor_ingestion.sh [upload_id]

UPLOAD_ID=$1
CONTAINER="rag-backend"

echo "🔍 Starting Real-Time Ingestion Monitor (ARIA v2.0.0)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -n "$UPLOAD_ID" ]; then
    echo "📌 Filtering for upload_id: $UPLOAD_ID"
    echo ""
else
    echo "💡 Tip: Provide upload_id for focused monitoring"
    echo "   Usage: ./monitor_ingestion.sh <upload_id>"
    echo ""
fi

echo "🏗️  Architecture:"
echo "   • ARIA Chunking: 3000 tokens/chunk, 200 overlap"
echo "   • SafeIngestionQueue: Token-aware rate limiting"
echo "   • DocumentQueue: Sequential FIFO processing"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "📊 Monitoring Graphiti ingestion logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Follow logs with filters (ARIA v2.0.0 keywords)
if [ -n "$UPLOAD_ID" ]; then
    # Filter by specific upload_id
    docker logs -f "$CONTAINER" 2>&1 | grep --line-buffered -E "\[$UPLOAD_ID\]|diveteacher\.graphiti|diveteacher\.processor|diveteacher\.aria_chunker|diveteacher\.safe_queue|diveteacher\.queue|Starting Graphiti|Initializing Graphiti|RecursiveCharacterTextSplitter|ARIA|SafeIngestionQueue|DocumentQueue|Claude Haiku|Episode|Entity|Token|chunks \(ARIA|Sequential|✅|❌|📊|🔧|📥|📝|🔪|🔒|Step [0-9]/[0-9]|Progress:" | while read line; do
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
    # Monitor all Graphiti + ARIA activity
    docker logs -f "$CONTAINER" 2>&1 | grep --line-buffered -E "diveteacher\.graphiti|diveteacher\.processor|diveteacher\.aria_chunker|diveteacher\.safe_queue|diveteacher\.queue|Starting Graphiti|Initializing Graphiti|RecursiveCharacterTextSplitter|ARIA|SafeIngestionQueue|DocumentQueue|Claude Haiku|Episode|Entity|Token|chunks \(ARIA|Sequential|✅|❌|📊|🔧|📥|📝|🔪|🔒|Step [0-9]/[0-9]|Chunk [0-9]|Ingestion" | while read line; do
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

