# 🔌 DiveTeacher API Reference

> **Project:** RAG Knowledge Graph for Scuba Diving Education  
> **Version:** Phase 1.2 COMPLETE (RAG + Cross-Encoder Reranking)  
> **Last Updated:** November 5, 2025, 11:30 CET  
> **Base URL:** `http://localhost:8000` (local), `https://api.diveteacher.io` (production)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Upload Endpoints](#upload-endpoints)
- [RAG Query Endpoints](#rag-query-endpoints)
- [Status & Monitoring](#status--monitoring)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

DiveTeacher API provides RESTful endpoints for:
1. **Document Upload** - Upload FFESSM/SSI PDFs/PPTs for processing
2. **RAG Queries** - Query the knowledge graph with streaming/non-streaming responses
3. **Status Tracking** - Monitor document processing progress
4. **Health Checks** - Verify system availability

### Base URL

```
Local Development: http://localhost:8000
Production: https://api.diveteacher.io
```

### API Versioning

All endpoints are prefixed with `/api`:
```
http://localhost:8000/api/upload
http://localhost:8000/api/query
http://localhost:8000/api/health
```

---

## Authentication

### Current Status (Phase 1.0)
**No authentication required** - Open API for development.

### Future (Phase 1.1+)
Authentication will use **Supabase Auth** with JWT tokens:

```http
Authorization: Bearer <supabase_jwt_token>
```

**Roles:**
- `admin` - Full access (upload, query, manage)
- `instructor` - Query + limited upload
- `student` - Query only (rate-limited)

---

## Upload Endpoints

### POST `/api/upload`

Upload a document (PDF/PPT) for processing into the knowledge graph.

**Authentication:** None (Phase 1.0), `admin` or `instructor` (Phase 1.1+)

**Request:**

```http
POST /api/upload HTTP/1.1
Content-Type: multipart/form-data

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="nitrox.pdf"
Content-Type: application/pdf

<binary data>
------WebKitFormBoundary--
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file` | File | Yes | PDF or PPT file (max 50MB) |

**Allowed File Types:**
- `application/pdf` (.pdf)
- `application/vnd.ms-powerpoint` (.ppt)
- `application/vnd.openxmlformats-officedocument.presentationml.presentation` (.pptx)

**Response (Success):**

```json
{
  "upload_id": "uuid-v4-string",
  "filename": "nitrox.pdf",
  "status": "processing",
  "message": "Document upload successful, processing started"
}
```

**Response Codes:**
- `200 OK` - Upload accepted, processing started
- `400 Bad Request` - Invalid file type or size
- `413 Payload Too Large` - File exceeds 50MB
- `500 Internal Server Error` - Upload failed

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/nitrox.pdf"
```

**Processing Pipeline:**

1. **Validation** - File type, size, corruption check
2. **Docling Conversion** - PDF → Markdown + OCR + TableFormer
3. **Chunking** - HierarchicalChunker semantic segmentation
4. **Graphiti Ingestion** - Entity extraction + Neo4j storage

**Processing Time:** 2-10 minutes (depends on document size)

---

### GET `/api/upload/{upload_id}/status`

Get processing status for an uploaded document.

**Authentication:** None (Phase 1.0)

**Request:**

```http
GET /api/upload/550e8400-e29b-41d4-a716-446655440000/status HTTP/1.1
```

**Response (Processing):**

```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "nitrox.pdf",
  "status": "processing",
  "stage": "chunking",
  "progress": 50,
  "message": "Chunking document (Step 2/4)",
  "started_at": "2025-10-28T14:30:00Z",
  "completed_at": null,
  "error": null
}
```

**Response (Complete):**

```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "nitrox.pdf",
  "status": "completed",
  "stage": "complete",
  "progress": 100,
  "message": "Processing complete",
  "started_at": "2025-10-28T14:30:00Z",
  "completed_at": "2025-10-28T14:35:42Z",
  "chunks_processed": 72,
  "entities_extracted": 45,
  "relations_created": 123
}
```

**Response (Error):**

```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "nitrox.pdf",
  "status": "failed",
  "stage": "docling",
  "progress": 25,
  "message": "Processing failed",
  "error": "Docling conversion timeout after 300 seconds",
  "started_at": "2025-10-28T14:30:00Z",
  "completed_at": "2025-10-28T14:35:00Z"
}
```

**Status Values:**
- `processing` - Document is being processed
- `completed` - Processing successful
- `failed` - Processing encountered an error

**Stage Values:**
- `validation` - File validation (Step 1/4)
- `docling` - PDF conversion (Step 1/4)
- `chunking` - Semantic chunking (Step 2/4)
- `ingestion` - Graphiti + Neo4j (Step 3/4)
- `complete` - All steps done

**cURL Example:**

```bash
curl http://localhost:8000/api/upload/550e8400-e29b-41d4-a716-446655440000/status | jq
```

---

## RAG Query Endpoints

### POST `/api/query/` (Non-Streaming)

Query the knowledge graph and get a complete response.

**Authentication:** None (Phase 1.0), `admin`, `instructor`, or `student` (Phase 1.1+)

**Request:**

```http
POST /api/query/ HTTP/1.1
Content-Type: application/json

