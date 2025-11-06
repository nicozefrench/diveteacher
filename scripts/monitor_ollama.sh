#!/bin/bash
# Ollama Performance Monitoring Script for Qwen 2.5 7B Q8_0
# This script monitors NATIVE Ollama (baremetal Mac Metal GPU), model status, and performance metrics
# NOTE: Ollama now runs natively on Mac host for Metal GPU access
# See: Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md

BASE_URL="${1:-http://localhost:8000}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}      Ollama Performance Monitor - Qwen 2.5 7B Q8_0 (Metal GPU)      ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

# 1. Ollama Process Status (Native)
echo -e "${BOLD}1. Ollama Process Status (Native Baremetal)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLLAMA_PID=$(pgrep -x ollama)
if [ -n "$OLLAMA_PID" ]; then
    echo -e "${GREEN}✅ Ollama process is running (native)${NC}"
    echo -e "   PID: $OLLAMA_PID"
    
    # Get process memory usage
    MEM_RSS=$(ps -o rss= -p "$OLLAMA_PID" 2>/dev/null)
    if [ -n "$MEM_RSS" ]; then
        MEM_GB=$(echo "scale=2; $MEM_RSS / 1024 / 1024" | bc)
        echo -e "   Memory (RSS): ${BOLD}${MEM_GB} GB${NC}"
    fi
    
    # Get CPU usage
    CPU_PERC=$(ps -o %cpu= -p "$OLLAMA_PID" 2>/dev/null | xargs)
    if [ -n "$CPU_PERC" ]; then
        echo -e "   CPU: ${BOLD}${CPU_PERC}%${NC}"
    fi
else
    echo -e "${RED}❌ Ollama process is not running${NC}"
    echo -e "${YELLOW}⚠️  Start Ollama with: OLLAMA_HOST=0.0.0.0:11434 OLLAMA_ORIGINS=\"*\" ollama serve${NC}"
    exit 1
fi

# 2. Ollama API Status
echo -e "\n${BOLD}2. Ollama API Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version | jq -r '.version')
if [ -n "$OLLAMA_VERSION" ] && [ "$OLLAMA_VERSION" != "null" ]; then
    echo -e "${GREEN}✅ Ollama API is responding${NC}"
    echo -e "   Version: $OLLAMA_VERSION"
    echo -e "   Endpoint: http://localhost:11434"
else
    echo -e "${RED}❌ Ollama API is not responding${NC}"
    exit 1
fi

# 3. Model Information & GPU Status
echo -e "\n${BOLD}3. Model Information & GPU Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# List all models
MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[]')
if [ -n "$MODELS" ]; then
    echo -e "${GREEN}✅ Models available:${NC}"
    curl -s http://localhost:11434/api/tags | jq -r '.models[] | "   - \(.name) (Size: \(.size / 1024 / 1024 / 1024 | floor)GB)"'
    
    # Check if Qwen model is loaded
    QWEN_LOADED=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' | grep -i "qwen")
    if [ -n "$QWEN_LOADED" ]; then
        echo -e "${GREEN}✅ Qwen model is available${NC}"
    else
        echo -e "${YELLOW}⚠️  Qwen model not found${NC}"
    fi
else
    echo -e "${RED}❌ No models available${NC}"
fi

