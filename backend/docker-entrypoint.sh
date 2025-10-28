#!/bin/bash
# Docker entrypoint script with Docling warm-up

set -e

echo "=================================================="
echo "🚀 DiveTeacher Backend Starting..."
echo "=================================================="
echo ""

# Check if warm-up should be performed
if [ "${SKIP_WARMUP}" != "true" ]; then
    echo "🔥 Step 1: Warming up Docling models..."
    echo "--------------------------------------------------"
    
    # Run warm-up script AS A MODULE (ensures correct PYTHONPATH)
    # Using -m flag adds current directory to sys.path automatically
    python3 -m app.warmup || {
        echo "⚠️  Warm-up failed or skipped"
        echo "⚠️  Models will download on first document upload"
    }
    
    echo ""
    echo "✅ Warm-up phase complete"
    echo ""
else
    echo "⏭️  Skipping warm-up (SKIP_WARMUP=true)"
    echo ""
fi

echo "🚀 Step 2: Starting FastAPI application..."
echo "--------------------------------------------------"
echo ""

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