{
  "question": "What is the maximum depth for recreational diving?",
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": false,
  "group_ids": null,
  "use_reranking": true
}
```

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | Yes | - | User's question (1-1000 chars) |
| `temperature` | float | No | 0.7 | LLM creativity (0.0-1.0) |
| `max_tokens` | int | No | 2000 | Max response length (100-4000) |
| `stream` | bool | No | true | Enable streaming (not used here) |
| `group_ids` | string[] | No | null | Filter by groups (multi-tenant) |
| `use_reranking` | bool | No | true | Enable cross-encoder reranking (+16.67% precision) |

**Response:**

```json
{
  "question": "What is the maximum depth for recreational diving?",
  "answer": "According to FFESSM standards, the maximum depth for recreational diving varies by certification level:\n\n- Level 1 (N1): 20 meters\n- Level 2 (N2): 40 meters\n- Level 3 (N3): 60 meters\n\nThese limits ensure diver safety while allowing progressive depth exposure as skills advance.",
  "num_sources": 5,
  "reranked": true,
  "context": {
    "facts_used": [
      {
        "content": "FFESSM Level 1 certification authorizes diving to 20m depth...",
        "source": "FFESSM-MFT-N1.pdf",
        "relevance": 0.95
      },
      {
        "content": "Level 2 divers can explore depths up to 40m...",
        "source": "FFESSM-MFT-N2.pdf",
        "relevance": 0.92
      }
    ],
    "retrieval_time_ms": 234,
    "generation_time_ms": 3421,
    "total_time_ms": 3655
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | Echo of the user's question |
| `answer` | string | LLM-generated answer grounded in context |
| `num_sources` | int | Number of facts used from knowledge graph |
| `reranked` | bool | Whether cross-encoder reranking was applied |
| `context` | object | Retrieval metadata (facts, timing) |

**Response Codes:**
- `200 OK` - Query successful
- `400 Bad Request` - Invalid request (e.g., empty question)
- `500 Internal Server Error` - Query processing failed

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is nitrogen narcosis?",
    "temperature": 0.7,
    "max_tokens": 500
  }' | jq
```

---

### POST `/api/query/stream` (Server-Sent Events)

Query the knowledge graph with streaming response (real-time token generation).

**Authentication:** None (Phase 1.0), `admin`, `instructor`, or `student` (Phase 1.1+)

**Request:**

```http
POST /api/query/stream HTTP/1.1
Content-Type: application/json

{
  "question": "Explain the buddy system in scuba diving",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Request Body:** Same as `/api/query/` (non-streaming)

**Response (SSE Stream):**

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"token": "The", "index": 1}

data: {"token": " buddy", "index": 2}

data: {"token": " system", "index": 3}

data: {"token": " is", "index": 4}

...

data: {"done": true, "token_count": 245, "duration_seconds": 12.3, "tokens_per_second": 19.9, "context_facts": 5}
```

**SSE Event Format:**

Each event is prefixed with `data: ` and contains JSON:

**Token Event:**
```json
{
  "token": "string",
  "index": 1
}
```

**Completion Event:**
```json
{
  "done": true,
  "token_count": 245,
  "duration_seconds": 12.3,
  "tokens_per_second": 19.9,
  "context_facts": 5
}
```

**Error Event:**
```json
{
  "error": "Internal error",
  "detail": "Ollama service unavailable"
}
```

**cURL Example:**

```bash
curl -N -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the signs of decompression sickness?",
    "temperature": 0.7
  }'
```

**JavaScript/Fetch Example:**

```javascript
const eventSource = new EventSource('/api/query/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What are the risks of deep diving?',
    temperature: 0.7
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.token) {
    // Append token to UI
    console.log(data.token);
  }
  
  if (data.done) {
    // Query complete
    console.log(`Completed in ${data.duration_seconds}s`);
    eventSource.close();
  }
  
  if (data.error) {
    // Handle error
    console.error(data.error);
    eventSource.close();
  }
};
```

**Response Headers:**

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no  # Disable nginx buffering
```

