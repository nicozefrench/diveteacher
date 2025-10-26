# Application Goal - DiveTeacher RAG Knowledge Graph System

**Project Type:** SaaS Platform for Dive Training with RAG + Knowledge Graph  
**Target Users:** Dive Instructors, Students, Dive Centers  
**Target Deployment:** Vercel (Frontend) + DigitalOcean GPU (Backend)  
**LLM Provider:** Mistral 7B-instruct-Q5_K_M (local on GPU) - Agnostic architecture  
**Organizations:** FFESSM (France) + SSI (International) - V1

---

## 🎯 Primary Objective

Build a **production-ready SaaS application** that allows dive instructors, students, and dive centers to:
1. **Access** comprehensive knowledge from official FFESSM and SSI dive training materials
2. **Upload** dive training documents (MFT FFESSM, SSI manuals, safety procedures, theory documents)
3. **Process** documents automatically using Dockling (PDF/PPT → Markdown conversion)
4. **Ingest** processed content into a Neo4j Knowledge Graph using Graphiti
5. **Query** the knowledge base in French or English using natural language via an LLM-powered RAG system
6. **Stream** precise responses in real-time with exact citations from source documents
7. **Manage** conversations history for continuous learning and review
8. **Visualize** (Admin) the knowledge graph to understand relationships between certifications, procedures, and concepts

### Value Proposition
> **"Master scuba diving with AI - Instant access to FFESSM & SSI knowledge, precise answers to all your dive training questions, backed by official documentation."**

---

## 🔑 Key Features

### **1. Document Processing Pipeline**
- **Upload:** Drag & drop PDF/PPT files via React UI
- **Storage:** Original files stored on DigitalOcean (persistent volume)
- **Processing:** Dockling converts documents to markdown
- **Ingestion:** Graphiti builds knowledge graph in Neo4j
- **Status:** Real-time upload progress and processing status

### **2. Knowledge Graph**
- **Database:** Neo4j 5.x with APOC and Graph Data Science plugins
- **Schema:** Graphiti-managed entity and relationship extraction
- **Context:** Maintains document provenance and metadata
- **Query:** Cypher-based retrieval for RAG context

### **3. RAG System**
- **Retrieval:** Query Neo4j knowledge graph for relevant context
- **Augmentation:** Inject retrieved context into LLM prompt
- **Generation:** LLM generates response based on retrieved knowledge only
- **Grounding:** Responses strictly based on ingested documents (no hallucination)

### **4. LLM Integration (Agnostic)**
- **Primary:** Ollama (local models: llama3, mistral, mixtral)
- **Alternative:** Claude, OpenAI (API-based, configurable via env)
- **Abstraction:** Unified interface for switching providers
- **Streaming:** Real-time token streaming for better UX

### **5. Modern Web Interface**
- **Frontend:** React 18 + Vite + TailwindCSS + shadcn/ui
- **Upload UI:** Drag & drop, multi-file support, progress bars
- **Chat UI:** Streaming responses, markdown rendering, code highlighting
- **Responsive:** Mobile-first design, dark/light mode
- **Deployment:** Vercel (free tier, CDN, auto-deploy from GitHub)

### **6. Monitoring & Observability**
- **Error Tracking:** Sentry integration (backend + frontend)
- **Logging:** Structured logs with correlation IDs
- **Metrics:** Document processing stats, query performance
- **Health Checks:** API endpoints, database connectivity

---

## 🏗️ Technical Architecture

### **Frontend (Vercel)**
```
React + Vite
├── shadcn/ui components (modern UI primitives)
├── TailwindCSS (utility-first styling)
├── React Query (state management)
├── SSE / WebSocket (streaming responses)
└── File upload (multipart/form-data)
```

### **Backend (DigitalOcean Droplet)**
```
FastAPI + Docker Compose
├── FastAPI (Python web framework)
│   ├── /upload - Document upload endpoint
│   ├── /query - RAG query endpoint (streaming)
│   ├── /status - Processing status
│   └── /health - Health check
│
├── Neo4j 5.x (Knowledge Graph)
│   ├── APOC plugin (advanced queries)
│   └── GDS plugin (graph algorithms)
│
├── Ollama (LLM Server)
│   ├── llama3:8b (default model)
│   └── Custom models (configurable)
│
└── Dockling + Graphiti (Processing pipeline)
    ├── PDF/PPT → Markdown
    └── Markdown → Neo4j KG
```

---

## 🌐 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  VERCEL (Frontend)                      │
│  - React app (static build)             │
│  - Global CDN                           │
│  - HTTPS automatic                      │
│  - Environment: VITE_API_URL            │
└──────────────┬──────────────────────────┘
               │ HTTPS API calls
               ▼
┌─────────────────────────────────────────┐
│  DIGITALOCEAN (Backend)                 │
│  - Docker Compose                       │
│  - Nginx reverse proxy (SSL)            │
│  - Persistent volumes:                  │
│    • /uploads (original files)          │
│    • /neo4j-data (graph database)       │
│    • /ollama-models (LLM models)        │
└─────────────────────────────────────────┘
```

---

## 🎨 User Experience Flow

### **1. Document Upload**
```
User uploads PDF/PPT → Frontend
  ↓
