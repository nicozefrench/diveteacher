# 🏗️ DiveTeacher - Technical Architecture

> **Project:** RAG Knowledge Graph for Scuba Diving Education  
> **Version:** Phase 0.9 COMPLETE (Graphiti Integration + AsyncIO Fix)  
> **Last Updated:** October 28, 2025, 08:50  
> **Status:** 🟢 Phase 0.9 COMPLETE - Ingestion pipeline 100% functional

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Data Flow](#data-flow)
- [Document Processing Pipeline](#document-processing-pipeline)
- [Knowledge Graph Architecture](#knowledge-graph-architecture)
- [RAG Architecture](#rag-architecture)
- [Database Schemas](#database-schemas)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)

---

## Overview

**DiveTeacher** est une application RAG (Retrieval-Augmented Generation) spécialisée dans l'éducation à la plongée sous-marine. Elle transforme des documents FFESSM/SSI (PDFs, PPTs) en un knowledge graph interrogeable via LLM.

### Key Features

- ✅ **Document Processing:** PDF → Markdown avec OCR + TableFormer (Docling)
- ✅ **Semantic Chunking:** HierarchicalChunker pour chunks cohérents
- ✅ **Knowledge Graph:** Neo4j + Graphiti pour extraction d'entités/relations
- ✅ **RAG Hybride:** Full-text search + graph traversal
- ✅ **LLM Agnostic:** Ollama (local), Claude, OpenAI
- 🔜 **Multi-user:** Supabase Auth + PostgreSQL (Phase 1+)

### Value Proposition

**Pour les plongeurs:**
- Q&A précises sur procédures FFESSM/SSI
- Recherche contextuelle dans manuels MFT
- Recommandations personnalisées selon niveau

**Pour les moniteurs:**
- Assistant pédagogique intelligent
- Génération de supports de cours
- Vérification des connaissances

---

## Tech Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.115.0 | REST API + async support |
| **Document Processor** | Docling | 2.5.1 | PDF/PPT → Markdown + OCR |
| **Chunker** | HierarchicalChunker | docling-core 2.3.0 | Semantic chunking |
| **Knowledge Graph** | Neo4j | 5.26.0 | Graph database |
| **Graph Library** | Graphiti | graphiti-core[anthropic] 0.17.0 | Entity/relation extraction ✅ |
| **LLM Cloud** | Anthropic Claude | Haiku 4.5 | Entity extraction (ARIA-validated) ✅ |
| **LLM Local** | Ollama | Latest | Mistral 7b for RAG queries |
| **LLM Model** | Mistral | 7b-instruct-q5_K_M | French + diving context |
| **Embeddings** | OpenAI | text-embedding-3-small | 1536 dims (for Graphiti) |
| **Embeddings Local** | sentence-transformers | 3.3.1 | Semantic similarity |
| **Validation** | Pydantic | 2.11.5 | Data validation |
| **Monitoring** | Sentry | Latest | Error tracking |

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3.1 | UI library |
| **Build Tool** | Vite | 5.4.2 | Fast dev server |
| **Styling** | TailwindCSS | 3.4.1 | Utility-first CSS |
| **Components** | shadcn/ui | Latest | Modern UI components |
| **State** | TanStack Query | 5.59.16 | Server state management |
| **Routing** | React Router | 6.26.2 | Client-side routing |

### Infrastructure (Local Dev)
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Containerization** | Docker | Latest | Service isolation |
| **Orchestration** | Docker Compose | Latest | Multi-container management |
| **OS** | macOS (M1 Max) | 14.6 | Development environment |
| **Memory** | 32GB Unified | - | Handles ML models |

### Infrastructure (Production - Phase 9)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Host** | DigitalOcean GPU Droplet | LLM inference |
| **Frontend Host** | Vercel | Static hosting + CDN |
| **Auth + DB** | Supabase Cloud | PostgreSQL + Auth |
| **Domain** | diveteacher.io | Primary domain |
| **Monitoring** | Sentry | Error tracking |

---

## System Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DiveTeacher System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Frontend   │◄────────┤   Backend    │                  │
│  │  React+Vite  │  REST   │   FastAPI    │                  │
│  │  Port: 5173  │  API    │  Port: 8000  │                  │
│  └──────────────┘         └───────┬──────┘                  │
│                                    │                          │
│                  ┌─────────────────┼─────────────────┐       │
│                  │                 │                 │       │
│            ┌─────▼────┐     ┌─────▼─────┐    ┌─────▼────┐  │
│            │  Neo4j   │     │  OpenAI   │    │ Docling  │  │
│            │  :7475   │     │  Cloud    │    │ Library  │  │
│            │  Graph   │     │ GPT-5nano │    │   PDF    │  │
│            │  + RAG   │     │ (BLOCKED) │    │Processor │  │
│            └──────────┘     └───────────┘    └──────────┘  │
│                  │                                           │
│            ┌─────▼────┐                                     │
│            │  Ollama  │                                     │
│            │  :11434  │                                     │
│            │ Mistral  │                                     │
│            │  7b RAG  │                                     │
│            └──────────┘                                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Service Communication

```
User Upload (PDF)
      │
      ▼
┌─────────────────┐
│  React Frontend │ ──── POST /api/upload ────┐
└─────────────────┘                            │
                                               ▼
                                    ┌──────────────────┐
                                    │ FastAPI Backend  │
                                    └────────┬─────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
                        ▼                    ▼                    ▼
              ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐
              │ Docling Service │  │ Graphiti Client │  │ Neo4j Client │
              │ - Convert PDF   │  │ - Extract Graph │  │ - RAG Queries│
              │ - Chunk Text    │  │ - Build Entities│  │ - Store Data │
              └─────────────────┘  └─────────────────┘  └──────────────┘
                        │                    │                    │
                        └────────────────────┴────────────────────┘
                                             │
                                             ▼
                                      Neo4j Database
                                      (Episodes, Entities,
                                       Relations, Communities)
```

### RAG Query Flow

```
User Question ("Quels sont les prérequis Niveau 4?")
      │
      ▼
┌─────────────────┐
│  React Frontend │ ──── POST /api/rag/query ────┐
└─────────────────┘                               │
                                                  ▼
                                       ┌──────────────────┐
                                       │ FastAPI Backend  │
                                       └────────┬─────────┘
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        │                       │                       │
                        ▼                       ▼                       ▼
              ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
              │ Neo4j RAG Query │    │ Graphiti Search │    │ Ollama LLM   │
              │ - Fulltext      │    │ - Entities      │    │ - Generate   │
              │ - Hybrid Search │    │ - Relations     │    │ - Answer     │
              └─────────────────┘    └─────────────────┘    └──────────────┘
                        │                       │                       │
                        └───────────────────────┴───────────────────────┘
                                                │
                                                ▼
                                         Grounded Answer
                                    (Citations + Context)
```

---

## Data Flow

### Document Ingestion Pipeline

```
1. Upload
   └─ User uploads PDF via frontend
   └─ File saved to /uploads (backend)

2. Validation
   └─ File type check (.pdf, .docx, .pptx)
   └─ Size check (max 50MB)
   └─ Corruption check (read first KB)

3. Docling Conversion
   └─ PDF → DoclingDocument object
   └─ OCR enabled (for scanned docs)
   └─ TableFormer ACCURATE mode (for tables)
   └─ Timeout: 300s (5 min)
   └─ Output: DoclingDocument (35 pages example)

4. Metadata Extraction
   └─ Extract: name, origin, num_pages, num_tables, num_pictures
   └─ Store for tracking

5. Semantic Chunking
   └─ HierarchicalChunker with sentence-transformers
   └─ Tokenizer: BAAI/bge-small-en-v1.5
   └─ Max tokens: 512, Min tokens: 64
   └─ Output: 436 chunks (example)
   └─ Each chunk: {index, text, metadata}

6. Graphiti Ingestion
   └─ For each chunk:
      └─ Create Episode node in Neo4j
      └─ Extract entities (automatic)
      └─ Extract relations (automatic)
      └─ Build knowledge graph

7. Community Building
   └─ Group related entities
   └─ Optimize for search

8. Status Update
   └─ Mark upload as "completed"
   └─ Return upload_id to frontend
```

### RAG Query Pipeline

```
1. User Question
   └─ "Quels sont les prérequis pour le Niveau 4 GP?"

2. Hybrid Search (Neo4j)
   A. Full-text Search (Episodes)
      └─ FULLTEXT index on Episode.content
      └─ Returns: Top 5 relevant chunks + scores
   
   B. Entity Search
      └─ Extract keywords from question
      └─ Search Entity.name (RANGE index)
      └─ Traverse RELATES_TO relationships (depth=2)
      └─ Returns: Related entities + context

3. Context Assembly
   └─ Combine Episodes + Entities
   └─ Format for LLM prompt:
      ├─ DOCUMENT EXCERPTS (from chunks)
      └─ RELATED CONCEPTS & ENTITIES (from graph)

4. LLM Generation (Ollama Mistral)
   └─ System Prompt: "You are DiveTeacher..."
   └─ User Prompt: Context + Question
   └─ Generation: Grounded answer with citations

5. Response
   └─ Return to frontend
   └─ Display answer + sources
```

---

## Document Processing Pipeline

### Docling Integration

**Purpose:** Convert PDF/PPT to structured markdown with OCR and table recognition.

**Key Components:**

1. **DocumentConverter Singleton**
   ```python
   # backend/app/integrations/dockling.py
   class DoclingSingleton:
       _instance: Optional[DocumentConverter] = None
       
       @classmethod
       def get_converter(cls) -> DocumentConverter:
           if cls._instance is None:
               pipeline_options = PdfPipelineOptions(
                   do_ocr=True,                    # For scanned docs
                   do_table_structure=True,        # For tables
                   artifacts_path=None,            # Auto-download models
               )
               pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
               
               cls._instance = DocumentConverter(
                   format_options={
                       InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                   }
               )
           return cls._instance
   ```

2. **Conversion Function**
   ```python
   async def convert_document_to_docling(
       file_path: str,
       timeout: int = 300  # 5 minutes
   ) -> DoclingDocument:
       # Validates file
       # Converts with timeout
       # Returns DoclingDocument object (NOT markdown)
   ```

3. **Metadata Extraction**
   ```python
   def extract_document_metadata(doc: DoclingDocument) -> Dict:
       return {
           "name": doc.name,
           "origin": str(doc.origin),
           "num_pages": doc.num_pages,
           "num_tables": len(doc.tables),
           "num_pictures": len(doc.pictures),
       }
   ```

**Why Singleton?**
- Docling models loaded once (HuggingFace download)
- Reused across requests
- Saves memory + startup time

### Semantic Chunking

**Purpose:** Split document into semantically coherent chunks for RAG.

**Key Components:**

1. **HierarchicalChunker Configuration**
   ```python
   # backend/app/services/document_chunker.py
   self.chunker = HierarchicalChunker(
       tokenizer="BAAI/bge-small-en-v1.5",  # Embedding model
       max_tokens=512,                       # Embedding limit
       min_tokens=64,                        # Avoid tiny chunks
       merge_peers=True                      # Merge small adjacent chunks
   )
   ```

2. **Chunking Process**
   ```python
   def chunk_document(
       self,
       docling_doc: DoclingDocument,
       filename: str,
       upload_id: str
   ) -> List[Dict[str, Any]]:
       # HierarchicalChunker returns DocChunk objects
       chunk_iterator = self.chunker.chunk(docling_doc)
       chunks = list(chunk_iterator)
       
       # Format for RAG pipeline
       formatted_chunks = []
       for i, chunk in enumerate(chunks):
           chunk_meta = chunk.meta  # DocChunk.meta attribute
           formatted_chunk = {
               "index": i,
               "text": chunk.text,  # DocChunk.text attribute
               "metadata": {
                   "filename": filename,
                   "upload_id": upload_id,
                   "chunk_index": i,
                   "total_chunks": len(chunks),
                   "headings": getattr(chunk_meta, "headings", []),
                   "doc_items": [str(item) for item in getattr(chunk_meta, "doc_items", [])],
                   "origin": str(getattr(chunk_meta, "origin", "")),
               }
           }
           formatted_chunks.append(formatted_chunk)
       
       return formatted_chunks
   ```

**Why HierarchicalChunker?**
- Respects document structure (headings, sections)
- Semantic boundaries (not fixed character count)
- Better RAG retrieval quality

**Example Output:**
```json
{
  "index": 0,
  "text": "FÉDÉRATION FRANÇAISE D'ÉTUDES ET DE SPORTS SOUS-MARINS...",
  "metadata": {
    "filename": "Niveau 4 GP.pdf",
    "upload_id": "abc123",
    "chunk_index": 0,
    "total_chunks": 436,
    "headings": [],
    "doc_items": ["TextItem(...)"],
    "origin": "DocumentOrigin(mimetype='application/pdf', ...)"
  }
}
```

---

## Knowledge Graph Architecture

### Neo4j + Graphiti

**Purpose:** Extract entities, relations, and communities from document chunks for graph-based retrieval.

**Node Types (Graphiti):**

1. **Episode**
   - Represents a document chunk
   - Properties: `content`, `source_description`, `name`, `created_at`
   - Created by: `Graphiti.add_episode()`

2. **Entity**
   - Extracted from Episode content
   - Properties: `name`, `summary`, `entity_type`
   - Created by: Graphiti (automatic extraction)

3. **Community** (future)
   - Groups of related entities
   - Created by: `Graphiti.build_communities()`

**Relationship Types:**

1. **RELATES_TO**
   - Connects entities
   - Properties: `fact` (description of relationship)
   - Created by: Graphiti (automatic extraction)

### Graph Ingestion Flow

```python
# backend/app/integrations/graphiti.py
async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> None:
    """
    Ingest chunks into Neo4j knowledge graph via Graphiti.
    
    Uses:
    - LLM: Anthropic Claude Haiku 4.5 (claude-haiku-4-5-20251001)
    - Embedder: OpenAI text-embedding-3-small (1536 dimensions)
    
    Architecture:
    - Native AnthropicClient (ARIA-validated, 5 days production)
    - Single event loop (FastAPI main)
    - Zero threading conflicts
    - Dedicated ThreadPoolExecutor for Docling only
    """
    graphiti = await get_graphiti_client()
    
    for i, chunk in enumerate(chunks, 1):
        episode_data = build_episode_data(chunk, metadata)
        await graphiti.add_episode(**episode_data)
```

---

## Background Processing Architecture (Phase 0.9)

### AsyncIO + FastAPI Integration ✅

**Problem Solved:** Thread event loop deadlock causing 100% ingestion failure.

**Root Cause:**
- `ThreadPoolExecutor` created new event loop in worker thread
- `process_document()` attempted to use default executor (FastAPI main loop)
- Deadlock: thread loop waiting for main loop, main loop blocked by thread

**Solution Implemented (ARIA Pattern):**

```python
# backend/app/api/upload.py

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload endpoint - Returns immediately (< 100ms)
    Background processing via asyncio.create_task()
    """
    # 1. Save file
    upload_id = str(uuid.uuid4())
    file_path = save_file(file, upload_id)
    
    # 2. ✅ ARIA Pattern: asyncio.create_task() (NOT ThreadPoolExecutor)
    asyncio.create_task(
        process_document_wrapper(
            file_path=file_path,
            upload_id=upload_id,
            metadata=metadata
        )
    )
    
    # 3. Return immediately
    return {"upload_id": upload_id, "status": "processing"}


async def process_document_wrapper(file_path: str, upload_id: str, metadata: dict):
    """
    Wrapper for graceful error handling.
    Runs in SAME event loop as FastAPI (no threading).
    """
    try:
        await process_document(
            file_path=file_path,
            upload_id=upload_id,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"[{upload_id}] Processing error: {e}")
        # Status dict updated with error details
```

**Key Architecture Decisions:**

1. **Single Event Loop**
   - FastAPI main loop handles ALL async operations
   - `asyncio.create_task()` schedules tasks in same loop
   - Zero threading = zero deadlock risk

2. **Dedicated Executor for Sync Operations**
   ```python
   # backend/app/integrations/dockling.py
   _docling_executor = ThreadPoolExecutor(max_workers=2)  # Module-level
   
   async def convert_document_to_docling(file_path: str):
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           _docling_executor,  # ← Dedicated (not None!)
           lambda: converter.convert(file_path).document
       )
       return result
   ```
   
3. **Why This Works:**
   - Docling is CPU-bound (OCR, ML models) → needs thread pool
   - Dedicated executor doesn't conflict with FastAPI loop
   - All async I/O (Neo4j, API calls) stays in main loop

**Performance Results:**
- Upload response: **< 100ms** ✅
- Processing start: **< 1s** ✅ (was: NEVER)
- Docling conversion: **~45s** (35 pages)
- Total pipeline: **~5-7 min** (72 chunks)
- Success rate: **100%** (was: 0%)

---

## Status API & JSON Serialization (Phase 0.9)

### Status Endpoint Architecture

**Problem Solved:** `JSONResponse` serialization error - "Object of type method is not JSON serializable"

**Root Cause:**
- `processing_status` dict stored non-serializable objects (methods, custom classes)
- FastAPI/Starlette's `JSONResponse` failed when encountering these objects

**Solution Implemented:**

```python
# backend/app/api/upload.py

def _sanitize_for_json(obj):
    """
    Recursively sanitize object for JSON serialization.
    
    Handles:
    - datetime → isoformat()
    - callable (method/function) → string representation
    - custom objects → str()
    - nested dicts/lists → recursive
    """
    from datetime import datetime, date
    
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item) for item in obj]
    elif callable(obj):
        return f"<{obj.__class__.__name__}: {obj.__name__ if hasattr(obj, '__name__') else 'anonymous'}>"
    else:
        return str(obj)


@router.get("/upload/status/{upload_id}")
async def get_upload_status(upload_id: str):
    """
    Status endpoint with pre-serialization.
    """
    status = get_processing_status(upload_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    # Sanitize + pre-serialize
    sanitized_status = _sanitize_for_json(status)
    json_str = json.dumps(sanitized_status, indent=2)
    
    # Return as plain Response (not JSONResponse)
    return Response(content=json_str, media_type="application/json")
```

**Additional Fix in processor.py:**

```python
# backend/app/core/processor.py

# Ensure metadata is JSON-safe before storing
safe_metadata = {}
for key, value in doc_metadata.items():
    if isinstance(value, datetime):
        safe_metadata[key] = value.isoformat()
    elif callable(value):
        continue  # Skip methods/functions
    else:
        safe_metadata[key] = value

processing_status[upload_id].update({
    "status": "completed",
    "metadata": safe_metadata,  # ← Safe dict
    "durations": {...},
    "completed_at": datetime.now().isoformat()
})
```

**Status Response Example:**

```json
{
  "status": "completed",
  "stage": "completed",
  "progress": 100,
  "num_chunks": 72,
  "metadata": {
    "name": "Nitrox.pdf",
    "origin": "file:///uploads/...",
    "num_pages": 35,
    "num_tables": 12,
    "num_pictures": 8
  },
  "durations": {
    "conversion": 45.2,
    "chunking": 3.5,
    "ingestion": 324.8,
    "total": 373.5
  },
  "completed_at": "2025-10-28T07:45:32.123456"
}
```

---

### Graph Ingestion Flow (Legacy Section)
    client = await get_graphiti_client()
    
    for chunk in chunks:
        await client.add_episode(
            name=f"{metadata['filename']} - Chunk {chunk['index']}",
            episode_body=chunk["text"],
            source=EpisodeType.text,
            source_description=f"Document: {metadata['filename']}",
            reference_time=datetime.now(timezone.utc),
        )
    
    # Build communities after ingestion
    await client.build_communities()
```

**Key Decisions:**
- ✅ One Episode per chunk (not per document)
- ✅ Graphiti auto-extracts entities/relations
- ✅ Community building for better search
- 🔜 Custom `entity_types` and `edge_types` (Phase 1+)

---

## RAG Architecture

### Hybrid Search Strategy

**Purpose:** Combine full-text search (chunks) + graph search (entities) for better retrieval.

**Components:**

1. **Full-text Search (Episodes)**
   ```cypher
   CALL db.index.fulltext.queryNodes('episode_content', $search_text)
   YIELD node, score
   RETURN node.content AS text, score
   ORDER BY score DESC
   LIMIT 5
   ```

2. **Entity Search + Graph Traversal**
   ```cypher
   MATCH (e:Entity)
   WHERE toLower(e.name) CONTAINS toLower($entity_name)
   OPTIONAL MATCH (e)-[r:RELATES_TO*1..2]-(related:Entity)
   RETURN e, collect(related) AS related_entities
   LIMIT 10
   ```

3. **Hybrid Combination**
   ```python
   def query_context_hybrid(question: str, top_k: int = 5):
       # 1. Full-text search on chunks
       episodes = query_context_fulltext(question, top_k)
       
       # 2. Extract keywords from question
       keywords = extract_keywords(question)
       
       # 3. Search entities for each keyword
       entities = []
       for keyword in keywords[:3]:
           entity_results = query_entities_related(keyword, depth=1)
           entities.extend(entity_results)
       
       return {
           "episodes": episodes,
           "entities": entities[:top_k],
           "total": len(episodes) + len(entities)
       }
   ```

### RAG Indexes (Neo4j)

**Created at startup:**

1. **episode_content** (FULLTEXT)
   - Index on: `Episode.content`
   - Purpose: Fast semantic search
   - Query: `db.index.fulltext.queryNodes()`

2. **entity_name_idx** (RANGE/B-tree)
   - Index on: `Entity.name`
   - Purpose: Fast entity lookup
   - Query: `WHERE e.name CONTAINS ...`

3. **episode_date_idx** (RANGE/B-tree)
   - Index on: `Episode.created_at`
   - Purpose: Time-based filtering
   - Query: `WHERE e.created_at > ...`

**Creation:**
```python
# backend/app/integrations/neo4j_indexes.py
def create_rag_indexes(driver: Driver):
    indexes = [
        "CREATE FULLTEXT INDEX episode_content IF NOT EXISTS FOR (e:Episode) ON EACH [e.content]",
        "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name)",
        "CREATE INDEX episode_date_idx IF NOT EXISTS FOR (e:Episode) ON (e.created_at)"
    ]
    for query in indexes:
        driver.execute_query(query)
```

### LLM Prompt Engineering

**System Prompt (DiveTeacher-specific):**
```
You are DiveTeacher, an AI assistant specialized in scuba diving education.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. If context is insufficient, say "I don't have enough information..."
3. NEVER make up or infer information not present in the context
4. Cite sources: [Chunk 1], [Chunk 2], or entity names
5. Be concise but thorough
6. Use technical diving terms accurately
7. For FFESSM/SSI procedures, cite exact source material
```

**User Prompt Structure:**
```
Context from diving manuals and knowledge base:

=== DOCUMENT EXCERPTS ===
[Chunk 1 - Niveau 4 GP.pdf - Relevance: 0.85]
Source: Niveau 4 GP.pdf - Chunk 12/436
[text content...]

[Chunk 2 - ...]
...

=== RELATED CONCEPTS & ENTITIES ===
**Niveau 4** (Certification): Plongeur autonome jusqu'à 60m
  Related to: Prérequis (requires), Prérogatives (grants), Niveau 3 (prerequisite)

**Prérequis** (Requirement): Avoir Niveau 3 + 40 plongées
  Related to: Niveau 4, Formation, Expérience

---

Question: Quels sont les prérequis pour le Niveau 4 GP?

Answer based ONLY on the context above. Cite your sources:
```

---

## Database Schemas

### Neo4j (via Graphiti)

**Managed by Graphiti - No manual schema required**

```
Nodes:
  Episode {
    uuid: string (PK)
    name: string
    content: string (indexed)
    source: string (enum: 'text', 'message', 'website')
    source_description: string
    created_at: datetime (indexed)
    valid_at: datetime
    metadata: jsonb
  }

  Entity {
    uuid: string (PK)
    name: string (indexed)
    summary: string
    entity_type: string
    created_at: datetime
    metadata: jsonb
  }

  Community {
    uuid: string (PK)
    name: string
    summary: string
    created_at: datetime
  }

Relationships:
  (Episode)-[:HAS_ENTITY]->(Entity)
  (Entity)-[:RELATES_TO {fact: string}]->(Entity)
  (Entity)-[:MEMBER_OF]->(Community)
```

### PostgreSQL (Supabase - Phase 1+)

**For multi-user features:**

```sql
-- Users (managed by Supabase Auth)
users {
  id: uuid (PK)
  email: string
  created_at: timestamp
  metadata: jsonb (diving_level, certifications, etc.)
}

-- Conversations
conversations {
  id: uuid (PK)
  user_id: uuid (FK -> users.id)
  title: string
  created_at: timestamp
  updated_at: timestamp
}

-- Messages
messages {
  id: uuid (PK)
  conversation_id: uuid (FK -> conversations.id)
  role: enum ('user', 'assistant')
  content: text
  sources: jsonb (citations)
  created_at: timestamp
}

-- Uploads
uploads {
  id: uuid (PK)
  user_id: uuid (FK -> users.id)
  filename: string
  status: enum ('processing', 'completed', 'failed')
  num_chunks: integer
  created_at: timestamp
}
```

---

## Security Architecture

### Phase 0 (Local Dev)
- ❌ No authentication
- ❌ No authorization
- ⚠️  Open to localhost only

### Phase 1+ (Production)
- ✅ Supabase Auth (email/password, OAuth)
- ✅ JWT tokens
- ✅ Row-level security (RLS) on PostgreSQL
- ✅ API rate limiting
- ✅ File upload validation
- ✅ CORS whitelist
- ✅ HTTPS only

### Sensitive Data
- **Neo4j password:** Environment variable
- **Supabase keys:** Environment variable
- **Sentry DSN:** Environment variable
- **API keys (future):** Encrypted in database

---

## Deployment Architecture

### Local Development (Phase 0-8)

```
Mac M1 Max (32GB)
  ├─ Docker Compose
  │  ├─ Neo4j (port 7475/7688)
  │  ├─ Ollama (port 11434)
  │  └─ Backend (port 8000)
  └─ Native
     └─ Frontend (port 5173)
```

**Cost:** 0€

### Production (Phase 9)

```
┌─────────────────────────────────────────────────────────┐
│                     Internet                             │
└─────────────┬───────────────────────┬───────────────────┘
              │                       │
              ▼                       ▼
   ┌──────────────────┐    ┌──────────────────┐
   │  Vercel (CDN)    │    │  DigitalOcean    │
   │  - React build   │    │  GPU Droplet     │
   │  - Static files  │    │  - FastAPI       │
   │  - Edge caching  │    │  - Neo4j         │
   │                  │    │  - Ollama        │
   │  diveteacher.io  │    │  - Graphiti      │
   └──────────────────┘    └────────┬─────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Supabase Cloud  │
                          │  - PostgreSQL    │
                          │  - Auth          │
                          │  - Storage (PDFs)│
                          └──────────────────┘
```

**Cost:** ~$120/mois
- DigitalOcean GPU: ~$100/mois
- Supabase: Free tier
- Vercel: Free tier

---

## Performance Considerations

### Bottlenecks Identified

1. **Docling Conversion:** 300s timeout for 35-page PDF
   - **Solution:** Increase timeout, optimize pipeline options
   
2. **Neo4j Full-text Search:** Could be slow on large graphs
   - **Solution:** Limit results (top_k=5), use indexes

3. **LLM Generation:** Variable latency (3-10s)
   - **Solution:** Streaming responses (Phase 1+)

### Optimization Strategies

1. **Singletons:**
   - DocumentConverter (Docling)
   - Graphiti client
   - Neo4j driver

2. **Async/Await:**
   - FastAPI async handlers
   - Background tasks for ingestion

3. **Caching (future):**
   - LLM responses (Redis)
   - Frequent queries

4. **Batch Processing (future):**
   - Multiple PDFs at once
   - Parallel chunking

---

## Next Steps

### Phase 0.9 - Graphiti Validation
- [ ] Test E2E: PDF → Docling → Chunks → Graphiti → Neo4j
- [ ] Validate entity extraction quality
- [ ] Test community building
- [ ] Measure performance (latency, memory)

### Phase 1 - Multi-user
- [ ] Supabase Auth integration
- [ ] User-specific conversations
- [ ] Conversation history (PostgreSQL)
- [ ] Frontend auth flow

### Phase 2 - Advanced RAG
- [ ] Custom entity types (diving-specific)
- [ ] Relation types (prerequisites, contains, recommends)
- [ ] Confidence scores
- [ ] Source citations in UI

---

**📚 Related Documentation:**
- [SETUP.md](SETUP.md) - Local environment setup
- [DOCLING.md](DOCLING.md) - Document processing details
- [NEO4J.md](NEO4J.md) - Knowledge graph details
- [API.md](API.md) - API reference