---

### GET `/api/query/health`

Check if the RAG query system is operational.

**Authentication:** None

**Request:**

```http
GET /api/query/health HTTP/1.1
```

**Response (Healthy):**

```json
{
  "status": "healthy",
  "provider": "ollama",
  "model": "qwen2.5:7b-instruct-q8_0",
  "test_response": "2 + 2 equals 4"
}
```

**Response (Unhealthy):**

```json
{
  "status": "unavailable",
  "error": "Ollama service not responding",
  "detail": "Connection refused to http://ollama:11434"
}
```

**Response Codes:**
- `200 OK` - Service healthy
- `503 Service Unavailable` - Service down

**cURL Example:**

```bash
curl http://localhost:8000/api/query/health | jq
```

---

## Status & Monitoring

### GET `/api/health`

Overall system health check.

**Authentication:** None

**Request:**

```http
GET /api/health HTTP/1.1
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "neo4j": "connected",
    "ollama": "connected",
    "graphiti": "available"
  },
  "timestamp": "2025-10-28T14:30:00Z"
}
```

**Response Codes:**
- `200 OK` - System healthy
- `503 Service Unavailable` - One or more services down

**cURL Example:**

```bash
curl http://localhost:8000/api/health | jq
```

---

### GET `/api/graph/stats`

Get knowledge graph statistics.

**Authentication:** None (Phase 1.0), `admin` only (Phase 1.1+)

**Request:**

```http
GET /api/graph/stats HTTP/1.1
```

**Response:**

```json
{
  "nodes": {
    "total": 250,
    "by_label": {
      "Entity": 205,
      "EpisodeType": 72
    }
  },
  "relationships": {
    "total": 2229,
    "by_type": {
      "RELATES_TO": 1850,
      "MENTIONS": 379
    }
  },
  "indexes": {
    "total": 8,
    "rag_indexes": 3,
    "graphiti_indexes": 5
  }
}
```

**cURL Example:**

```bash
curl http://localhost:8000/api/graph/stats | jq
```

---

## Error Handling

### Standard Error Response

All errors return this format:

```json
{
  "detail": "Error message",
  "error_code": "UPLOAD_FAILED",
  "timestamp": "2025-10-28T14:30:00Z"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `INVALID_FILE_TYPE` | File type not supported |
| 400 | `INVALID_QUESTION` | Question too short/long |
| 400 | `INVALID_PARAMETER` | Temperature out of range |
| 413 | `FILE_TOO_LARGE` | File exceeds 50MB |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `DOCLING_FAILED` | PDF conversion failed |
| 500 | `GRAPHITI_FAILED` | Entity extraction failed |
| 503 | `SERVICE_UNAVAILABLE` | Neo4j/Ollama down |

### Error Response Examples

**400 Bad Request:**
```json
{
  "detail": "Question must be between 1 and 1000 characters",
  "error_code": "INVALID_QUESTION"
}
```

**413 Payload Too Large:**
```json
{
  "detail": "File size (75MB) exceeds maximum allowed size (50MB)",
  "error_code": "FILE_TOO_LARGE"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Docling conversion timeout after 300 seconds",
  "error_code": "DOCLING_FAILED",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Ollama service not responding",
  "error_code": "SERVICE_UNAVAILABLE",
  "service": "ollama"
}
```

---

## Rate Limiting

### Current Status (Phase 1.0)
**No rate limiting** - Development mode.

### Future (Phase 1.1+)

Rate limits will be enforced per user role:

| Role | Queries/Hour | Uploads/Day | Burst |
|------|--------------|-------------|-------|
| `student` | 20 | 0 | 5 |
| `instructor` | 100 | 10 | 20 |
| `admin` | Unlimited | Unlimited | Unlimited |

**Rate Limit Headers:**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698764400
```

**Rate Limit Exceeded Response:**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 3600

