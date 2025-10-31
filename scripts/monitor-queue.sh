#!/bin/bash
#
# DocumentQueue Real-Time Monitor
# 
# Monitors the document processing queue status in real-time.
# Shows: queue size, current processing, completed/failed counts, queued documents
#
# Usage:
#   ./scripts/monitor-queue.sh [interval_seconds]
#
# Examples:
#   ./scripts/monitor-queue.sh          # Monitor every 2 seconds
#   ./scripts/monitor-queue.sh 5        # Monitor every 5 seconds
#   ./scripts/monitor-queue.sh 1        # Monitor every 1 second (fast updates)
#

# Configuration
API_URL="http://localhost:8000/api"
INTERVAL="${1:-2}"  # Default: 2 seconds

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Clear screen function
clear_screen() {
    printf "\033c"
}

# Display header
display_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  📥 DOCUMENT QUEUE MONITOR (ARIA v2.0.0)                            ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Refresh: ${INTERVAL}s | Press Ctrl+C to stop"
    echo ""
}

# Main monitoring loop
main() {
    while true; do
        clear_screen
        display_header
        
        # Fetch queue status
        QUEUE_DATA=$(curl -s "${API_URL}/queue/status" 2>/dev/null)
        
        if [ -z "$QUEUE_DATA" ]; then
            echo -e "${RED}❌ Cannot connect to backend${NC}"
            echo "   Make sure backend is running: docker ps | grep backend"
            sleep $INTERVAL
            continue
        fi
        
        # Parse queue status
        QUEUE_SIZE=$(echo "$QUEUE_DATA" | jq -r '.queue_size // 0')
        PROCESSING=$(echo "$QUEUE_DATA" | jq -r '.processing // false')
        COMPLETED=$(echo "$QUEUE_DATA" | jq -r '.completed_count // 0')
        FAILED=$(echo "$QUEUE_DATA" | jq -r '.failed_count // 0')
        TOTAL=$(echo "$QUEUE_DATA" | jq -r '.stats.total_enqueued // 0')
        SUCCESS_RATE=$(echo "$QUEUE_DATA" | jq -r '.stats.success_rate // 0')
        
        # Current document
        CURRENT_DOC=$(echo "$QUEUE_DATA" | jq -r '.current_document')
        
        # ════════════════════════════════════════════════════════
        # Display Queue Summary
        # ════════════════════════════════════════════════════════
        
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "  📊 QUEUE STATUS"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        
        # Processing status
        if [ "$PROCESSING" = "true" ]; then
            echo -e "  Status: ${GREEN}●${NC} PROCESSING"
        else
            echo -e "  Status: ${BLUE}○${NC} IDLE"
        fi
        
        # Queue size
        if [ "$QUEUE_SIZE" -gt 0 ]; then
            echo -e "  Queue: ${YELLOW}${QUEUE_SIZE} documents waiting${NC}"
        else
            echo -e "  Queue: ${GREEN}Empty${NC}"
        fi
        
        # Statistics
        echo ""
        echo "  📈 Statistics:"
        echo "     • Total Enqueued: $TOTAL"
        echo "     • Completed: ${GREEN}$COMPLETED${NC}"
        echo "     • Failed: ${RED}$FAILED${NC}"
        echo "     • Success Rate: ${SUCCESS_RATE}%"
        echo ""
        
        # ════════════════════════════════════════════════════════
        # Current Document Being Processed
        # ════════════════════════════════════════════════════════
        
        if [ "$CURRENT_DOC" != "null" ] && [ -n "$CURRENT_DOC" ]; then
            echo "═══════════════════════════════════════════════════════════════════════"
            echo "  📄 CURRENT DOCUMENT"
            echo "═══════════════════════════════════════════════════════════════════════"
            echo ""
            
            CURRENT_FILENAME=$(echo "$CURRENT_DOC" | jq -r '.filename // "unknown"')
            CURRENT_UPLOAD_ID=$(echo "$CURRENT_DOC" | jq -r '.upload_id // "unknown"')
            CURRENT_STATUS=$(echo "$CURRENT_DOC" | jq -r '.status // "unknown"')
            CURRENT_STARTED=$(echo "$CURRENT_DOC" | jq -r '.started_at // "unknown"')
            
            echo "  📌 Filename: ${CYAN}${CURRENT_FILENAME}${NC}"
            echo "  🆔 Upload ID: ${CURRENT_UPLOAD_ID}"
            echo "  📊 Status: ${CURRENT_STATUS}"
            echo "  ⏱️  Started: ${CURRENT_STARTED}"
            
            # Get detailed status from upload endpoint
            UPLOAD_STATUS=$(curl -s "${API_URL}/upload/${CURRENT_UPLOAD_ID}/status" 2>/dev/null)
            if [ -n "$UPLOAD_STATUS" ]; then
                STAGE=$(echo "$UPLOAD_STATUS" | jq -r '.stage // "unknown"')
                PROGRESS=$(echo "$UPLOAD_STATUS" | jq -r '.progress // 0')
                NUM_CHUNKS=$(echo "$UPLOAD_STATUS" | jq -r '.metrics.num_chunks // "?"')
                
                echo ""
                echo "  🔄 Current Stage: ${STAGE}"
                echo "  📊 Progress: ${PROGRESS}%"
                echo "  🔪 Chunks: ${NUM_CHUNKS} (ARIA pattern)"
                
                # Ingestion progress if available
                INGESTION=$(echo "$UPLOAD_STATUS" | jq -r '.ingestion_progress')
                if [ "$INGESTION" != "null" ] && [ -n "$INGESTION" ]; then
                    CHUNKS_DONE=$(echo "$INGESTION" | jq -r '.chunks_completed // 0')
                    CHUNKS_TOTAL=$(echo "$INGESTION" | jq -r '.chunks_total // 0')
                    INGESTION_PCT=$(echo "$INGESTION" | jq -r '.progress_pct // 0')
                    
                    echo "  📈 Ingestion: ${CHUNKS_DONE}/${CHUNKS_TOTAL} chunks (${INGESTION_PCT}%)"
                fi
            fi
            
            echo ""
        fi
        
        # ════════════════════════════════════════════════════════
        # Queued Documents (Waiting)
        # ════════════════════════════════════════════════════════
        
        if [ "$QUEUE_SIZE" -gt 0 ]; then
            echo "═══════════════════════════════════════════════════════════════════════"
            echo "  ⏳ QUEUED DOCUMENTS"
            echo "═══════════════════════════════════════════════════════════════════════"
            echo ""
            
            # Parse queued documents
            QUEUED_DOCS=$(echo "$QUEUE_DATA" | jq -r '.queued_documents')
            
            echo "$QUEUED_DOCS" | jq -r '.[] | "  [\(.queue_position)] \(.filename) (Upload ID: \(.upload_id | .[0:8])...)"'
            
            echo ""
        fi
        
        # ════════════════════════════════════════════════════════
        # Footer with Info
        # ════════════════════════════════════════════════════════
        
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        echo -e "${BLUE}ℹ️  Architecture:${NC} Sequential FIFO + ARIA Chunking (3000 tokens/chunk)"
        echo -e "${BLUE}ℹ️  Inter-document delay:${NC} 60 seconds (rate limit safety)"
        echo -e "${BLUE}ℹ️  Queue endpoint:${NC} ${API_URL}/queue/status"
        echo ""
        
        # Wait before next refresh
        sleep $INTERVAL
    done
}

# Cleanup on exit
cleanup() {
    echo ""
    echo "👋 Monitoring stopped"
    exit 0
}

trap cleanup INT TERM

# Run monitor
main

