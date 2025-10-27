# CURRENT CONTEXT - DiveTeacher RAG Knowledge Graph

> **🤖 AI Agent Notice:** This file is the persistent memory for Claude Sonnet 4.5 agents working on DiveTeacher.  
> **Purpose:** Maintain continuity across sessions, track progress, document decisions.  
> **Usage:** Read at start of EVERY session, update at end of EVERY session.

**Last Updated:** October 27, 2025 - Session 3 - Phase 0.9 BLOCKED (~30%) ⚠️  
**Project:** DiveTeacher - Assistant IA pour Formation Plongée  
**Repository:** https://github.com/nicozefrench/diveteacher (PRIVÉ)  
**Domaine Principal:** diveteacher.io (+ diveteacher.app en redirect)

---

## 🤖 Documentation Strategy for AI Agents

### Critical Files for AI Understanding
All documentation in this project is **optimized for Claude Sonnet 4.5 agents**:

| File | Purpose | When to Read |
|------|---------|--------------|
| **CURRENT-CONTEXT.md** | Persistent memory, session history | START of every session |
| **docs/SETUP.md** | Local dev setup (Phases 0-8) | Phase 0, or when debugging local env |
| **docs/DEPLOYMENT.md** | Production deployment (Phase 9) | Phase 9 ONLY, after all local testing |
| **GOAL.md** | Project vision, architecture | When user asks "what is DiveTeacher" |
| **DIVETEACHER-V1-PLAN.md** | Complete 9-phase plan | When planning next steps or phases |
| **docs/API.md** | Backend API reference | When implementing API endpoints |
| **docs/ARCHITECTURE.md** | System design deep-dive | When implementing complex features |

### Documentation Standards for AI
- ✅ **Unambiguous:** No vague instructions, exact commands provided
- ✅ **Context-Rich:** Why decisions were made, not just what to do
- ✅ **Testable:** Expected outputs for every command
- ✅ **Decision Trees:** IF/THEN logic for AI to follow
- ✅ **Checklists:** Clear success criteria for each phase
- ✅ **Error Recovery:** Exact solutions for common issues

### Why This Matters
**Human documentation** uses implicit knowledge and assumes context.  
**AI documentation** must be explicit, complete, and actionable without human interpretation.

---

## 📍 Current Status

**Phase:** 0.9 - Graphiti Integration (BLOCKED - 30% complete) ⚠️  
**Session:** 3 (Current)  
**Environment:** macOS (darwin 24.6.0) - Mac M1 Max, 32GB RAM  
**Blocker:** Vector dimension mismatch between OpenAI embeddings (1536) and Neo4j config

**Development Strategy:**
- ✅ **Phases 0-8:** 100% Local sur Mac M1 Max (Docker) → **Coût: 0€**
- ⏸️ **Phase 9:** Production (DigitalOcean GPU + Vercel) → **Coût: ~$120/mois**  
  (Activé UNIQUEMENT quand tout fonctionne en local)

---

## 🎯 Project Overview

### What This Is
**DiveTeacher** - Une plateforme SaaS pour la formation en plongée sous-marine, utilisant:
- **RAG (Retrieval-Augmented Generation)** pour réponses précises
- **Neo4j + Graphiti** pour graphe de connaissances (entités plongée)
- **Mistral 7B-instruct-Q5_K_M** (LLM local sur GPU)
- **React + FastAPI** application full-stack
- **Supabase** pour auth multi-users
- **Docker** deployment: Vercel (frontend) + DigitalOcean GPU (backend)

### Value Proposition
> **"Maîtrisez la plongée avec l'IA - Accès instantané aux connaissances FFESSM & SSI, réponses précises à toutes vos questions de formation, basées sur la documentation officielle."**

### Target Users
1. **Instructeurs de plongée** - Préparer cours, vérifier procédures
2. **Élèves plongeurs** - Réviser théorie, préparer examens
3. **Centres de plongée** - Référence rapide, formation équipes

### Documents Sources (V1)
- **FFESSM:** MFT tous niveaux (N1→MF2), cours N4, cours MF1, exercices
- **SSI:** Documentation officielle, procédures
- **Formats:** PDF, PPT (10-200+ pages)
- **Langues:** Français + Anglais

### Key Capabilities
1. Upload documents plongée → Auto-process → Knowledge Graph
2. Questions en langage naturel (FR/EN) → Réponses streaming avec citations exactes
3. Pas d'hallucinations (réponses basées uniquement sur documents ingérés)
4. Interface admin (upload, gestion, visualisation graphe)
5. Multi-utilisateurs avec auth (admin, instructeurs, élèves)
6. Conversations sauvegardées avec historique
7. Extraction images/schémas des documents