Multipart upload → Backend /upload endpoint
  ↓
Save to /uploads volume → Return upload_id
  ↓
Background processing starts
  ↓
Dockling: PDF → Markdown
  ↓
Graphiti: Markdown → Neo4j Knowledge Graph
  ↓
Status: "completed" (WebSocket notification)
```

### **2. Knowledge Query**
```
User types question → Frontend
  ↓
POST /query (streaming) → Backend
  ↓
Query Neo4j (retrieve relevant context)
  ↓
Build RAG prompt (context + question)
  ↓
Stream LLM response → Frontend (SSE)
  ↓
Display streaming answer (token by token)
```

---

## 🔐 Security & Configuration

### **Environment Variables (All services)**
```bash
# LLM Configuration
LLM_PROVIDER=ollama           # ollama, claude, openai
OLLAMA_MODEL=llama3:8b
OLLAMA_BASE_URL=http://ollama:11434

# Optional: External LLM APIs
ANTHROPIC_API_KEY=sk-ant-...  # If using Claude
OPENAI_API_KEY=sk-...         # If using OpenAI

# Neo4j Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_password_here

# Graphiti
GRAPHITI_ENABLED=true

# Monitoring (Sentry)
SENTRY_DSN_BACKEND=https://...@sentry.io/...
SENTRY_DSN_FRONTEND=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production  # or development
SENTRY_TRACES_SAMPLE_RATE=1.0

# Backend API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-app.vercel.app

# Frontend (Vercel)
VITE_API_URL=https://api.your-domain.com
VITE_SENTRY_DSN=https://...@sentry.io/...
```

---

## 📊 Success Metrics

### **Functionality**
- ✅ Upload PDF/PPT → Processed → Ingested (end-to-end)
- ✅ Query returns accurate answers from uploaded documents
- ✅ Streaming responses work smoothly (no lag)
- ✅ No hallucinations (answers only from knowledge graph)

### **Performance**
- ⚡ Document processing: < 30s per document
- ⚡ Query latency: < 2s to first token
- ⚡ Streaming: Smooth token delivery (30-50 tokens/s)

### **Reliability**
- 🛡️ Error tracking (Sentry captures all errors)
- 🛡️ Health checks (backend, Neo4j, Ollama)
- 🛡️ Graceful degradation (fallback to status messages)

### **Usability**
- 🎨 Modern UI (shadcn/ui components)
- 🎨 Responsive design (mobile + desktop)
- 🎨 Real-time feedback (upload progress, processing status)

---

## 🚀 Getting Started (Quick)

### **Local Development (5 min)**
```bash
# 1. Clone boilerplate
git clone <repo>
cd rag-kg-boilerplate

# 2. Configure environment
cp .env.template .env
# Edit .env with your settings

# 3. Start all services
docker-compose -f docker/docker-compose.dev.yml up -d

# 4. Pull Ollama model (first time)
docker exec rag-ollama ollama pull llama3:8b

# 5. Access application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Neo4j: http://localhost:7474
```

### **Production Deployment (20 min)**
```bash
# 1. Deploy backend to DigitalOcean
ssh your-droplet
cd /opt/rag-app
docker-compose -f docker-compose.prod.yml up -d

# 2. Deploy frontend to Vercel
cd frontend
vercel --prod
# Or: Push to GitHub (auto-deploy)
```

---

## 🎯 Target Users

### **Primary Use Cases**
1. **Research:** Academic papers → Knowledge graph → Q&A
2. **Legal:** Contracts/policies → Compliance queries
3. **Business:** Reports/presentations → Executive summaries
4. **Technical:** Documentation → Developer assistance

### **Ideal For**
- Teams needing private document Q&A (no external APIs)
- Organizations with compliance requirements (data stays on-prem)
- Developers building RAG applications (boilerplate foundation)
- Researchers processing large document collections

---

## 📚 Documentation Structure

```
docs/
├── SETUP.md              # Installation guide (local + prod)
├── DEPLOYMENT.md         # DigitalOcean + Vercel deployment
├── ARCHITECTURE.md       # System design deep-dive
├── API.md                # Backend API reference
├── TROUBLESHOOTING.md    # Common issues + solutions
└── EXAMPLES.md           # Usage examples + screenshots
```

---

## 🔮 Future Enhancements (Post-MVP)

- [ ] Multi-user support (authentication)
- [ ] Document collections (organize uploads)
- [ ] Advanced search (filters, metadata)
- [ ] Export conversations (PDF, JSON)
- [ ] Knowledge graph visualization (D3.js, vis.js)
- [ ] Batch processing (upload multiple docs)
- [ ] LangChain integration (agent workflows)
- [ ] Vector search (hybrid retrieval)

---

**Status:** 🚧 **Boilerplate in development**  
**Target:** Production-ready foundation for RAG + KG applications  
**License:** MIT (open-source, reusable)

