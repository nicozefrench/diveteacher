#!/bin/bash
#
# Monitor upload progress (passive - doesn't initiate upload)
# Usage: ./scripts/monitor-upload.sh <upload_id>
#

UPLOAD_ID="$1"
API_URL="http://localhost:8000/api"
POLL_INTERVAL=5

if [ -z "$UPLOAD_ID" ]; then
    echo "Usage: $0 <upload_id>"
    exit 1
fi

echo ""
echo "📊 Monitoring Upload: ${UPLOAD_ID}"
echo "   Polling every ${POLL_INTERVAL}s (Ctrl+C to stop)"
echo ""

LAST_PROGRESS=0
START_TIME=$(date +%s)

while true; do
    STATUS=$(curl -s "${API_URL}/upload/${UPLOAD_ID}/status")
    
    CURRENT_STATUS=$(echo "$STATUS" | jq -r '.status')
    STAGE=$(echo "$STATUS" | jq -r '.stage')
    SUB_STAGE=$(echo "$STATUS" | jq -r '.sub_stage')
    PROGRESS=$(echo "$STATUS" | jq -r '.progress')
    
    ELAPSED=$(($(date +%s) - START_TIME))
    
    if [ "$PROGRESS" != "$LAST_PROGRESS" ]; then
        echo "[$(date +%H:%M:%S)] ${ELAPSED}s | Status: ${CURRENT_STATUS} | Stage: ${STAGE} | Progress: ${PROGRESS}%"
        LAST_PROGRESS="$PROGRESS"
    fi
    
    if [ "$CURRENT_STATUS" = "completed" ]; then
        echo ""
        echo "✅ Processing completed!"
        
        # Show final metrics
        ENTITIES=$(echo "$STATUS" | jq -r '.metrics.entities // 0')
        RELATIONS=$(echo "$STATUS" | jq -r '.metrics.relations // 0')
        CHUNKS=$(echo "$STATUS" | jq -r '.metrics.num_chunks // 0')
        TOTAL_TIME=$(echo "$STATUS" | jq -r '.durations.total // 0')
        
        echo ""
        echo "📊 Final Metrics:"
        echo "   Entities: ${ENTITIES}"
        echo "   Relations: ${RELATIONS}"
        echo "   Chunks: ${CHUNKS}"
        echo "   Total Time: ${TOTAL_TIME}s"
        
        if [ "$CHUNKS" -gt 0 ]; then
            AVG=$(echo "scale=2; $TOTAL_TIME / $CHUNKS" | bc)
            echo "   Avg per chunk: ${AVG}s"
        fi
        
        break
    fi
    
    if [ "$CURRENT_STATUS" = "failed" ]; then
        echo ""
        echo "❌ Processing failed!"
        ERROR=$(echo "$STATUS" | jq -r '.error')
        echo "   Error: ${ERROR}"
        exit 1
    fi
    
    sleep $POLL_INTERVAL
done

echo ""

