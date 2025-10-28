#!/bin/bash
# Test script for RAG Query System with Qwen 2.5 7B
# This script tests the three main query endpoints without requiring Python dependencies

BASE_URL="${1:-http://localhost:8000}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}      RAG Query System Test Suite - Qwen 2.5 7B Q5_K_M              ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"
echo -e "Base URL: $BASE_URL"
echo -e "Time: $(date '+%Y-%m-%d %H:%M:%S')\n"

# Test 1: Health Check
echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}             Test 1: Health Check                                    ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

echo -e "${BLUE}ℹ️  Testing /api/query/health...${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/query/health")

if echo "$HEALTH_RESPONSE" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo -e "  Status: $(echo "$HEALTH_RESPONSE" | jq -r '.status')"
    echo -e "  Provider: $(echo "$HEALTH_RESPONSE" | jq -r '.provider')"
    echo -e "  Model: $(echo "$HEALTH_RESPONSE" | jq -r '.model')"
    echo -e "  Test response: $(echo "$HEALTH_RESPONSE" | jq -r '.test_response' | head -c 50)..."
    TEST_1="PASSED"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo -e "  Response: $HEALTH_RESPONSE"
    TEST_1="FAILED"
fi

# Test 2: Non-Streaming Query
echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}             Test 2: Non-Streaming Query                              ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

TEST_QUESTION="What is the maximum depth for recreational diving?"
echo -e "${BLUE}ℹ️  Question: $TEST_QUESTION${NC}"
echo -e "${BLUE}ℹ️  Sending POST request to /api/query/...${NC}"

START_TIME=$(date +%s)
QUERY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/query/" \
    -H "Content-Type: application/json" \
    -d "{
        \"question\": \"$TEST_QUESTION\",
        \"temperature\": 0.7,
        \"max_tokens\": 200
    }")
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if echo "$QUERY_RESPONSE" | jq -e '.answer' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Non-streaming query successful${NC}"
    echo -e "  Duration: ${DURATION}s"
    echo -e "  Answer length: $(echo "$QUERY_RESPONSE" | jq -r '.answer' | wc -c) chars"
    echo -e "  Answer preview: $(echo "$QUERY_RESPONSE" | jq -r '.answer' | head -c 150 | tr '\n' ' ')..."
    echo -e "  Sources used: $(echo "$QUERY_RESPONSE" | jq -r '.num_sources')"
    
    NUM_SOURCES=$(echo "$QUERY_RESPONSE" | jq -r '.num_sources')
    if [ "$NUM_SOURCES" -gt 0 ]; then
        echo -e "${GREEN}✅ ✓ Successfully retrieved context from knowledge graph${NC}"
    else
        echo -e "${YELLOW}⚠️  ⚠ No context retrieved (knowledge graph may be empty)${NC}"
    fi
    TEST_2="PASSED"
else
    echo -e "${RED}❌ Non-streaming query failed${NC}"
    echo -e "  Response: $(echo "$QUERY_RESPONSE" | head -c 200)"
    TEST_2="FAILED"
fi

# Test 3: Streaming Query
echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}             Test 3: Streaming Query (SSE)                           ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

TEST_QUESTION2="Explain the buddy system in scuba diving"
echo -e "${BLUE}ℹ️  Question: $TEST_QUESTION2${NC}"
echo -e "${BLUE}ℹ️  Sending POST request to /api/query/stream...${NC}"
echo -e "${BLUE}ℹ️  Streaming response:${NC}\n"

START_TIME=$(date +%s.%N)
STREAM_OUTPUT=$(mktemp)
TOKEN_COUNT=0

