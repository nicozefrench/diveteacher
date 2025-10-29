# 📚 DiveTeacher - Documentation Index

> **Version:** Phase 1.0 + Warm-up Refactoring COMPLETE  
> **Last Updated:** October 28, 2025, 22:00 CET  
> **Environment:** Local Development (Mac M1 Max)  
> **Status:** 🟢 Fully Operational - Ready for E2E Testing

---

## 🎯 Quick Navigation

### 🚀 Getting Started
- **[SETUP.md](SETUP.md)** - Local development setup (Phase 0 complete guide)
  - Prerequisites & installation
  - Docker services configuration
  - Neo4j setup & troubleshooting
  - Docling + HierarchicalChunker validation
  - Testing procedures

### 🏗️ Technical Architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & data flow
  - Overview & tech stack
  - Service architecture (FastAPI, Neo4j, Ollama, React)
  - Document processing pipeline
  - RAG (Retrieval-Augmented Generation) flow
  - Database schemas

### 📄 Document Processing
- **[DOCLING.md](DOCLING.md)** - Advanced document processing
  - Docling integration & configuration
  - `PdfPipelineOptions` (OCR, TableFormer)
  - `HierarchicalChunker` semantic chunking
  - Metadata extraction
  - Performance optimization
  - Common issues & solutions

### 🔗 Knowledge Graph & RAG
- **[GRAPHITI.md](GRAPHITI.md)** - Graphiti knowledge graph integration ✅ **COMPLETE**
  - Claude Haiku 4.5 configuration (production-validated)
  - AnthropicClient integration
  - Entity extraction & relation detection
  - Vector embeddings (text-embedding-3-small)
  - AsyncIO threading architecture
- **[NEO4J.md](NEO4J.md)** - Neo4j database + RAG queries
  - Neo4j setup & authentication
  - RAG indexes (fulltext, entity, hybrid)
  - Query examples
  - Performance tuning

### 🔌 API Reference
- **[API.md](API.md)** - Backend endpoints documentation ✅ **UPDATED**
  - Upload endpoints (multipart/form-data)
  - **RAG query endpoints** (streaming + non-streaming) ✅ **NEW**
  - Health & monitoring
  - Status tracking
  - Authentication (future Phase 1.1)
  - Rate limiting (future)

### 🔧 Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues & fixes
  - Neo4j authentication errors
  - Docling conversion timeouts
  - Docker port conflicts
  - Performance issues
  - Known bugs & workarounds
- **[TIMEOUT-FIX-GUIDE.md](TIMEOUT-FIX-GUIDE.md)** - Docling timeout fix (COMPLETE)
  - Problem analysis
  - 3-layer solution (timeout + warm-up + UI)
  - Refactored warm-up architecture
  - Deployment instructions

### 🔍 Monitoring & Testing ✅ NEW
- **[MONITORING.md](MONITORING.md)** - Scripts de monitoring & debugging ✅ **NEW**
  - `monitor_ingestion.sh` - Logs Graphiti temps réel
  - `monitor_ollama.sh` - Performance Ollama/Docker
  - `test_rag_query.sh` - Tests RAG query automatisés
  - `clean_neo4j.sh` - Nettoyage Neo4j complet
  - Commandes Docker utiles
  - Debugging avancé
- **[TESTING-LOG.md](TESTING-LOG.md)** - Historique complet des tests ✅ **NEW**
  - État actuel du système
  - Historique des sessions de test
  - Tests en attente (E2E pipeline)
  - Known issues & resolutions
  - Success criteria & metrics

### ☁️ Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment (Phase 9)
  - DigitalOcean GPU setup (RTX 4000 Ada)
  - **Qwen 2.5 7B Q8_0** deployment guide ✅ **NEW**
  - Ollama GPU configuration
  - Vercel frontend deployment
  - Supabase Cloud integration
  - Environment variables & secrets management
  - Monitoring & backups
- **[251028-rag-gpu-deployment-guide.md](../resources/251028-rag-gpu-deployment-guide.md)** - Complete GPU deployment reference ✅ **NEW**
  - From Local Docker (Mac M1) → DigitalOcean GPU → Modal.com
  - Qwen 2.5 7B Q8_0 setup & benchmarking
  - Cost optimization strategies
  - Performance tuning

---

## 📊 Development Status

### ✅ Phase 0 - Local Environment (COMPLETE)

