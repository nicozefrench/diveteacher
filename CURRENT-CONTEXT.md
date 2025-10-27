# CURRENT CONTEXT - RAG Knowledge Graph Project

**Last Updated:** October 27, 2025 - Session 2 Starting  
**Project:** DiveTeacher - Assistant IA pour Formation Plongée  
**Repository:** https://github.com/nicozefrench/diveteacher (PRIVÉ)  
**Domaine Principal:** diveteacher.io (+ diveteacher.app en redirect)

---

## 📍 Current Status

**Phase:** Planning Complete - Starting Phase 0  
**Session:** 2 (Starting)  
**Environment:** macOS (darwin 24.6.0) - Mac M1 Max, 32GB RAM

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

### Session 2 (October 27, 2025) 🔄 IN PROGRESS
- **Duration:** Starting now
- **Focus:** Clarifications + préparation Phase 0
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
  - ✅ **UPDATED:** CURRENT-CONTEXT.md
    - Stratégie Supabase Cloud documentée
    - Dev strategy 0€ phases 0-8
    - Session 2 history added
- **Next:** Démarrer Phase 0 - Setup environnement local

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