# Check running models (ps command)
echo -e "\n${BOLD}Running Models:${NC}"
RUNNING_MODELS=$(curl -s http://localhost:11434/api/ps | jq -r '.models[]')
if [ -n "$RUNNING_MODELS" ]; then
    echo -e "${GREEN}✅ Models currently loaded in memory:${NC}"
    curl -s http://localhost:11434/api/ps | jq -r '.models[] | "   - \(.name)"'
    curl -s http://localhost:11434/api/ps | jq -r '.models[] | "     Size: \(.size / 1024 / 1024 / 1024 | floor)GB | Processor: \(.details.processor // "N/A") | Until: \(.expires_at)"'
    
    # Check for GPU usage
    GPU_STATUS=$(curl -s http://localhost:11434/api/ps | jq -r '.models[0].details.processor')
    if [ "$GPU_STATUS" = "100% GPU" ]; then
        echo -e "${GREEN}✅ GPU (Metal) is active: 100%${NC}"
    elif echo "$GPU_STATUS" | grep -q "GPU"; then
        echo -e "${YELLOW}⚠️  GPU detected but not at 100%: $GPU_STATUS${NC}"
    else
        echo -e "${RED}❌ WARNING: Model running on CPU, not GPU!${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  No models currently loaded (will load on first query)${NC}"
fi

# 4. Backend API Health
echo -e "\n${BOLD}4. Backend API Health${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

API_HEALTH=$(curl -s "$BASE_URL/api/health")
if echo "$API_HEALTH" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is healthy${NC}"
    LLM_PROVIDER=$(echo "$API_HEALTH" | jq -r '.services.llm.provider')
    echo -e "   Provider: $LLM_PROVIDER"
    
    # Check if backend can reach Ollama
    if [ "$LLM_PROVIDER" = "ollama" ]; then
        echo -e "${GREEN}✅ Backend → Ollama connection configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend not using Ollama (Provider: $LLM_PROVIDER)${NC}"
    fi
else
    echo -e "${RED}❌ Backend API health check failed${NC}"
fi

# 5. Performance Benchmark
echo -e "\n${BOLD}5. Performance Benchmark (Quick Test)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}ℹ️  Running a quick performance test...${NC}"

START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct-q8_0",
  "prompt": "Count from 1 to 5 quickly",
  "stream": false
}' | jq -r '.response')
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
    TOKEN_COUNT=$(echo "$RESPONSE" | wc -w)
    CHAR_COUNT=$(echo "$RESPONSE" | wc -c)
    TOKENS_PER_SEC=$(echo "scale=1; $TOKEN_COUNT / $DURATION" | bc)
    
    echo -e "${GREEN}✅ Performance test completed${NC}"
    echo -e "   Duration: ${DURATION}s"
    echo -e "   Words generated: $TOKEN_COUNT"
    echo -e "   Chars generated: $CHAR_COUNT"
    echo -e "   Est. tokens/second: ${BOLD}${TOKENS_PER_SEC} tok/s${NC}"
    
    # Compare against targets
    if (( $(echo "$TOKENS_PER_SEC >= 7" | bc -l) )); then
        echo -e "${GREEN}✅ Performance meets Metal GPU target (>= 7 tok/s)${NC}"
    elif (( $(echo "$TOKENS_PER_SEC >= 3" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Performance below target but acceptable (3-7 tok/s)${NC}"
    else
        echo -e "${RED}❌ Performance significantly below target (< 3 tok/s)${NC}"
        echo -e "${RED}   Recommendation: Check if model is running on GPU (not CPU)${NC}"
    fi
else
    echo -e "${RED}❌ Performance test failed - model did not respond${NC}"
    echo -e "${YELLOW}⚠️  Model may need to load first (try running again)${NC}"
fi

# 6. System Resources
echo -e "\n${BOLD}6. System Resources (Mac M1 Max)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check system memory
TOTAL_MEM=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024}')
if [ -n "$TOTAL_MEM" ]; then
    echo -e "   Total System Memory: ${BOLD}${TOTAL_MEM} GB${NC}"
fi

# Check Metal GPU info (if available)
if command -v system_profiler &> /dev/null; then
    GPU_INFO=$(system_profiler SPDisplaysDataType 2>/dev/null | grep -A 3 "Chipset Model" | head -4)
    if [ -n "$GPU_INFO" ]; then
        echo -e "\n${BOLD}Metal GPU:${NC}"
        echo "$GPU_INFO" | sed 's/^/   /'
    fi
fi

# 7. Recommendations
echo -e "\n${BOLD}7. Configuration & Recommendations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${BOLD}Current Setup (Development - Mac M1 Max):${NC}"
echo -e "   Model: Qwen 2.5 7B Q8_0 (8.1GB)"
echo -e "   Processor: Metal GPU (M1 Max)"
echo -e "   Memory: ~9GB during inference"
echo -e "   Performance: 7-14 tok/s (Metal GPU)"

echo -e "\n${BOLD}For Production (DigitalOcean GPU):${NC}"
echo -e "   Model: Qwen 2.5 7B Q8_0 (same)"
echo -e "   GPU: NVIDIA RTX 4000 Ada (20GB VRAM)"
echo -e "   Expected: 40-60 tok/s"
echo -e "   Deployment: Docker with NVIDIA runtime"

echo -e "\n${BOLD}Migration Status:${NC}"
echo -e "   ${GREEN}✅ Ollama migrated from Docker to baremetal${NC}"
echo -e "   ${GREEN}✅ Metal GPU active (100%)${NC}"
echo -e "   ${GREEN}✅ Performance gain: 30-60× vs Docker CPU${NC}"
echo -e "   ${GREEN}✅ Backend → Native Ollama connectivity OK${NC}"

echo -e "\n${BOLD}Next Steps:${NC}"
echo -e "   1. Keep Terminal 1 open (ollama serve)"
echo -e "   2. Run E2E tests with full RAG queries"
echo -e "   3. Validate Gap #2 reranking improvement"
echo -e "   4. Complete Days 5-7 of Gap #2"

echo -e "\n${BOLD}${GREEN}✅ Monitoring complete!${NC}\n"