# Stream the response and capture tokens
curl -s -N -X POST "$BASE_URL/api/query/stream" \
    -H "Content-Type: application/json" \
    -d "{
        \"question\": \"$TEST_QUESTION2\",
        \"temperature\": 0.7,
        \"max_tokens\": 150
    }" | while IFS= read -r line; do
    
    if [[ $line == data:* ]]; then
        # Extract the data part
        data="${line#data: }"
        
        # Check for completion or error
        if [[ "$data" == "[DONE]" ]]; then
            break
        elif [[ "$data" == \[ERROR* ]]; then
            echo -e "\n${RED}❌ Stream error: $data${NC}"
            exit 1
        else
            # Print the token
            echo -n "$data"
            echo "$data" >> "$STREAM_OUTPUT"
        fi
    fi
done

END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

# Count tokens (approximate - count chunks received)
TOKEN_COUNT=$(wc -c < "$STREAM_OUTPUT")
TOKENS_PER_SEC=$(echo "scale=1; $TOKEN_COUNT / $DURATION" | bc)

echo -e "\n"

if [ $TOKEN_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ Streaming query successful${NC}"
    echo -e "  Duration: ${DURATION}s"
    echo -e "  Chars streamed: $TOKEN_COUNT"
    echo -e "  Chars/second: ${TOKENS_PER_SEC}"
    echo -e "  Response length: $TOKEN_COUNT chars"
    
    # Check performance (approximate - using chars as proxy for tokens)
    # Note: Actual tokens/sec would be different, this is just a rough indicator
    if (( $(echo "$TOKENS_PER_SEC >= 100" | bc -l) )); then
        echo -e "${GREEN}✅ ✓ Good performance: ${TOKENS_PER_SEC} chars/s${NC}"
    else
        echo -e "${YELLOW}⚠️  ⚠ Performance could be better: ${TOKENS_PER_SEC} chars/s${NC}"
    fi
    TEST_3="PASSED"
else
    echo -e "${RED}❌ Streaming query failed${NC}"
    TEST_3="FAILED"
fi

rm -f "$STREAM_OUTPUT"

# Test 4: Error Handling
echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}             Test 4: Error Handling                                  ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

echo -e "${BLUE}ℹ️  Testing invalid temperature (> 1.0)...${NC}"
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/query/" \
    -H "Content-Type: application/json" \
    -d '{
        "question": "Test",
        "temperature": 2.0,
        "max_tokens": 100
    }')

if echo "$ERROR_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ✓ Correctly rejected invalid temperature${NC}"
    ERROR_TEST_1="PASSED"
else
    echo -e "${YELLOW}⚠️  ⚠ Unexpected response to invalid temperature${NC}"
    ERROR_TEST_1="FAILED"
fi

echo -e "${BLUE}ℹ️  Testing missing question field...${NC}"
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/query/" \
    -H "Content-Type: application/json" \
    -d '{
        "temperature": 0.7,
        "max_tokens": 100
    }')

if echo "$ERROR_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ✓ Correctly rejected missing question${NC}"
    ERROR_TEST_2="PASSED"
else
    echo -e "${YELLOW}⚠️  ⚠ Unexpected response to missing question${NC}"
    ERROR_TEST_2="FAILED"
fi

if [ "$ERROR_TEST_1" == "PASSED" ] && [ "$ERROR_TEST_2" == "PASSED" ]; then
    echo -e "${GREEN}✅ Error handling tests passed${NC}"
    TEST_4="PASSED"
else
    echo -e "${RED}❌ Some error handling tests failed${NC}"
    TEST_4="FAILED"
fi

# Summary
echo -e "\n${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}             Test Summary                                            ${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}\n"

TOTAL_TESTS=4
PASSED_TESTS=0

# Print results
if [ "$TEST_1" == "PASSED" ]; then
    echo -e "${GREEN}✅ PASSED${NC} - Health Check"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} - Health Check"
fi

if [ "$TEST_2" == "PASSED" ]; then
    echo -e "${GREEN}✅ PASSED${NC} - Non-Streaming Query"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} - Non-Streaming Query"
fi

if [ "$TEST_3" == "PASSED" ]; then
    echo -e "${GREEN}✅ PASSED${NC} - Streaming Query"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} - Streaming Query"
fi

if [ "$TEST_4" == "PASSED" ]; then
    echo -e "${GREEN}✅ PASSED${NC} - Error Handling"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} - Error Handling"
fi

echo -e "\n${BOLD}Total: $PASSED_TESTS/$TOTAL_TESTS tests passed${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 All tests passed! RAG Query System is working correctly.${NC}\n"
    exit 0
else
    echo -e "\n${RED}⚠️  $((TOTAL_TESTS - PASSED_TESTS)) test(s) failed. Please review the errors above.${NC}\n"
    exit 1
fi

