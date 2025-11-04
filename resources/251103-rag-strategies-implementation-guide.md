# RAG Strategies Implementation Guide
## Complete Reference for Claude Sonnet 4.5 AI Agent

**Source Repository:** https://github.com/coleam00/ottomator-agents/tree/main/all-rag-strategies  
**Author:** Cole Medin (coleam00)  
**Purpose:** Implementation, debugging, and optimization guide for advanced RAG systems

---

## Table of Contents

1. [Overview of RAG Strategies](#overview-of-rag-strategies)
2. [Foundational RAG Architecture](#foundational-rag-architecture)
3. [Agentic RAG Strategies](#agentic-rag-strategies)
4. [Advanced RAG Techniques](#advanced-rag-techniques)
5. [Knowledge Graph Integration](#knowledge-graph-integration)
6. [Multi-Format Document Processing](#multi-format-document-processing)
7. [Production Best Practices](#production-best-practices)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Resource Links](#resource-links)

---

## Overview of RAG Strategies

### Core Principles

RAG (Retrieval Augmented Generation) systems enhance LLM responses by retrieving relevant information from a knowledge base. The strategies presented here move beyond "naive lookups" to create intelligent, context-aware retrieval systems.

### Key Limitations of Traditional RAG

Traditional RAG systems face several critical challenges:

- **Table Analysis Weakness:** Struggles with numerical data and spreadsheet analysis
- **Context Fragmentation:** Misses big-picture context when working with chunks
- **Cross-Document Blindness:** Fails to connect information across multiple documents
- **Static Tool Usage:** Cannot dynamically switch between lookup and analysis modes
- **Lack of Self-Correction:** No ability to self-improve retrieval strategies

### Evolution to Agentic RAG

Agentic RAG overcomes these limitations by:

- Reasoning about how to explore knowledge bases
- Self-improving lookup strategies
- Dynamically selecting appropriate tools based on query type
- Switching between vector search, SQL queries, and full document retrieval
- Connecting information across entire knowledge bases

---

## Foundational RAG Architecture

### Basic RAG Components

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/foundational-rag-agent

This implementation provides a simple, production-ready RAG system using:

- **Framework:** Pydantic AI
- **Database:** Supabase with pgvector
- **Embeddings:** OpenAI embeddings
- **Document Types:** TXT and PDF

### Architecture Structure

```
foundational-rag-agent/
├── database/
│   └── setup.py              # Database setup and connection utilities
├── document_processing/
│   ├── chunker.py            # Text chunking functionality
│   ├── embeddings.py         # Embeddings generation with OpenAI
│   ├── ingestion.py          # Document ingestion pipeline
│   └── processors.py         # TXT and PDF processing
├── agent/
│   ├── agent.py              # Main agent definition
│   ├── prompts.py            # System prompts
│   └── tools.py              # Knowledge base search tool
├── ui/
│   └── app.py                # Streamlit application
└── tests/
    ├── test_chunker.py
    ├── test_embeddings.py
    ├── test_ingestion.py
    ├── test_processors.py
    └── test_agent.py
```

### Implementation Steps

1. **Database Setup**
   - Use Supabase, Neon, or self-hosted PostgreSQL
   - Enable pgvector extension
   - Create tables for documents and embeddings

2. **Document Processing Pipeline**
   ```python
   # Key components:
   - Text extraction (PDF, TXT)
   - Chunking strategy (default: 1000 characters)
   - Embedding generation
   - Vector storage
   ```

3. **Agent Configuration**
   - Define system prompts
   - Configure search tools
   - Set up Streamlit UI

---

## Agentic RAG Strategies

### n8n Agentic RAG Agent

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/n8n-agentic-rag-agent

This template provides a complete Agentic RAG implementation in n8n with multiple tools.

#### Key Features

- **Intelligent Tool Selection:** Automatically switches between RAG lookups, SQL queries, or full document retrieval
- **Complete Document Context:** Accesses entire documents when needed instead of just chunks
- **Accurate Numerical Analysis:** Uses SQL for precise calculations on tabular data
- **Cross-Document Insights:** Connects information across entire knowledge base
- **Multi-File Processing:** Handles multiple documents in a single workflow loop

#### Tool Arsenal

1. **RAG Lookup Tool**
   - Semantic search through vector embeddings
   - Returns relevant chunks with metadata

2. **Document Listing Tool**
   - Lists all documents in knowledge base
   - Helps agent understand available resources

3. **Full Document Retrieval Tool**
   - Extracts complete text from specific documents
   - Used when context requires full document understanding

4. **SQL Query Tool**
   - Queries tabular data in `document_rows` table
   - Performs calculations, aggregations, and filtering

#### Agent Decision Logic

```
Query Analysis Flow:
1. Analyze user question
2. Determine if requires:
   a. SQL query (for numerical/tabular data) → Use SQL tool
   b. RAG lookup (for semantic search) → Use RAG tool
   c. Full context (for comprehensive understanding) → List docs + Retrieve full docs
3. If initial approach fails → Try alternative tool
4. Always inform user if answer not found
```

### Ultimate n8n RAG Agent

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/ultimate-n8n-rag-agent

Enhanced version with **reranking** and **agentic chunking**.

#### Additional Features

- **Reranking:** Post-retrieval ranking to improve relevance
- **Agentic Chunking:** Dynamic chunk creation based on content
- **Advanced Metadata:** Rich metadata tracking for better retrieval

#### Reranking Implementation

```python
# Reranking improves initial retrieval results
# Steps:
1. Initial vector search retrieves top-k candidates
2. Reranker model scores each candidate
3. Results reordered by reranker scores
4. Top results passed to LLM
```

#### Agentic Chunking Strategy

Instead of fixed-size chunks:
- Analyzes document structure
- Creates semantically meaningful sections
- Preserves context boundaries
- Adapts chunk size to content type

---

## Advanced RAG Techniques

### Contextual Retrieval

**Source:** https://github.com/coleam00/mcp-crawl4ai-rag

Enhances basic embeddings with contextual information.

#### Implementation

1. **Contextual Embeddings**
   - Add document-level context to each chunk
   - Include metadata about chunk position
   - Preserve relationship to parent document

2. **Late Chunking**
   - Delay chunking until after embedding generation
   - Allows model to see full context before splitting
   - Improves semantic coherence

### Semantic Chunking

**Used in:** Docling RAG Agent and Knowledge Graph RAG

Instead of character-based splitting:

```python
# Semantic Chunking Process:
1. Analyze document structure (headings, paragraphs, sections)
2. Identify semantic boundaries
3. Create chunks that preserve meaning
4. Maintain relationships between chunks
```

#### Benefits

- Preserves logical structure
- Maintains context within chunks
- Improves retrieval relevance
- Better handles complex documents

### Hybrid Search

Combines multiple search strategies:

1. **Vector Search:** Semantic similarity
2. **Keyword Search:** Exact term matching
3. **Graph Traversal:** Relationship-based discovery

---

## Knowledge Graph Integration

### Agentic RAG with Knowledge Graph

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/agentic-rag-knowledge-graph

Combines traditional RAG (vector search) with knowledge graph capabilities.

#### Architecture

- **Vector Database:** PostgreSQL with pgvector (semantic search)
- **Knowledge Graph:** Neo4j with Graphiti (relationship mapping)
- **Temporal Intelligence:** Tracks how facts change over time

#### Why Knowledge Graphs?

Traditional vector search limitations:
- No explicit relationship tracking
- Difficult to answer "how are X and Y related?"
- Cannot traverse multi-hop connections
- Limited temporal understanding

Knowledge graphs solve this by:
- Storing explicit entity relationships
- Enabling graph traversal queries
- Tracking temporal changes
- Supporting complex reasoning

#### Implementation Components

```
System Architecture:
┌─────────────────┐     ┌──────────────────┐
│   Vector DB     │     │  Knowledge Graph │
│   (pgvector)    │     │    (Neo4j +      │
│                 │     │    Graphiti)     │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         └───────┬───────────────┘
                 │
         ┌───────▼────────┐
         │   AI Agent     │
         │  (Pydantic AI) │
         └────────────────┘
```

#### Tools Available

1. **vector_search:** Semantic similarity search
2. **graph_search:** Relationship-based queries
3. **hybrid_search:** Combines vector + graph
4. **get_entity_relationships:** Traverse connections

#### Example Usage

```
User: "What are Microsoft's AI initiatives?"
Tools Used:
1. vector_search(query='Microsoft AI initiatives', limit=10)
2. graph_search(query='Microsoft AI projects')

User: "How is Microsoft connected to OpenAI?"
Tools Used:
1. hybrid_search(query='Microsoft OpenAI partnership', limit=10)
2. get_entity_relationships(entity='Microsoft')
```

#### Ingestion Process

```bash
# Basic ingestion with semantic chunking
python -m ingestion.ingest

# Clean existing data and re-ingest
python -m ingestion.ingest --clean

# Custom settings (no knowledge graph for faster processing)
python -m ingestion.ingest --chunk-size 800 --no-semantic --verbose
```

**⚠️ Warning:** Knowledge graph creation is computationally expensive. Processing 21 documents can take 30+ minutes due to entity extraction and relationship building.

### n8n Knowledge Graph RAG

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/n8n_knowledge_graph_rag

n8n implementation combining RAG + Knowledge Graph.

**Requirements:**
- Self-hosted n8n
- Community MCP node installed
- PostgreSQL with pgvector
- Neo4j with Graphiti

---

## Multi-Format Document Processing

### Docling RAG Agent

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/docling-rag-agent

Comprehensive document processing with multiple format support.

#### Supported Formats

- **Text Documents:** TXT, MD, DOC, DOCX
- **PDFs:** Extracted and parsed
- **Spreadsheets:** CSV, XLSX with table preservation
- **Audio Files:** Automatic transcription with OpenAI Whisper Turbo

#### Audio Transcription Feature

```
Audio Processing:
1. Upload audio file (MP3, WAV, etc.)
2. Whisper Turbo transcribes with timestamps
3. Transcript stored as searchable text
4. Timestamps preserved for reference

Example Output:
[time: 0.0-4.0] Welcome to our podcast on AI
[time: 5.28-9.96] Today we'll discuss RAG systems
```

#### Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  CLI User   │───▶│   RAG Agent  │───▶│ PostgreSQL  │
│   (Input)   │    │ (PydanticAI) │    │  PGVector   │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼────┐  ┌────▼─────┐
              │ OpenAI   │  │ OpenAI   │
              │   LLM    │  │Embeddings│
              └──────────┘  └──────────┘
```

#### Ingestion Commands

```bash
# Ingest all documents in folder
uv run python -m ingestion.ingest --documents documents/

# Adjust chunk size
uv run python -m ingestion.ingest --documents documents/ --chunk-size 800

# Custom settings
uv run python -m ingestion.ingest --documents documents/ --chunk-size 1200 --verbose
```

**⚠️ Important:** Default ingestion clears existing database before adding new documents.

#### Learning Path

The repository includes progressive tutorials in `docling_basics/`:
1. Basic document processing
2. Chunk creation and embedding
3. Vector storage
4. Retrieval implementation
5. Full RAG agent integration

---

## Production Best Practices

### Database Configuration

#### PostgreSQL Connection

**Critical:** Use transaction pooler method for Supabase

```
Wrong: Direct connection
Right: Transaction pooler

Connection String Format:
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

This prevents connection exhaustion and improves performance.

#### Required Tables

1. **documents table**
   - Stores chunked text with embeddings
   - Columns: id, content, embedding, metadata

2. **document_metadata table**
   - Tracks document information
   - Columns: file_id, file_title, file_type, created_at, schema

3. **document_rows table** (for tabular data)
   - Stores CSV/Excel data for SQL queries
   - Schema matches source file structure

### Embeddings Strategy

#### Model Selection

- **Production:** OpenAI `text-embedding-3-small` or `text-embedding-3-large`
- **Local/Private:** Ollama models (nomic-embed-text, all-minilm)
- **Cost-Effective:** Hugging Face embeddings

#### Chunking Parameters

```python
# Recommended defaults:
chunk_size = 1000  # characters
chunk_overlap = 200  # characters

# For technical docs:
chunk_size = 800
chunk_overlap = 150

# For narrative content:
chunk_size = 1500
chunk_overlap = 300
```

### Agent Prompting

#### System Prompt Template

```
You are a knowledge assistant with access to a vector database containing {document_types}.

Available Tools:
- rag_search: Semantic search through document chunks
- list_documents: View all available documents
- get_full_document: Retrieve complete document text
- sql_query: Query tabular data (for CSV/Excel files)

Strategy:
1. For text-based questions → Use rag_search
2. For numerical calculations → Use sql_query
3. For comprehensive context → List documents first, then retrieve full text
4. If uncertain about document availability → List documents

Always:
- Tell the user if you didn't find the answer
- Cite your sources with file names
- Explain which tool you used and why
```

### Error Handling

#### Common Issues

1. **Empty Results**
   ```python
   if not results:
       # Try broader search or alternative tool
       # Inform user about lack of information
   ```

2. **Vector Search Failures**
   ```python
   # Fallback strategies:
   - Reduce similarity threshold
   - Expand search to more results
   - Try keyword-based search
   - Query document metadata
   ```

3. **SQL Query Errors**
   ```python
   # Validate before execution:
   - Check table exists
   - Verify column names
   - Handle NULL values
   - Limit result size
   ```

---

## R1 Distill RAG Strategy

**Repository:** https://github.com/coleam00/ottomator-agents/tree/main/r1-distill-rag

### Concept: Two-Stage RAG with Reasoning

This strategy uses a specialized reasoning model to improve RAG quality.

#### Architecture

```python
# Stage 1: Vector retrieval
docs = vectordb.similarity_search(user_query, k=3)
context = "\n\n".join(doc.page_content for doc in docs)

# Stage 2: Reasoning model processes context
prompt = f"""Based on the following context, answer the question.
Be concise and specific.
If insufficient information, suggest a better query.

Context: {context}
Question: {user_query}
Answer:"""

response = reasoner.run(prompt, reset=False)
```

#### Benefits

- **Improved Accuracy:** Reasoning model analyzes context before answering
- **Query Refinement:** Suggests better queries when information insufficient
- **Cost Optimization:** Uses different models for different tasks

#### Implementation with Smolagents

```python
from smolagents import OpenAIServerModel, CodeAgent, ToolCallingAgent

# Primary agent directs conversation
tool_model = get_model(tool_model_id)
primary_agent = ToolCallingAgent(
    tools=[rag_with_reasoner],
    model=tool_model,
    add_base_tools=False,
    max_steps=3
)

# Reasoning agent processes RAG results
reasoning_model = get_model(reasoning_model_id)
reasoner = CodeAgent(
    tools=[],
    model=reasoning_model,
    add_base_tools=False,
    max_steps=2
)
```

---

## Web Crawling RAG

### MCP Crawl4AI RAG

**Repository:** https://github.com/coleam00/mcp-crawl4ai-rag

Integrates web crawling with RAG for dynamic knowledge bases.

#### Features

- **Smart URL Detection:** Handles webpages, sitemaps, text files
- **Recursive Crawling:** Follows internal links automatically
- **Content Processing:** Converts to markdown for storage
- **Vector Storage:** Indexes crawled content in Supabase

#### Advanced Strategies Available

1. **Contextual Retrieval**
   - Enriches chunks with document context
   - Improves semantic understanding

2. **Late Chunking**
   - Delays chunking until after initial processing
   - Preserves more context

3. **Enhanced Chunking (Context 7-inspired)**
   - Focuses on examples
   - Creates semantically meaningful sections
   - Improves retrieval precision

#### Configuration

```python
# Enable advanced strategies
config = {
    'contextual_embeddings': True,
    'late_chunking': True,
    'enhanced_chunking': True
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **Setup Infrastructure**
   - [ ] PostgreSQL with pgvector
   - [ ] Embedding model (OpenAI or local)
   - [ ] Basic document storage

2. **Implement Basic RAG**
   - [ ] Document ingestion pipeline
   - [ ] Text chunking (fixed-size)
   - [ ] Vector storage
   - [ ] Simple semantic search
   - [ ] Basic LLM integration

3. **Testing**
   - [ ] Test with 10-20 sample documents
   - [ ] Measure retrieval accuracy
   - [ ] Benchmark response time

### Phase 2: Agentic Enhancement (Week 3-4)

1. **Add Multiple Tools**
   - [ ] Document listing tool
   - [ ] Full document retrieval
   - [ ] SQL query tool (for tabular data)

2. **Implement Agent Logic**
   - [ ] Tool selection based on query type
   - [ ] Multi-step reasoning
   - [ ] Fallback strategies

3. **Testing**
   - [ ] Test tool selection accuracy
   - [ ] Verify cross-document connections
   - [ ] Measure improvement over basic RAG

### Phase 3: Advanced Techniques (Week 5-6)

1. **Reranking**
   - [ ] Implement post-retrieval reranking
   - [ ] Test different reranking models
   - [ ] Measure quality improvement

2. **Semantic Chunking**
   - [ ] Replace fixed-size chunking
   - [ ] Implement structure-aware splitting
   - [ ] Preserve context boundaries

3. **Contextual Retrieval**
   - [ ] Add document-level context to chunks
   - [ ] Implement late chunking
   - [ ] Test improvement

### Phase 4: Knowledge Graph (Week 7-8)

1. **Graph Setup**
   - [ ] Deploy Neo4j with Graphiti
   - [ ] Configure entity extraction
   - [ ] Setup relationship mapping

2. **Hybrid Search**
   - [ ] Implement vector + graph search
   - [ ] Create graph traversal queries
   - [ ] Add temporal tracking

3. **Testing**
   - [ ] Test relationship queries
   - [ ] Measure graph traversal performance
   - [ ] Verify temporal accuracy

### Phase 5: Production Hardening (Week 9-10)

1. **Monitoring**
   - [ ] Add logging
   - [ ] Track query performance
   - [ ] Monitor error rates

2. **Optimization**
   - [ ] Cache frequent queries
   - [ ] Optimize embedding generation
   - [ ] Improve database queries

3. **Documentation**
   - [ ] API documentation
   - [ ] User guides
   - [ ] Troubleshooting guides

---

## Troubleshooting Guide

### Issue: Poor Retrieval Quality

**Symptoms:**
- Irrelevant results returned
- Missing obvious relevant documents
- Low confidence scores

**Solutions:**

1. **Adjust Chunk Size**
   ```python
   # Try different sizes:
   chunk_size = 500  # Smaller for specific queries
   chunk_size = 1500  # Larger for context-heavy queries
   ```

2. **Increase Retrieved Results**
   ```python
   # Retrieve more candidates
   results = vectordb.similarity_search(query, k=10)  # Instead of k=5
   ```

3. **Implement Reranking**
   - Post-process vector search results
   - Use cross-encoder model to rerank

4. **Try Hybrid Search**
   - Combine vector search with keyword search
   - Merge and deduplicate results

### Issue: Slow Response Time

**Symptoms:**
- Long wait for results
- Timeout errors
- Poor user experience

**Solutions:**

1. **Optimize Embeddings**
   ```python
   # Use smaller embedding model
   model = "text-embedding-3-small"  # Instead of large
   
   # Batch embed documents
   embeddings = embed_batch(documents, batch_size=100)
   ```

2. **Add Caching**
   ```python
   # Cache frequent queries
   @lru_cache(maxsize=1000)
   def cached_search(query: str):
       return vectordb.similarity_search(query)
   ```

3. **Database Optimization**
   ```sql
   -- Add indexes
   CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
   
   -- Use connection pooling
   -- Increase pool size for high traffic
   ```

4. **Async Operations**
   ```python
   # Use async for concurrent operations
   async def search_multiple_sources(queries):
       tasks = [search_async(q) for q in queries]
       results = await asyncio.gather(*tasks)
       return results
   ```

### Issue: Knowledge Graph Too Slow

**Symptoms:**
- Entity extraction takes 30+ minutes
- Graph queries timeout
- High computational costs

**Solutions:**

1. **Disable for Initial Testing**
   ```bash
   python -m ingestion.ingest --no-semantic --verbose
   ```

2. **Reduce Document Size**
   - Process fewer documents initially
   - Split large documents
   - Filter unnecessary content

3. **Optimize Entity Extraction**
   ```python
   # Use faster LLM for entity extraction
   # Or reduce entity types extracted
   entity_types = ['PERSON', 'ORG']  # Instead of all types
   ```

4. **Incremental Processing**
   ```python
   # Process documents in batches
   for batch in document_batches:
       process_and_store(batch)
       # Allow other queries between batches
   ```

### Issue: SQL Queries Failing

**Symptoms:**
- SQL tool returns errors
- Table not found
- Column mismatch

**Solutions:**

1. **Validate Table Structure**
   ```python
   # Before executing SQL
   def validate_table(table_name):
       tables = get_available_tables()
       if table_name not in tables:
           return f"Table {table_name} not found"
       return get_table_schema(table_name)
   ```

2. **Dynamic Schema Detection**
   ```python
   # Agent learns table structure
   schema = get_table_schema('document_rows')
   prompt = f"Available columns: {schema}\nGenerate SQL for: {query}"
   ```

3. **Error Recovery**
   ```python
   try:
       results = execute_sql(query)
   except Exception as e:
       # Try alternative approach
       return rag_search(original_question)
   ```

### Issue: Out of Memory

**Symptoms:**
- Process crashes during ingestion
- OOM errors
- System freeze

**Solutions:**

1. **Batch Processing**
   ```python
   # Process documents in batches
   batch_size = 10
   for i in range(0, len(documents), batch_size):
       batch = documents[i:i+batch_size]
       process_batch(batch)
       # Clear memory
       del batch
       gc.collect()
   ```

2. **Reduce Embedding Dimensions**
   ```python
   # Use smaller embedding model
   # Or reduce dimensions with PCA
   from sklearn.decomposition import PCA
   pca = PCA(n_components=512)  # Reduce from 1536
   reduced_embeddings = pca.fit_transform(embeddings)
   ```

3. **Stream Processing**
   ```python
   # Don't load all documents at once
   for doc_path in document_paths:
       doc = load_single_document(doc_path)
       process_and_store(doc)
       del doc
   ```

---

## Resource Links

### Official Repositories

- **Main Repository:** https://github.com/coleam00/ottomator-agents
- **All RAG Strategies:** https://github.com/coleam00/ottomator-agents/tree/main/all-rag-strategies
- **Foundational RAG:** https://github.com/coleam00/ottomator-agents/tree/main/foundational-rag-agent
- **n8n Agentic RAG:** https://github.com/coleam00/ottomator-agents/tree/main/n8n-agentic-rag-agent
- **Ultimate n8n RAG:** https://github.com/coleam00/ottomator-agents/tree/main/ultimate-n8n-rag-agent
- **Knowledge Graph RAG (Python):** https://github.com/coleam00/ottomator-agents/tree/main/agentic-rag-knowledge-graph
- **Knowledge Graph RAG (n8n):** https://github.com/coleam00/ottomator-agents/tree/main/n8n_knowledge_graph_rag
- **Docling RAG:** https://github.com/coleam00/ottomator-agents/tree/main/docling-rag-agent
- **R1 Distill RAG:** https://github.com/coleam00/ottomator-agents/tree/main/r1-distill-rag
- **MCP Crawl4AI RAG:** https://github.com/coleam00/mcp-crawl4ai-rag

### Educational Resources

- **Cole Medin's YouTube Channel:** Search for "Cole Medin RAG" for video tutorials
- **oTTomator Live Agent Studio:** https://ottomator.ai (platform for testing agents)
- **n8n Community:** https://community.n8n.io (for n8n-specific questions)
- **Pydantic AI Documentation:** https://ai.pydantic.dev
- **LangChain Documentation:** https://python.langchain.com

### Tools and Frameworks

- **n8n:** https://n8n.io (workflow automation)
- **Supabase:** https://supabase.com (PostgreSQL + pgvector)
- **Neon:** https://neon.tech (serverless PostgreSQL)
- **Neo4j:** https://neo4j.com (knowledge graph database)
- **Graphiti:** Entity and relationship extraction
- **Ollama:** https://ollama.ai (local LLM hosting)
- **Crawl4AI:** Web crawling and content extraction

### Embedding Models

- **OpenAI Embeddings:** text-embedding-3-small, text-embedding-3-large
- **Sentence Transformers:** all-MiniLM-L6-v2, all-mpnet-base-v2
- **Cohere Embeddings:** embed-english-v3.0
- **Voyage AI:** voyage-2, voyage-code-2

### Reranking Models

- **Cohere Rerank:** rerank-english-v2.0
- **Cross-Encoders:** ms-marco-MiniLM-L-6-v2
- **BGE Reranker:** BAAI/bge-reranker-base

---

## Quick Start Commands

### Basic RAG Setup

```bash
# Clone repository
git clone https://github.com/coleam00/ottomator-agents.git
cd ottomator-agents/foundational-rag-agent

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys and database credentials

# Run ingestion
python -m ingestion.ingest --documents ./documents

# Start agent
python -m ui.app
```

### n8n Agentic RAG

```bash
# Import workflow JSON into n8n
# Configure credentials for:
# - OpenAI API
# - Supabase/PostgreSQL
# - LangChain nodes

# Setup database tables
# Run SQL scripts provided in repository

# Test workflow
# Upload documents via n8n interface
```

### Knowledge Graph RAG

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure databases
# Edit .env for PostgreSQL and Neo4j

# Run ingestion (this takes time!)
python -m ingestion.ingest --clean

# Start agent
python -m agent.cli
```

---

## Performance Benchmarks

### Expected Response Times

| Strategy | Setup Time | Query Time | Ingestion (100 docs) |
|----------|-----------|------------|---------------------|
| Basic RAG | 5 min | 1-2 sec | 5-10 min |
| Agentic RAG | 15 min | 2-4 sec | 10-15 min |
| + Reranking | 20 min | 3-5 sec | 15-20 min |
| + Knowledge Graph | 1 hour | 4-8 sec | 30-60 min |
| Full Stack | 2 hours | 5-10 sec | 60-120 min |

### Accuracy Improvements

| Strategy | Retrieval Accuracy | Answer Quality |
|----------|-------------------|----------------|
| Baseline (no RAG) | N/A | 60% |
| Basic RAG | 70% | 75% |
| Semantic Chunking | 75% | 80% |
| + Reranking | 80% | 85% |
| Agentic RAG | 85% | 90% |
| + Knowledge Graph | 90% | 95% |

*Note: These are approximate values based on typical implementations. Actual results vary by use case.*

---

## Advanced Configuration

### Embedding Model Comparison

```python
# OpenAI (best quality, paid)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Sentence Transformers (good quality, free)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# Ollama (local, private)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
```

### Chunking Strategies

```python
# Fixed-size chunking (simple)
from langchain.text_splitter import CharacterTextSplitter
splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Recursive chunking (better for code)
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

# Semantic chunking (best quality)
# Use LLM to determine boundaries
# See Docling RAG implementation
```

### Vector Store Selection

```python
# Supabase (managed PostgreSQL)
vectorstore = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="documents"
)

# Pinecone (managed vector DB)
vectorstore = Pinecone.from_documents(
    documents,
    embeddings,
    index_name="rag-index"
)

# Chroma (local, good for development)
vectorstore = Chroma.from_documents(
    documents,
    embeddings,
    persist_directory="./chroma_db"
)

# Qdrant (self-hosted or cloud)
vectorstore = Qdrant.from_documents(
    documents,
    embeddings,
    url="http://localhost:6333",
    collection_name="rag_collection"
)
```

---

## Testing and Evaluation

### RAG Quality Metrics

```python
# Key metrics to track:
1. Retrieval Precision: Are retrieved chunks relevant?
2. Retrieval Recall: Are all relevant chunks retrieved?
3. Answer Correctness: Is the final answer correct?
4. Answer Completeness: Does answer cover all aspects?
5. Latency: Response time
6. Cost: API calls and compute
```

### Evaluation Dataset

Create test questions covering:
- Simple fact lookup
- Multi-document synthesis
- Numerical calculations
- Temporal queries
- Relationship queries
- Ambiguous questions

### Automated Testing

```python
# Example test suite
def test_rag_system():
    test_cases = [
        {
            "question": "What is X?",
            "expected_sources": ["doc1.pdf"],
            "expected_answer_contains": ["key phrase"]
        },
        # Add more test cases
    ]
    
    for test in test_cases:
        result = rag_agent.query(test["question"])
        assert_sources_used(result, test["expected_sources"])
        assert_answer_quality(result, test["expected_answer_contains"])
```

---

## Cost Optimization

### Embedding Cost Reduction

```python
# Strategy 1: Use smaller models
# OpenAI text-embedding-3-small vs text-embedding-3-large
# ~5x cheaper, minimal quality loss for most use cases

# Strategy 2: Reduce embedding dimensions
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=512  # Instead of default 3072
)

# Strategy 3: Use local models
# Completely free, but requires GPU
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)
```

### LLM Cost Reduction

```python
# Strategy 1: Use smaller models for tool calling
# GPT-4-turbo for reasoning, GPT-3.5-turbo for tool selection

# Strategy 2: Implement caching
from langchain.cache import SQLiteCache
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

# Strategy 3: Reduce max_tokens
llm = ChatOpenAI(max_tokens=500)  # Instead of 2000

# Strategy 4: Use local models
llm = Ollama(model="llama2:13b")  # Free, private
```

---

## Security Considerations

### API Key Management

```python
# Use environment variables
import os
from dotenv import load_load_env()

openai_key = os.getenv("OPENAI_API_KEY")

# Never hardcode keys
# ❌ Bad: openai_key = "sk-..."
# ✅ Good: openai_key = os.getenv("OPENAI_API_KEY")
```

### Data Privacy

```python
# For sensitive data, use local models
embeddings = HuggingFaceEmbeddings(
    model_name="all-mpnet-base-v2"
)
llm = Ollama(model="llama2")

# Or use on-premise deployments
# Azure OpenAI, AWS Bedrock with private endpoints
```

### SQL Injection Prevention

```python
# Always use parameterized queries
# ❌ Bad: f"SELECT * FROM docs WHERE id = {user_input}"
# ✅ Good: Use prepared statements

from psycopg2 import sql
query = sql.SQL("SELECT * FROM docs WHERE id = %s")
cursor.execute(query, (user_input,))
```

---

## Monitoring and Observability

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Query received: {query}")
logger.info(f"Retrieved {len(results)} documents")
logger.warning(f"Low confidence score: {score}")
```

### Metrics Tracking

```python
# Track key metrics
from prometheus_client import Counter, Histogram

query_counter = Counter('rag_queries_total', 'Total queries')
query_latency = Histogram('rag_query_latency_seconds', 'Query latency')

@query_latency.time()
def process_query(query):
    query_counter.inc()
    return rag_agent.query(query)
```

---

## Future Enhancements

### Roadmap from Cole Medin

1. **Integration with Archon**
   - Building RAG directly into Archon
   - Comprehensive knowledge engine for AI coding assistants

2. **Multiple Embedding Models**
   - Support for various embedding providers
   - Local models with Ollama
   - Complete privacy and control

3. **Enhanced Chunking**
   - Context 7-inspired approach
   - Focus on examples
   - Semantic sections

4. **Performance Optimization**
   - Faster crawling and indexing
   - Quick documentation indexing
   - Real-time knowledge updates

5. **Smart URL Detection**
   - Better handling of different URL types
   - Improved sitemap processing
   - Enhanced content extraction

---

## Conclusion

This guide provides a comprehensive overview of RAG strategies from Cole Medin's ottomator-agents repository. As an AI agent implementing these strategies:

1. **Start Simple:** Begin with foundational RAG, test thoroughly
2. **Add Complexity Gradually:** Implement agentic features when basic RAG is solid
3. **Measure Everything:** Track metrics before and after each enhancement
4. **Focus on User Needs:** Choose strategies based on your specific use case
5. **Iterate Quickly:** Test, learn, improve continuously

Remember: The best RAG system is the one that solves your specific problem effectively. Not every strategy is needed for every use case.

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Maintainer:** AI Agent implementing RAG strategies  
**Source:** https://github.com/coleam00/ottomator-agents

For questions, issues, or contributions, refer to the original repository or Cole Medin's YouTube channel for the latest updates and community support.

---

## Quick Reference Card

### When to Use Each Strategy

| Use Case | Recommended Strategy | Why |
|----------|---------------------|-----|
| Simple Q&A | Basic RAG | Fast, cost-effective, sufficient |
| Technical Docs | Semantic Chunking | Preserves code structure |
| Mixed Content | Agentic RAG | Handles different query types |
| Relationship Queries | Knowledge Graph | Explicit connections |
| Audio Content | Docling RAG | Whisper transcription |
| Web Content | Crawl4AI RAG | Dynamic updates |
| Privacy Concerns | Local Models | Complete data control |
| High Accuracy Needs | Reranking + KG | Maximum quality |

### Command Cheat Sheet

```bash
# Quick setup
git clone https://github.com/coleam00/ottomator-agents.git
cd ottomator-agents/[strategy-folder]
pip install -r requirements.txt
cp .env.example .env

# Ingestion
python -m ingestion.ingest --documents ./docs
python -m ingestion.ingest --clean  # Clear first
python -m ingestion.ingest --chunk-size 800

# Testing
python -m pytest tests/
python -m agent.cli  # Interactive mode

# Monitoring
tail -f logs/rag.log
```

---

**End of Guide**
