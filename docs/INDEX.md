# 📚 DiveTeacher - Documentation Index

> **Version:** Phase 0.9 In Progress (Graphiti Integration - BLOCKED)  
> **Last Updated:** October 27, 2025, 19:00  
> **Environment:** Local Development (Mac M1 Max)  
> **Status:** 🟡 Partially Working (~30% Phase 0.9 complete)

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
- **[GRAPHITI.md](GRAPHITI.md)** - Graphiti knowledge graph integration ⚠️ **NEW**
  - OpenAI GPT-5-nano configuration (blocked)
  - Custom LLM client implementation
  - Entity extraction & relation detection
  - Vector embeddings (text-embedding-3-small)
  - Known issues & troubleshooting
- **[NEO4J.md](NEO4J.md)** - Neo4j database + RAG queries
  - Neo4j setup & authentication
  - RAG indexes (fulltext, entity, hybrid)
  - Query examples
  - Performance tuning

### 🔌 API Reference
- **[API.md](API.md)** - Backend endpoints documentation
  - Upload endpoints
  - RAG query endpoints
  - Health & monitoring
  - Authentication (future)
  - Rate limiting (future)

### 🔧 Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues & fixes
  - Neo4j authentication errors
  - Docling conversion timeouts
  - Docker port conflicts
  - Performance issues
  - Known bugs & workarounds

### ☁️ Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment (Phase 9)
  - DigitalOcean GPU setup
  - Vercel frontend deployment
  - Supabase Cloud integration
  - Environment variables
  - Monitoring & backups

---

## 📊 Development Status

### ✅ Phase 0 - Local Environment (COMPLETE)

| Component | Status | Documentation |
|-----------|--------|---------------|
| **Docker Compose** | ✅ Operational | [SETUP.md](SETUP.md#docker-setup) |
| **Neo4j 5.25.1** | ✅ Healthy | [NEO4J.md](NEO4J.md) |
| **Ollama (Mistral)** | ✅ Running | [SETUP.md](SETUP.md#ollama-setup) |
| **Backend (FastAPI)** | ✅ Running | [API.md](API.md) |
| **Frontend (React)** | ✅ Running | [SETUP.md](SETUP.md#frontend-setup) |

### ✅ Phase 0.7 - Docling Integration (COMPLETE)

| Feature | Status | Documentation |
|---------|--------|---------------|
| **Docling 2.5.1** | ✅ Operational | [DOCLING.md](DOCLING.md#installation) |
| **HierarchicalChunker** | ✅ 436 chunks | [DOCLING.md](DOCLING.md#hierarchical-chunker) |
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

### ⚠️ Phase 0.9 - Graphiti OpenAI Integration (BLOCKED - 30%)

| Task | Status | Documentation |
|------|--------|---------------|
| **OpenAI GPT-5-nano Config** | ❌ BLOCKED | [GRAPHITI.md](GRAPHITI.md#openai-config) |
| **Custom LLM Client** | ⚠️ BUGGY | [GRAPHITI.md](GRAPHITI.md#custom-client) |
| **Vector Dimension Mismatch** | ❌ BLOCKING | [STATUS-REPORT-2025-10-27.md](../Devplan/STATUS-REPORT-2025-10-27.md#root-cause) |
| **Test E2E: PDF → Neo4j** | ❌ 0/72 chunks | [STATUS-REPORT-2025-10-27.md](../Devplan/STATUS-REPORT-2025-10-27.md#tests) |

**Current Blocker:** Vector dimension mismatch between OpenAI embeddings (1536) and Neo4j config. See [Status Report](../Devplan/STATUS-REPORT-2025-10-27.md) for detailed analysis.

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
   - **Status Report:** `@Devplan/STATUS-REPORT-2025-10-27.md` (current blockers)

3. **Troubleshooting:**
   - `@docs/TROUBLESHOOTING.md` first
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
| `GRAPHITI.md` | Graphiti/OpenAI config changes, LLM updates |
| `API.md` | New endpoints, parameter changes |
| `TROUBLESHOOTING.md` | New bugs discovered, solutions found |
| `DEPLOYMENT.md` | Production setup changes |
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