{
  "detail": "Rate limit exceeded: 100 queries per hour",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600,
  "limit": 100,
  "remaining": 0,
  "reset_at": "2025-10-28T15:00:00Z"
}
```

---

## Request/Response Examples

### Complete Upload & Query Flow

**Step 1: Upload Document**

```bash
# Upload diving manual
UPLOAD_RESPONSE=$(curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/ffessm-n1.pdf")

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"
```

**Step 2: Monitor Processing**

```bash
# Check status every 30 seconds
while true; do
  STATUS=$(curl -s http://localhost:8000/api/upload/$UPLOAD_ID/status)
  STAGE=$(echo $STATUS | jq -r '.stage')
  PROGRESS=$(echo $STATUS | jq -r '.progress')
  
  echo "Stage: $STAGE ($PROGRESS%)"
  
  if [[ "$STAGE" == "complete" ]]; then
    echo "Processing complete!"
    break
  fi
  
  sleep 30
done
```

**Step 3: Query Knowledge Graph**

```bash
# Non-streaming query
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the certification requirements for FFESSM Level 1?",
    "temperature": 0.7,
    "max_tokens": 500
  }' | jq '.answer'
```

**Step 4: Streaming Query**

```bash
# Streaming query (real-time)
curl -N -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the risks of nitrogen narcosis at depth",
    "temperature": 0.7
  }'
```

---

## Testing

### Automated Testing

Use the provided test scripts:

```bash
# Bash test suite (4 tests)
./scripts/test_rag_query.sh

# Python test suite (advanced)
python scripts/test_rag_query.py

# Expected output: 4/4 tests passing
```

### Manual Testing

**Health Check:**
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/query/health
```

**Upload Test:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.pdf"
```

**Query Test:**
```bash
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question", "max_tokens": 100}'
```

---

## Performance Metrics

### Local Development (Mac M1 Max CPU)

| Metric | Value | Notes |
|--------|-------|-------|
| Upload Response | < 100ms | File saved, processing starts |
| Docling Conversion | 30-60s | Per 20-page PDF |
| Graphiti Ingestion | 60-180s | Per 70 chunks |
| Non-Streaming Query | 10-60s | CPU-only inference |
| Streaming First Token | 1-3s | Time to first token |
| Streaming Rate | 10-15 tok/s | CPU-only (expected) |

### Production (DigitalOcean RTX 4000 Ada)

| Metric | Target | Notes |
|--------|--------|-------|
| Upload Response | < 100ms | Same as local |
| Docling Conversion | 15-30s | GPU-accelerated |
| Graphiti Ingestion | 30-90s | GPU-accelerated |
| Non-Streaming Query | 3-8s | GPU inference |
| Streaming First Token | 0.5-1s | GPU latency |
| Streaming Rate | 40-60 tok/s | GPU target (Qwen Q8_0) |

**Reference:** See `resources/251028-rag-gpu-deployment-guide.md` for complete performance analysis.

---

## API Versioning & Changes

### Version 1.0 (Current) - October 28, 2025

**New Endpoints:**
- ✅ `POST /api/query/` - Non-streaming RAG query
- ✅ `POST /api/query/stream` - Streaming RAG query (SSE)
- ✅ `GET /api/query/health` - Query system health

**Model:**
- ✅ Qwen 2.5 7B Q8_0 (8.1GB)
- ✅ Optimal RAG quality (98/100)
- ✅ 40-60 tok/s on GPU (target)

**Changes from v0.9:**
- Switched from OpenAI GPT-5-nano to Anthropic Claude Haiku 4.5 (Graphiti)
- Switched from Mistral 7B Q5_K_M to Qwen 2.5 7B Q8_0 (RAG queries)
- Added streaming support (SSE)
- Fixed AsyncIO threading architecture
- Added comprehensive error handling

### Upcoming in Version 1.1 (Phase 1.1)

**Planned Features:**
- 🔜 Supabase Auth integration (JWT tokens)
- 🔜 User roles (admin, instructor, student)
- 🔜 Rate limiting per role
- 🔜 Multi-tenancy (group-based access)
- 🔜 Conversation history
- 🔜 Bookmarks/favorites

---

## Related Documentation

- **[SETUP.md](SETUP.md)** - Local development setup
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[GRAPHITI.md](GRAPHITI.md)** - Knowledge graph integration
- **[DOCLING.md](DOCLING.md)** - Document processing

**Reference Guides:**
- `Devplan/PHASE-1.0-RAG-QUERY-IMPLEMENTATION.md` - Implementation plan
- `Devplan/STATUS-PHASE-1.0-COMPLETION-REPORT.md` - Completion report
- `resources/251028-rag-gpu-deployment-guide.md` - GPU deployment

---

**Last Updated:** October 28, 2025, 16:20 CET  
**API Version:** 1.0  
**Status:** ✅ Production-Ready (Local Dev)

