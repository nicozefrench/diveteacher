#!/bin/bash
# Ollama Performance Monitoring Script for Qwen 2.5 7B Q5_K_M
# This script monitors Docker resource usage, model status, and performance metrics

BASE_URL="${1:-http://localhost:8000}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}      Ollama Performance Monitor - Qwen 2.5 7B Q5_K_M               ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

# 1. Docker Container Status
echo -e "${BOLD}1. Docker Container Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLLAMA_STATUS=$(docker ps --filter "name=rag-ollama" --format "{{.Status}}")
if [ -n "$OLLAMA_STATUS" ]; then
    echo -e "${GREEN}✅ Ollama container is running${NC}"
    echo -e "   Status: $OLLAMA_STATUS"
else
    echo -e "${RED}❌ Ollama container is not running${NC}"
    exit 1
fi

# 2. Docker Resource Usage
echo -e "\n${BOLD}2. Docker Resource Usage${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Get Docker stats (one-shot)
STATS=$(docker stats rag-ollama --no-stream --format "{{.MemUsage}}\t{{.CPUPerc}}\t{{.NetIO}}\t{{.BlockIO}}")

if [ -n "$STATS" ]; then
    MEM_USAGE=$(echo "$STATS" | awk '{print $1}')
    CPU_PERC=$(echo "$STATS" | awk '{print $3}')
    NET_IO=$(echo "$STATS" | awk '{print $4, $5, $6}')
    BLOCK_IO=$(echo "$STATS" | awk '{print $7, $8, $9}')
    
    echo -e "   Memory: ${BOLD}$MEM_USAGE${NC}"
    echo -e "   CPU: ${BOLD}$CPU_PERC${NC}"
    echo -e "   Network I/O: $NET_IO"
    echo -e "   Block I/O: $BLOCK_IO"
    
    # Check memory usage against limits
    MEM_USED_GB=$(echo "$MEM_USAGE" | grep -oE '[0-9.]+' | head -1)
    MEM_TOTAL_GB=$(echo "$MEM_USAGE" | grep -oE '[0-9.]+' | tail -1)
    
    if (( $(echo "$MEM_USED_GB > 14" | bc -l) )); then
        echo -e "${RED}⚠️  High memory usage (> 14GB of 16GB allocated)${NC}"
    elif (( $(echo "$MEM_USED_GB > 10" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Moderate memory usage (> 10GB)${NC}"
    else
        echo -e "${GREEN}✅ Memory usage is healthy${NC}"
    fi
else
    echo -e "${RED}❌ Could not retrieve Docker stats${NC}"
fi

# 3. Ollama API Status
echo -e "\n${BOLD}3. Ollama API Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version | jq -r '.version')
if [ -n "$OLLAMA_VERSION" ] && [ "$OLLAMA_VERSION" != "null" ]; then
    echo -e "${GREEN}✅ Ollama API is responding${NC}"
    echo -e "   Version: $OLLAMA_VERSION"
else
    echo -e "${RED}❌ Ollama API is not responding${NC}"
fi

# 4. Model Information
echo -e "\n${BOLD}4. Model Information${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[]')
if [ -n "$MODELS" ]; then
    echo -e "${GREEN}✅ Models loaded:${NC}"
    curl -s http://localhost:11434/api/tags | jq -r '.models[] | "   - \(.name) (Size: \(.size / 1024 / 1024 / 1024 | floor)GB)"'
    
    # Check if Qwen model is loaded
    QWEN_LOADED=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' | grep -i "qwen")
    if [ -n "$QWEN_LOADED" ]; then
        echo -e "${GREEN}✅ Qwen model is loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Qwen model not found in loaded models${NC}"
    fi
else
    echo -e "${RED}❌ No models loaded${NC}"
fi

# 5. Backend API Health
echo -e "\n${BOLD}5. Backend API Health${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

API_HEALTH=$(curl -s "$BASE_URL/api/query/health")
if echo "$API_HEALTH" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is healthy${NC}"
    echo -e "   Provider: $(echo "$API_HEALTH" | jq -r '.provider')"
    echo -e "   Model: $(echo "$API_HEALTH" | jq -r '.model')"
else
    echo -e "${RED}❌ Backend API health check failed${NC}"
fi

# 6. Performance Benchmark
echo -e "\n${BOLD}6. Performance Benchmark (Quick Test)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}ℹ️  Running a quick performance test (50 tokens)...${NC}"

START_TIME=$(date +%s.%N)
RESPONSE=$(docker exec rag-ollama ollama run qwen2.5:7b-instruct-q5_K_M "Count from 1 to 10" 2>/dev/null)
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

if [ -n "$RESPONSE" ]; then
    TOKEN_COUNT=$(echo "$RESPONSE" | wc -w)
    CHAR_COUNT=$(echo "$RESPONSE" | wc -c)
    TOKENS_PER_SEC=$(echo "scale=1; $TOKEN_COUNT / $DURATION" | bc)
    
    echo -e "${GREEN}✅ Performance test completed${NC}"
    echo -e "   Duration: ${DURATION}s"
    echo -e "   Words generated: $TOKEN_COUNT"
    echo -e "   Chars generated: $CHAR_COUNT"
    echo -e "   Est. tokens/second: ${BOLD}${TOKENS_PER_SEC} tok/s${NC}"
    
    # Compare against targets from deployment guide
    if (( $(echo "$TOKENS_PER_SEC >= 30" | bc -l) )); then
        echo -e "${GREEN}✅ Performance meets target (>= 30 tok/s)${NC}"
    elif (( $(echo "$TOKENS_PER_SEC >= 20" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Performance below target but acceptable (20-30 tok/s)${NC}"
        echo -e "${YELLOW}   Note: Q5_K_M on Mac M1 Max may be slower than GPU deployment${NC}"
    else
        echo -e "${RED}❌ Performance significantly below target (< 20 tok/s)${NC}"
        echo -e "${RED}   Recommendation: Check Docker memory allocation and CPU usage${NC}"
    fi
else
    echo -e "${RED}❌ Performance test failed - model did not respond${NC}"
fi

# 7. Docker Desktop Memory Check
echo -e "\n${BOLD}7. Docker Desktop Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Docker memory limit
DOCKER_MEM_LIMIT=$(docker info 2>/dev/null | grep -i "Total Memory" | awk '{print $3, $4}')
if [ -n "$DOCKER_MEM_LIMIT" ]; then
    echo -e "   Docker Memory Limit: ${BOLD}$DOCKER_MEM_LIMIT${NC}"
    
    # Extract numeric value
    MEM_VAL=$(echo "$DOCKER_MEM_LIMIT" | grep -oE '[0-9.]+' | head -1)
    if (( $(echo "$MEM_VAL >= 16" | bc -l) )); then
        echo -e "${GREEN}✅ Docker has sufficient memory allocated (>= 16GB)${NC}"
    elif (( $(echo "$MEM_VAL >= 12" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Docker memory is sufficient but could be higher (12-16GB)${NC}"
    else
        echo -e "${RED}❌ Docker memory may be insufficient (< 12GB)${NC}"
        echo -e "${RED}   Recommendation: Increase Docker Desktop memory to 16GB${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not determine Docker memory limit${NC}"
fi

# 8. Recommendations
echo -e "\n${BOLD}8. Recommendations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${BOLD}Model Configuration:${NC}"
echo -e "   Current: Qwen 2.5 7B Q5_K_M (6.9GB RAM requirement)"
echo -e "   Memory: ~7-8GB during inference"
echo -e "   Performance: Good balance of quality and speed for local dev"

echo -e "\n${BOLD}For Production (DigitalOcean GPU):${NC}"
echo -e "   Recommended: Qwen 2.5 7B Q8_0 (9.3GB RAM requirement)"
echo -e "   GPU: NVIDIA RTX 4000 Ada (20GB VRAM)"
echo -e "   Expected: 40-60 tok/s (see @251028-rag-gpu-deployment-guide.md)"

echo -e "\n${BOLD}Next Steps:${NC}"
echo -e "   1. Upload documents to populate knowledge graph"
echo -e "   2. Test RAG queries with actual context"
echo -e "   3. Monitor performance with real workloads"
echo -e "   4. Plan GPU deployment when ready for production"

echo -e "\n${BOLD}${GREEN}✅ Monitoring complete!${NC}\n"