| Component | Status | Documentation |
|-----------|--------|---------------|
| **Docker Compose** | ✅ Operational | [SETUP.md](SETUP.md#docker-setup) |
| **Neo4j 5.26.0** | ✅ Healthy | [NEO4J.md](NEO4J.md) |
| **Ollama (Qwen 2.5 7B Q8_0)** | ✅ Running | [SETUP.md](SETUP.md#ollama-setup) |
| **Backend (FastAPI)** | ✅ Running | [API.md](API.md) |
| **Frontend (React)** | ✅ Running | [SETUP.md](SETUP.md#frontend-setup) |

### ✅ Phase 0.7 - Docling Integration (COMPLETE)

| Feature | Status | Documentation |
|---------|--------|---------------|
| **Docling 2.5.1** | ✅ Operational | [DOCLING.md](DOCLING.md#installation) |
| **HierarchicalChunker** | ✅ Production-ready | [DOCLING.md](DOCLING.md#hierarchical-chunker) |
| **OCR + TableFormer** | ✅ ACCURATE mode | [DOCLING.md](DOCLING.md#pipeline-options) |
| **Metadata Extraction** | ✅ Fixed | [DOCLING.md](DOCLING.md#metadata) |
| **Singleton Pattern** | ✅ Implemented | [DOCLING.md](DOCLING.md#performance) |

### ✅ Phase 0.8 - Neo4j RAG (COMPLETE)

| Feature | Status | Documentation |
|---------|--------|---------------|
| **Neo4jClient Refactor** | ✅ Sync API | [NEO4J.md](NEO4J.md#client-refactor) |
| **RAG Indexes** | ✅ 3 indexes | [NEO4J.md](NEO4J.md#indexes) |
| **Hybrid Search** | ✅ Episodes + Entities | [NEO4J.md](NEO4J.md#hybrid-search) |
| **Graphiti Integration** | ✅ API calls working | [GRAPHITI.md](GRAPHITI.md) |

### ✅ Phase 0.9 - Graphiti Claude Integration (COMPLETE)

| Task | Status | Documentation |
|------|--------|---------------|
| **Claude Haiku 4.5 Config** | ✅ WORKING | [GRAPHITI.md](GRAPHITI.md#claude-config) |
| **AnthropicClient** | ✅ Production-validated | [GRAPHITI.md](GRAPHITI.md#client) |
| **AsyncIO Threading Fix** | ✅ Resolved | [Devplan/251027-ASYNC-THREADING-FIX-IMPLEMENTATION-PLAN.md](../Devplan/251027-ASYNC-THREADING-FIX-IMPLEMENTATION-PLAN.md) |
| **Test E2E: PDF → Neo4j** | ✅ Functional | [CURRENT-CONTEXT.md](../CURRENT-CONTEXT.md#session-3) |

### ✅ Phase 1.0 - RAG Query Implementation (COMPLETE) 🎉

| Task | Status | Documentation |
|------|--------|---------------|
| **Ollama Docker Config** | ✅ Optimized | [Docker Compose](../docker/docker-compose.dev.yml) |
| **Qwen 2.5 7B Q8_0** | ✅ Loaded (8.1GB) | [ENV_CONFIGURATION](../resources/251028-qwen2.5-7b-instruct-q8_0-ollama-guide.md) |
| **RAG Query API** | ✅ 3 endpoints | [API.md](API.md#rag-query-endpoints) |
| **Streaming (SSE)** | ✅ Working | [API.md](API.md#streaming) |
| **Test Scripts** | ✅ 4/4 passing | [MONITORING.md](MONITORING.md#3-🧪-test_rag_querysh) |
| **Monitoring Scripts** | ✅ 5 scripts ready | [MONITORING.md](MONITORING.md) ✅ **NEW** |
| **Documentation** | ✅ Complete | [STATUS-PHASE-1.0](../Devplan/STATUS-PHASE-1.0-COMPLETION-REPORT.md) |

**Phase 1.0 Achievement:** Full RAG pipeline operational (upload → process → query) with Qwen 2.5 7B Q8_0 for optimal RAG quality (98/100).

---

### ✅ Warm-up System Refactoring (COMPLETE) 🎉

| Task | Status | Documentation |
|------|--------|---------------|
| **Root Cause Identified** | ✅ Import errors | [STATUS-REPORT](../Devplan/251028-STATUS-REPORT-WARM-UP-ISSUE.md) |
| **Refactoring Plan** | ✅ Solution C chosen | [WARMUP-REFACTORING-PLAN](../Devplan/251028-WARMUP-REFACTORING-PLAN.md) |
| **`app/warmup.py`** | ✅ Created | Inside package (proper imports) |
| **`DoclingSingleton.warmup()`** | ✅ Implemented | Reusable method in dockling.py |
| **Docker Entrypoint** | ✅ Modified | `python3 -m app.warmup` |
| **Validation** | ✅ Tested | < 1s warm-up, no errors |
| **Documentation** | ✅ Complete | [TIMEOUT-FIX-GUIDE](TIMEOUT-FIX-GUIDE.md) |

**Warm-up Achievement:** Production-ready architecture with proper package structure, reusable warm-up method, and validated execution.

---

## 🎓 Learning Paths

### For Developers

1. **Quick Start** (30 min)
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for overview
   - Follow [SETUP.md](SETUP.md) for local setup
   - Test with sample PDF

2. **Deep Dive: Document Processing** (2 hours)
   - Study [DOCLING.md](DOCLING.md) in detail
   - Understand chunking strategies
   - Review code: `backend/app/integrations/dockling.py`

3. **Deep Dive: Knowledge Graph** (2 hours)
   - Study [NEO4J.md](NEO4J.md) in detail
   - Understand Graphiti integration
   - Review code: `backend/app/integrations/graphiti.py`

### For AI Agents (Claude/Cursor)

**Context Loading Priority:**

1. **Session Start:** 
   - `@CURRENT-CONTEXT.md` (auto-loaded via `.cursor/rules`)
   - `@docs/INDEX.md` (this file)

2. **Development Tasks:**
   - Backend: `@docs/ARCHITECTURE.md` + `@docs/API.md`
   - Docling: `@docs/DOCLING.md` + `@resources/251027-docling-guide-ai-agent.md`
   - Neo4j: `@docs/NEO4J.md`
   - Graphiti: `@docs/GRAPHITI.md` + `@resources/251020-graphiti-technical-guide.md`
   - **RAG Query:** `@Devplan/PHASE-1.0-RAG-QUERY-IMPLEMENTATION.md` (complete plan)
   - **GPU Deployment:** `@resources/251028-rag-gpu-deployment-guide.md`
   - **Monitoring:** `@docs/MONITORING.md` (scripts guide) ✅ **NEW**
   - **Testing:** `@docs/TESTING-LOG.md` (test history) ✅ **NEW**
   - **Status Reports:** `@Devplan/STATUS-PHASE-1.0-COMPLETION-REPORT.md`

3. **Troubleshooting:**
   - `@docs/TROUBLESHOOTING.md` first
   - `@docs/MONITORING.md` for debugging scripts ✅ **NEW**
   - `@docs/TESTING-LOG.md` for known issues ✅ **NEW**
   - Then specific domain doc (DOCLING.md, NEO4J.md, etc.)

---

## 📝 Documentation Standards

### File Naming
- `UPPERCASE.md` for main docs
- `lowercase-with-dashes.md` for specific guides (future)
- Clear, descriptive names

### Structure
- **H1** for title (one per file)
- **H2** for main sections
- **H3** for subsections
- Code blocks with language tags
- Emojis for visual navigation (optional)

### Cross-References
- Use relative links: `[SETUP.md](SETUP.md)`
- Link to specific sections: `[Neo4j Setup](NEO4J.md#setup)`
- Always verify links work

### Code Examples
- Include context (file path, line numbers if relevant)
- Show expected output
- Highlight key changes with comments

---

## 🔄 Update Frequency

| Document | Update Trigger |
|----------|---------------|
| `INDEX.md` | After major phase completion |
| `SETUP.md` | Environment changes, new services |
| `ARCHITECTURE.md` | Tech stack changes, new services |
| `DOCLING.md` | Docling version upgrades, new features |
| `NEO4J.md` | Neo4j changes, query updates |
| `GRAPHITI.md` | Graphiti/Anthropic config changes, LLM updates |
| `API.md` | New endpoints, parameter changes |
| `TROUBLESHOOTING.md` | New bugs discovered, solutions found |
| `DEPLOYMENT.md` | Production setup changes |
| `TIMEOUT-FIX-GUIDE.md` | Timeout issues, warm-up changes |
| `MONITORING.md` ✅ **NEW** | New scripts, monitoring tools changes |
| `TESTING-LOG.md` ✅ **NEW** | After each test run, issues, resolutions |
| `STATUS-REPORT-*.md` | After major debugging sessions or phase blockers |

---

## 🤝 Contributing

When updating documentation:

1. ✅ Update the relevant domain file (e.g., `DOCLING.md`)
2. ✅ Update `INDEX.md` if adding new sections
3. ✅ Update `CURRENT-CONTEXT.md` for session continuity
4. ✅ Verify all cross-references work
5. ✅ Test code examples if included

---

## 📞 Support

- **GitHub Issues:** [diveteacher repository](https://github.com/nicozefrench/diveteacher)
- **Email:** `contact@diveteacher.io`
- **License:** Proprietary/Commercial (see `LICENSE`)

---

**🎯 Start Here:** New to the project? Begin with [SETUP.md](SETUP.md) → [ARCHITECTURE.md](ARCHITECTURE.md)