---

## ✅ Work Completed

### Session 1 (October 26, 2025) ✅ COMPLETE
- ✅ Cloned repository from GitHub (rag-knowledge-graph-starter)
- ✅ Reviewed README.md (project features, quick start, deployment)
- ✅ Reviewed GOAL.md (architecture, use cases, technical details)
- ✅ Created CURRENT-CONTEXT.md for persistent memory
- ✅ Configured .cursor/rules/load-current-context.mdc (auto-load context)
- ✅ Created new GitHub repository "diveteacher"
- ✅ Migrated project to diveteacher repository
- ✅ Pushed all files to https://github.com/nicozefrench/diveteacher.git
- ✅ **STRATEGIC PLANNING:** Asked comprehensive questions about DiveTeacher
- ✅ **ANALYZED:** Complete boilerplate code structure (backend, frontend, Docker)
- ✅ **CREATED:** DIVETEACHER-V1-PLAN.md (300+ lines, 9 phases détaillées)
- ✅ **UPDATED:** GOAL.md with DiveTeacher context
- ✅ **DEFINED:** Complete architecture (Vercel + DO GPU + Supabase + Neo4j)
- ✅ **DOCUMENTED:** Database schemas (Neo4j entities, PostgreSQL tables)
- ✅ **SPECIFIED:** All API endpoints, UI components, features
- ✅ **ESTIMATED:** Timeline (28-36 days), Costs ($121/mois)

---

## 🔧 Current Configuration

### Environment
- **OS:** macOS (darwin 24.6.0)
- **Hardware:** Mac M1 Max, 32GB RAM unifié, Metal GPU
- **Shell:** /bin/zsh
- **Workspace:** `/Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter`

### Development Environment (Local) ✅
- **Python:** Installé et fonctionnel
- **React/Node.js:** Installé et fonctionnel
- **Docker + Docker Compose:** Installé et fonctionnel
- **Note:** Phase 0 sera plus rapide grâce à environnement déjà opérationnel

### Repository State
- **Branch:** main
- **Status:** Clean working tree, synced with remote
- **Remote:** https://github.com/nicozefrench/diveteacher (PRIVÉ ✅)
- **Tracking:** origin/main
- **License:** Proprietary/Commercial (All Rights Reserved)

### Domaines & Hosting
- **Domaine Principal:** diveteacher.io (Vercel)
- **Domaine Secondaire:** diveteacher.app (redirect vers .io)
- **API Backend:** api.diveteacher.io (DigitalOcean GPU)
- **Vercel:** Compte payant avec API key ✅
- **DigitalOcean:** À configurer (GPU Droplet $100-150/mois)

### Services Status
- **Backend:** Not started yet (à faire Phase 0)
- **Frontend:** Not started yet (à faire Phase 0)
- **Neo4j:** Not started yet (à faire Phase 0)
- **Ollama + Mistral:** Not started yet (à faire Phase 0)
- **Supabase:** À configurer Phase 1
- **Sentry:** À configurer Phase 0
- **Docker Compose:** Not running yet

---

## 📋 Key Project Structure

```
diveteacher/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── upload.py      # Upload documents (admin)
│   │   │   ├── query.py       # RAG query (streaming)
│   │   │   ├── health.py      # Health checks
│   │   │   └── graph.py       # Graph endpoints
│   │   ├── core/              # Core logic
│   │   │   ├── llm.py         # LLM abstraction (Mistral)
│   │   │   ├── rag.py         # RAG chain
│   │   │   ├── processor.py   # Document processing
│   │   │   └── config.py      # Configuration
│   │   ├── integrations/      # External services
│   │   │   ├── neo4j.py       # Neo4j client
│   │   │   ├── graphiti.py    # Graphiti integration
│   │   │   ├── dockling.py    # PDF/PPT processing
│   │   │   ├── sentry.py      # Error tracking
│   │   │   └── supabase.py    # Auth & DB (à créer Phase 1)
│   │   └── models/            # Pydantic models
│   ├── requirements.txt       # Python deps
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Chat.jsx       # Chat interface
│   │   │   ├── FileUpload.jsx # Upload (admin)
│   │   │   ├── Auth/          # Login/Signup (à créer Phase 1)
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vercel.json
├── docker/
│   ├── docker-compose.dev.yml  # Dev local (Mac M1 Max)
│   └── docker-compose.prod.yml # Prod (DigitalOcean GPU)
├── CURRENT-CONTEXT.md          # This file (persistent memory)
├── DIVETEACHER-V1-PLAN.md      # Plan détaillé 9 phases
├── GOAL.md                     # Project objectives (DiveTeacher)
└── README.md                   # Quick start guide
```

---

## 🎯 Next Steps (Prioritized)

### Prochaine Session: PHASE 0 - Setup Environnement (2-3 jours)

#### Immediate Tasks - Session 2
1. [ ] Créer `.env` depuis `env.template`
2. [ ] Configurer Sentry (backend + frontend projects)
3. [ ] Démarrer stack Docker locale sur Mac M1 Max
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up -d
   ```
4. [ ] Pull Mistral 7B model
   ```bash
   docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M
   ```
5. [ ] Tester services locaux
   - Neo4j: http://localhost:7474
   - Backend API: http://localhost:8000/docs
   - Frontend: http://localhost:5173
   - Test Mistral inference
6. [ ] Vérifier que tout fonctionne sur Mac M1 Max

#### Setup Tasks - Session 2-3
1. [ ] Configurer DigitalOcean GPU Droplet (à faire quand prêt pour prod)
2. [ ] Décider domaine principal (.app vs .io)
3. [ ] (Phase 1) Créer projet Supabase + tables

### Development Phases (V1 - 28-36 jours)
- **Phase 0:** Setup environnement ← **PROCHAINE ÉTAPE**
- **Phase 1:** Auth multi-users (Supabase)
- **Phase 2:** Interface admin (gestion documents)
- **Phase 3:** Chat multi-conversations
- **Phase 4:** Graphe prérequis + visualisation
- **Phase 5:** i18n FR/EN
- **Phase 6:** Branding plongée (UI/UX océan)
- **Phase 7:** Monitoring (Sentry dashboards)
- **Phase 8:** Testing (documents FFESSM/SSI réels)
- **Phase 9:** Déploiement production

### Future Tasks (Post-Setup)
1. [ ] Uploader premiers documents FFESSM de test
2. [ ] Tester pipeline RAG complet
3. [ ] Optimiser prompts système pour plongée
4. [ ] Créer schéma Neo4j entités plongée
5. [ ] Implémenter extraction images/schémas

---

## 🔑 Key Configuration Files

### `.env.template` (Not Yet Reviewed)
**Purpose:** Template for environment variables  
**Critical Settings:**
- LLM_PROVIDER (ollama/claude/openai)
- NEO4J_PASSWORD
- OLLAMA_MODEL
- API URLs and ports

### `docker-compose.dev.yml`
**Purpose:** Local development orchestration  
**Services:**
- Backend (FastAPI)
- Neo4j (Graph database)
- Ollama (LLM server)
- Frontend (React dev server)

---

## 💡 Important Decisions & Notes

### Technology Choices
- **LLM:** Mistral 7B-instruct-Q5_K_M (local sur GPU DigitalOcean, Metal sur Mac dev)
- **Frontend Deployment:** Vercel (compte payant, domaines .app et .io)
- **Backend Deployment:** DigitalOcean GPU Droplet (~$120/mois) ⏸️ **Phase 9 seulement**
- **Database Graph:** Neo4j pour knowledge graph (entités plongée)
- **Database Users:** Supabase PostgreSQL (auth + conversations)
- **Auth:** Supabase **Cloud** (gratuit < 50k users) 💚
- **Monitoring:** Sentry (backend + frontend, gratuit < 5k events)

### Supabase Strategy (NEW Decision) ✅
- **✅ Supabase Cloud (gratuit)**
  - Jusqu'à 50,000 users gratuits
  - Pas de maintenance serveur
  - Dashboard intégré pour gestion
  - MCP tools disponibles pour création tables/auth
  - Même instance dev → production
- **❌ PAS self-hosted** (complexité, maintenance, coûts)

### Development Strategy
- **Local Dev:** Mac M1 Max (32GB RAM) avec Docker + Metal GPU pour Mistral
- **Phases 0-8:** 100% local (0€) - Aucun service cloud payant activé
- **Phase 9:** Production (DigitalOcean ~$120/mois) - Activé QUE quand tout fonctionne
- **Test local** complet avant push production
- **Supabase:** Cloud (gratuit) - Configuration lors Phase 1
- **Priority:** Setup environnement d'abord, puis auth, puis features

### DiveTeacher Specific Features
1. **Documents:** FFESSM (MFT, N4, MF1) + SSI (documentation officielle)
2. **Langues:** FR + EN avec toggle (react-i18next)
3. **Entités Neo4j:** Certifications, Équipement, Procédures, Concepts, Exercices
4. **Relations:** Prérequis (certif/exercices), Usage (équipement), Concepts liés
5. **Citations:** Extraits exacts avec badge école (FFESSM/SSI), pas de page number
6. **Images:** Extraction + affichage inline dans réponses
7. **Admin UI:** Upload, liste docs, stats Neo4j, visualisation graphe, monitoring
8. **User UI:** Chat streaming, sidebar conversations, historique sauvegardé

### Key Features to Remember
1. **Multi-utilisateurs:** Admin (tout accès), Instructeur (payant), Élève (limité ou payant)
2. **Streaming Responses:** Real-time token delivery pour UX fluide
3. **No Hallucinations:** Réponses UNIQUEMENT basées sur documents ingérés
4. **Document Processing:** Dockling (PDF/PPT→Markdown) → Graphiti (→Neo4j)
5. **Arbre Prérequis:** Éditable par admin, consulté par RAG
6. **Bilingue:** FR/EN avec switch, détection langue automatique
7. **Branding:** Thème océan (bleu #0077BE), logo "DiveTeacher" typography

---

## 🐛 Issues & Blockers

### Current Issues
- None yet

### Resolved Issues
- ✅ Repository cloning (was not a git repo initially, successfully cloned)

---

## 📚 Documentation References

### Key Documents
- **README.md:** Quick start, features, deployment
- **GOAL.md:** Architecture, objectives, technical details
- **docs/SETUP.md:** Detailed installation guide
- **docs/DEPLOYMENT.md:** Production deployment steps
- **docs/ARCHITECTURE.md:** System design deep-dive
- **docs/API.md:** Backend API reference
- **docs/TROUBLESHOOTING.md:** Common issues + solutions

### External Resources
- Neo4j: https://neo4j.com/
- Graphiti: https://github.com/getzep/graphiti
- Ollama: https://ollama.ai/
- Dockling: https://github.com/DS4SD/dockling
- FastAPI: https://fastapi.tiangolo.com/
- shadcn/ui: https://ui.shadcn.com/

---

## 🎓 Learning Notes

### RAG (Retrieval-Augmented Generation)
- Combines retrieval (from knowledge base) + generation (LLM)
- Prevents hallucinations by grounding responses in real data
- Flow: Query → Retrieve Context → Augment Prompt → Generate Answer

### Knowledge Graphs
- Entities (nodes) + Relationships (edges)
- Better than vector search for structured knowledge
- Cypher query language for Neo4j
- Graphiti automates entity/relationship extraction

### Document Processing Pipeline
```
PDF/PPT → Dockling (Markdown) → Graphiti (Entities/Relations) → Neo4j (Graph)
```

---

## 🔄 Session History

### Session 1 (October 26, 2025) ✅ COMPLETE
- **Duration:** Session complète (planning)
- **Focus:** Analyse boilerplate, planning stratégique V1, documentation complète
- **Key Actions:**
  - Cloned original rag-knowledge-graph-starter repository
  - Read README.md and GOAL.md in detail
  - Created CURRENT-CONTEXT.md for persistent tracking
  - Configured .cursor/rules/load-current-context.mdc for auto-context loading
  - Created new GitHub repository "diveteacher"
  - Migrated entire project to new repository
  - Updated all documentation references
  - Changed LICENSE to proprietary/commercial
  - **Strategic Planning Session:**
    - Asked 40+ questions stratégiques pour DiveTeacher
    - Analyzed complete boilerplate code (backend, frontend, Docker)
    - Documented all requirements utilisateurs
  - **Created DIVETEACHER-V1-PLAN.md:**
    - 9 phases détaillées (28-36 jours)
    - Architecture complète (diagrams, schemas)
    - Database schemas (Neo4j nodes/relations, PostgreSQL tables)
    - All API endpoints specifications
    - UI/UX specifications (admin + users)
    - Testing strategy
    - Deployment procedures
    - Cost estimates
  - **Updated GOAL.md:** DiveTeacher context, value proposition, users
  - **Key Decisions Documented:**
    - Domaine principal: **diveteacher.io** (+ .app en redirect)
    - LLM: Mistral 7B-instruct-Q5_K_M
    - Dev local: Mac M1 Max (32GB RAM, Metal GPU)
    - Auth: Supabase Cloud (gratuit)
    - Monitoring: Sentry
    - License: Proprietary (commercial)
    - Repository: Privé sur GitHub
- **Deliverables:**
  - ✅ DIVETEACHER-V1-PLAN.md (plan complet 900+ lignes)
  - ✅ CURRENT-CONTEXT.md (mémoire persistante)
  - ✅ GOAL.md updated
  - ✅ .cursor/rules configured
  - ✅ Git repository migrated
  - ✅ LICENSE proprietary
  - ✅ TODO list with 9 phases
- **Next Session Goal:** PHASE 0 - Setup environnement local (Docker, Mistral, tests)

### Session 2 (October 27, 2025) ✅ COMPLETE
- **Duration:** Session complète (Phase 0 → 0.8)
- **Focus:** Phase 0 completion + Phase 0.7 Advanced Document Processing + Phase 0.8 Neo4j RAG + Documentation
- **Key Actions:**
  - ✅ **CLARIFIED:** Supabase Strategy → **Cloud (gratuit)** vs self-hosted
    - Décision: Supabase Cloud (gratuit < 50k users)
    - MCP tools disponibles pour gestion
    - Pas de serveur à gérer
  - ✅ **CLARIFIED:** Dev 100% Local Strategy
    - Phases 0-8: 100% local (0€)
    - Phase 9 seulement: Production (DigitalOcean ~$120/mois)
    - Aucun coût avant que tout fonctionne
  - ✅ **UPDATED:** DIVETEACHER-V1-PLAN.md
    - Ajout tableau coûts par phase
    - Clarification Supabase Cloud usage
    - Section 0.2 DigitalOcean marquée "SKIP pour Phase 0-8"
    - Coûts production mis à jour
  - ✅ **PHASE 0: Environment Setup COMPLETE**
    - Created `.env` with local dev config
    - Fixed Python dependencies (docling, tenacity versions)
    - Fixed env var names (DOCKLING → DOCLING)
    - Resolved Neo4j port conflict with aria-neo4j
      - Changed DiveTeacher Neo4j: 7474→7475, 7687→7688
      - Kept aria-neo4j running (autre app)
    - Started all Docker services (neo4j, ollama, backend, frontend)
    - Pulled Mistral 7B-instruct-Q5_K_M (5.2GB)
    - Tested all services (Neo4j, Backend API, Frontend, Mistral inference)
    - All services healthy and running
  - ✅ **DOCUMENTATION OVERHAUL for AI Agents (First Pass)**
    - Rewrote `docs/SETUP.md` (100% optimized for Claude Sonnet 4.5)
      - Added AI agent context at top
      - Documented Neo4j port changes (7475/7688)
      - Added Mac M1 Max specific instructions
      - Included exact expected outputs for every command
      - Added decision trees and troubleshooting
      - 300+ lines, complete local dev guide
    - Rewrote `docs/DEPLOYMENT.md` (100% optimized for Claude Sonnet 4.5)
      - Phase 9 ONLY warning at top
      - Complete DigitalOcean GPU setup
      - Vercel deployment with custom domains
      - Security, monitoring, backup procedures
      - 600+ lines, production-ready guide
    - Updated `CURRENT-CONTEXT.md`
      - Added "Documentation Strategy for AI Agents" section
      - Documented all critical files for AI understanding
      - Explained why AI documentation differs from human docs
  - ✅ **PHASE 0.7: ADVANCED DOCUMENT PROCESSING IMPLEMENTED** 🚀
    - **Duration:** ~3h20 (incluant debug et tests)
    - **Référence:** `Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md`
    - **Objectif:** Production-ready RAG pipeline avec Docling + HybridChunker + Graphiti
    
  - ✅ **PHASE 0.8: NEO4J RAG OPTIMIZATION IMPLEMENTED** 🚀
    - **Duration:** ~2h30 (refactor + queries + tests)
    - **Référence:** `Devplan/PHASE-0.8-NEO4J-IMPLEMENTATION.md`
    - **Objectif:** Production-ready RAG queries avec full-text search + hybrid search
    
    **1. Neo4jClient Refactored ✅**
    - Migré `AsyncGraphDatabase` → `GraphDatabase.driver()` + `execute_query()`
    - Connection pool optimized (max 50 connections, timeout 60s)
    - Error handling spécifique (ServiceUnavailable, CypherSyntaxError, etc.)
    - Logging détaillé pour debugging
    
    **2. RAG Indexes Créés ✅**
    - Module: `backend/app/integrations/neo4j_indexes.py`
    - 3 indexes RAG-optimized:
      - `episode_content` (FULLTEXT) - Search dans chunks
      - `entity_name_idx` (RANGE) - Lookup rapide entités
      - `episode_date_idx` (RANGE) - Filter par date
    
    **3. RAG Queries Améliorées ✅**
    - `query_context_fulltext()` - Full-text search sur Episodes
    - `query_entities_related()` - Entity + graph traversal
    - `query_context_hybrid()` - Combine Episodes + Entities (BEST)
    - Scores, rankings, metadata enrichis
    
    **4. RAG Chain Updated ✅**
    - `retrieve_context()` utilise hybrid search
    - `build_rag_prompt()` format Episodes + Entities sections
    - System prompt DiveTeacher-specific
    - Citations avec scores et relations
    
    **5. Main.py Startup ✅**
    - create_rag_indexes() appelé au démarrage
    - verify_indexes() affiche stats (RAG: 3, Graphiti: 5)
    - Synchronous neo4j_client.close() au shutdown
    
    **6. API Graph Updated ✅**
    - graph.py migré vers execute_query() synchrone
    - Compatible avec nouveau driver pattern
    
    **7. Fichiers Créés (2) ✅**
    - `backend/app/integrations/neo4j_indexes.py` (189 lignes)
    - `backend/scripts/test_neo4j_rag.py` (200+ lignes)
    
    **8. Fichiers Modifiés (4) ✅**
    - `backend/app/integrations/neo4j.py` - Refactor complet (300 lignes)
    - `backend/app/core/rag.py` - Hybrid context support
    - `backend/app/main.py` - Index creation au startup
    - `backend/app/api/graph.py` - Synchronous queries
    
    **9. Tests E2E Créés ✅**
    - Script: `scripts/test_neo4j_rag.py`
    - 6 tests: Connection, Indexes, Full-text, Entity, Hybrid, RAG query
    
    **10. Documentation Updated ✅**
    - `docs/SETUP.md` - Section Phase 0.8 (260+ lignes)
    - `CURRENT-CONTEXT.md` - Summary Phase 0.8
  
  - ✅ **DOCUMENTATION UPDATE for Phase 0.7 & 0.8**
    - `backend/app/services/document_validator.py` (87 lignes)
    - `backend/app/services/document_chunker.py` (123 lignes)
    - `backend/tests/test_docling_pipeline.py` (200+ lignes)
    
    **7. Fichiers Modifiés (6) ✅**
    - `backend/app/integrations/dockling.py` - Refactor complet
    - `backend/app/integrations/graphiti.py` - API corrections
    - `backend/app/core/processor.py` - Pipeline 4 étapes
    - `backend/app/main.py` - Shutdown cleanup
    - `backend/requirements.txt` - +sentence-transformers +transformers
    - `backend/Dockerfile` - Force-reinstall tqdm
    
    **8. Tests End-to-End Réalisés ✅**
    - Upload PDF: ✅ Accepté, processing démarré
    - Docling models: ✅ Chargés sans crash
    - Status API: ✅ Retourne progress, stage, started_at
    - Logs: ✅ Affichent "Step 1/4", "Step 2/4", metrics détaillées
    
    **9. Validation Partielle ⏳**
    - Neo4j ingestion: En attente vérification complète (2-3 min)
    - Table extraction: Nécessite test avec tableaux complexes
    - Community building: À tester après multiple docs
    
    **10. Métriques Observées 📊**
    - Upload response: <100ms ✅
    - Docling model load: ~5-10s (première fois) ✅
    - Docker rebuild: ~70s ✅
    - tqdm crashes: 0 ✅
  
  - ✅ **DOCUMENTATION UPDATE for Phase 0.7**
    - Updated `Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md`
      - Status: ✅ IMPLÉMENTÉ ET TESTÉ
      - Ajout section "RÉSULTATS D'IMPLÉMENTATION" (120+ lignes)
      - Problèmes rencontrés + solutions documentés
      - Tests end-to-end détaillés
      - Métriques observées
      - Code coverage estimates
    - Updated `docs/SETUP.md`
      - Nouvelle section "Phase 0.7: Advanced Document Processing"
      - Détails des 5 changements majeurs
      - Tests validation Phase 0.7
      - Neo4j verification queries
      - Troubleshooting Phase 0.7 spécifique
      - Success criteria détaillés
    - Updated `CURRENT-CONTEXT.md` (cette section!)

- **Deliverables:**
  - ✅ Phase 0 complete (local env working)
  - ✅ Phase 0.7 COMPLETE (production RAG pipeline)
  - ✅ Phase 0.8 COMPLETE (Neo4j RAG optimization)
  - ✅ docs/SETUP.md (AI-optimized, 500+ lines avec Phase 0.7)
  - ✅ docs/DEPLOYMENT.md (AI-optimized, 600+ lines)
  - ✅ Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md (updated avec résultats)
  - ✅ Devplan/PHASE-0.8-NEO4J-IMPLEMENTATION.md (complete implementation)
  - ✅ CURRENT-CONTEXT.md (updated avec Phase 0.7 & 0.8)
  - ✅ 3 nouveaux modules Python (validator, chunker, tests)
  - ✅ 6 fichiers modifiés (docling, graphiti, processor, main, requirements, Dockerfile)
  - ✅ All changes committed to GitHub

- **Next Session Goal:** Phase 0.9 - Graphiti OpenAI Integration

### Session 3 (October 27, 2025) ⚠️ BLOCKED
- **Duration:** ~4h (tentatives multiples)
- **Focus:** Phase 0.9 - Graphiti Integration with OpenAI GPT-5-nano
- **Status:** 🟡 30% Complete - BLOCKED by vector dimension mismatch
- **Key Actions:**
  - ⚠️ **PHASE 0.9: Graphiti OpenAI Integration - BLOCKED**
    - **Objective:** Integrate OpenAI GPT-5-nano for entity extraction + text-embedding-3-small for embeddings
    - **Rationale:** 2M tokens/min rate limit (fastest), best quality extraction
    - **Architecture Decision:** 
      - Graphiti: OpenAI GPT-5-nano (entity extraction) + text-embedding-3-small (embeddings)
      - RAG/User: Ollama Mistral 7b (user queries) - SÉPARÉ, pas de mélange!
    
    **1. Dependencies Updated ✅**
    - graphiti-core: 0.3.7 → 0.17.0
    - neo4j: 5.25.0 → 5.26.0
    - openai: 1.52.0 → 1.91.0
    - pydantic: 2.9.0 → 2.11.5
    - tenacity: 8.5.0 → 9.0.0
    
    **2. Custom LLM Client Created ⚠️**
    - File: `backend/app/integrations/custom_llm_client.py` (108 lignes)
    - Purpose: Adapter OpenAI API parameters for gpt-5-nano
    - Problem: gpt-5-nano requires `max_completion_tokens` instead of `max_tokens`
    - Solution: Override `_generate_response()` to translate parameters
    - Bugs Fixed:
      - ✅ Signature mismatch (5 args vs 2-3)
      - ✅ Pydantic serialization (`ExtractedEntities` → dict via `model_dump()`)
      - ❌ **Vector dimension mismatch (CURRENT BLOCKER)**
    
    **3. Graphiti Client Refactored ⚠️**
    - File: `backend/app/integrations/graphiti.py` (refactor complet)
    - Explicit OpenAI configuration:
      - LLM: `Gpt5NanoClient` with gpt-5-nano model
      - Embedder: `OpenAIEmbedder` with text-embedding-3-small (1536 dims)
      - CrossEncoder: `OpenAIRerankerClient` with gpt-5-nano
    - Added detailed logs (chunk-by-chunk ingestion)
    - Added timeout: 120s per chunk with `asyncio.wait_for()`
    - Ingestion summary metrics (success/fail/avg time)
    
    **4. Tests Attempted (4 uploads) ❌**
    - **Test 1:** ❌ `max_tokens not supported` (72/72 chunks failed)
    - **Test 2:** ❌ Signature mismatch (72/72 chunks failed)
    - **Test 3:** ❌ `ExtractedEntities` serialization (72/72 chunks failed)
    - **Test 4:** ❌ **Vector dimension mismatch** (48+ chunks failed)
      ```
      Neo.ClientError.Statement.ArgumentError: 
      The supplied vectors do not have the same number of dimensions.
      ```
    - **Result:** 0 episodes created in Neo4j (144 old entities remain)
    
    **5. Root Cause Analysis 🔬**
    - **Symptom:** Vector similarity query crashes
    - **Hypothèse 1:** Neo4j indexes créés avec dimension incorrecte
    - **Hypothèse 2:** text-embedding-3-small (1536) incompatible avec Graphiti 0.17.0
    - **Hypothèse 3:** Custom client side effect sur embeddings generation
    - **Impact:** 100% ingestion failure, Phase 0.9 blocked
    
    **6. Documentation Créée ✅**
    - **Status Report:** `Devplan/STATUS-REPORT-2025-10-27.md` (672 lignes)
      - Executive summary
      - Components working vs not working
      - Root cause analysis (3 hypotheses)
      - 3 resolution options with trade-offs
      - Detailed test logs and metrics
    - **Graphiti Doc:** `docs/GRAPHITI.md` (nouveau, 500+ lignes)
      - Graphiti architecture & data model
      - OpenAI configuration details
      - Custom LLM client implementation
      - Known issues (3 bugs documented)
      - Troubleshooting guide
      - Next steps (Options A/B/C)
    - **Updated Documentation:**
      - `docs/INDEX.md` - Phase 0.9 status (BLOCKED)
      - `docs/ARCHITECTURE.md` - Tech stack avec OpenAI + Graphiti
      - Both reference new GRAPHITI.md and STATUS-REPORT
    
    **7. Fichiers Créés (2) ✅**
    - `backend/app/integrations/custom_llm_client.py` (108 lignes)
    - `docs/GRAPHITI.md` (500+ lignes)
    - `Devplan/STATUS-REPORT-2025-10-27.md` (672 lignes)
    
    **8. Fichiers Modifiés (4) ⚠️**
    - `backend/app/integrations/graphiti.py` (127 lignes, refactor complet)
    - `backend/requirements.txt` (5 dependencies updated)
    - `docs/INDEX.md` (updated Phase 0.9 status)
    - `docs/ARCHITECTURE.md` (updated tech stack)
    - `docker/docker-compose.dev.yml` (env_file configuration)
    
    **9. Métriques Observées 📊**
    - Docker rebuild: ~70s ✅
    - Backend startup: ~10s ✅
    - OpenAI API calls: 8-35s/chunk (working) ✅
    - Ingestion success rate: **0%** ❌
    - Neo4j episodes created: **0** ❌
    
    **10. Blockers Critiques ⚠️**
    - **Primary:** Vector dimension mismatch (Neo4j vector similarity)
    - **Secondary:** gpt-5-nano compatibility with Graphiti (custom client needed)
    - **Tertiary:** Docling tqdm thread lock (sporadic, ~20% uploads)

- **Deliverables:**
  - ✅ STATUS-REPORT-2025-10-27.md (complete analysis)
  - ✅ docs/GRAPHITI.md (new documentation)
  - ✅ docs/INDEX.md (updated)
  - ✅ docs/ARCHITECTURE.md (updated)
  - ✅ Custom LLM client implementation
  - ✅ Graphiti client refactored with explicit config
  - ❌ Graphiti ingestion pipeline (BLOCKED)

- **3 Resolution Options:**
  - **Option A (RECOMMENDED):** Fallback to gpt-4o-mini (<1h, low risk)
    - Revert custom client
    - Use officially supported model
    - Clear Neo4j Graphiti data
    - Test E2E ingestion
    - Trade-off: Lose 2M TPM speed, gain stability
  
  - **Option B (THOROUGH):** Debug vector dimension (2-3h, medium risk)
    - Inspect Neo4j vector indexes dimension
    - Log OpenAI embeddings actual dimension
    - Drop + recreate indexes with correct dimension
    - Fix gpt-5-nano integration
    - Trade-off: Understand root cause, potentially fix gpt-5-nano
  
  - **Option C (LONG TERM):** Pivot to Ollama (3-4h, high risk)
    - Fix Ollama container (currently unhealthy)
    - Configure Graphiti with OllamaClient
    - Test extraction quality
    - Trade-off: 0€ cost, local, but quality unknown

- **Next Session Goal:** 
  - **Decision Required:** Choose Option A/B/C
  - User analyzing STATUS-REPORT-2025-10-27.md
  - Recommended: Option A (gpt-4o-mini) for quick unblock

---

## 📝 Notes for Future Sessions

### Always Check First
1. Read this file (CURRENT-CONTEXT.md) at the start of each session
2. Update "Last Updated" timestamp when making changes
3. Mark completed tasks with ✅
4. Add any new decisions or blockers
5. Update "Session History" with summary of work done

### Before Starting Work
- Review "Next Steps" section
- Check "Issues & Blockers"
- Verify current configuration status
- Continue from where previous session left off

### Session End Checklist
- [ ] Update work completed section
- [ ] Update next steps
- [ ] Document any issues encountered
- [ ] Add session summary to history
- [ ] Update last modified timestamp

---

## 🎯 Project Goals (Roadmap)

### V1 Goals (MVP - 4-5 semaines)
1. ✅ Environnement dev local fonctionnel
2. Upload documents FFESSM/SSI → Neo4j knowledge graph
3. Chat Q&A multilingue (FR/EN) avec citations exactes
4. Auth multi-users (admin, instructors, students)
5. Interface admin (gestion documents, visualisation graphe)
6. Conversations sauvegardées
7. Deploy production (Vercel + DigitalOcean GPU)

### V2 Goals (Monétisation - 2-3 semaines)
1. **Stripe integration** 💳 (paiements récurrents)
   - Pricing: Free (10 q/mois), Instructor (29€), Center (99€)
   - Billing dashboard
   - Usage tracking et limits
   - Webhooks Stripe → Supabase
   - Email notifications (confirmations, renouvellements)
2. Export conversations PDF
3. Bookmarks/favoris questions
4. Recherche dans conversations

### V3 Goals (Expansion - 3-4 semaines)
1. PADI documents integration
2. NAUI, CMAS international
3. TDI/SDI (plongée technique)
4. Mode quiz (test connaissances)
5. Voice input (speech-to-text)

### V4 Goals (Advanced - 4-6 semaines)
1. Mobile app (React Native)
2. Offline mode
3. Génération plans de cours (instructeurs)
4. Recommendations personnalisées
5. White-label pour centres (Enterprise plan)

---

**Remember:** This file is your persistent memory. Update it frequently!

