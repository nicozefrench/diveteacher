# 🏊‍♂️ DIVETEACHER V1 - PLAN DE DÉVELOPPEMENT DÉTAILLÉ

**Projet:** DiveTeacher - Assistant IA pour formation plongée  
**Version:** V1 (MVP Production-Ready)  
**Date Création:** 26 Octobre 2025  
**Status:** 📋 Planning Phase

---

## 🎯 OBJECTIF V1

Créer une **application SaaS en ligne** permettant aux instructeurs et élèves plongeurs d'accéder à un assistant IA qui répond avec précision aux questions basées sur les documents officiels FFESSM et SSI.

### Proposition de Valeur
> "Accédez instantanément à toutes les connaissances des manuels FFESSM et SSI via un assistant IA intelligent. Préparez vos cours, révisez vos examens, vérifiez les procédures - tout en un."

---

## 📊 ARCHITECTURE V1

```
┌─────────────────────────────────────────────────────────┐
│  VERCEL (Frontend React)                                │
│  - Interface bilingue FR/EN                             │
│  - Chat utilisateur + historique conversations         │
│  - Interface admin (upload, monitoring, graphe)         │
│  - Auth Supabase (login/signup)                         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS API calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│  DIGITALOCEAN GPU DROPLET ($100-150/mois)               │
│                                                          │
│  Docker Compose Stack:                                  │
│  ├── FastAPI Backend (Python)                           │
│  │   ├── /api/upload (admin only)                       │
│  │   ├── /api/query (streaming RAG)                     │
│  │   ├── /api/chat (save/load conversations)           │
│  │   └── /api/admin/* (admin endpoints)                 │
│  │                                                       │
│  ├── Ollama + Mistral 7B-instruct-Q5_K_M               │
│  │   └── GPU: 5.2GB VRAM                                │
│  │                                                       │
│  ├── Neo4j (Knowledge Graph)                            │
│  │   ├── Entities: Certifications, Équipement, etc.    │
│  │   ├── Relations: Prérequis, Utilisé_pour, etc.      │
│  │   └── Métadonnées: Source, Niveau, Version          │
│  │                                                       │
│  └── Document Storage                                    │
│      └── /uploads (PDFs, PPTs originaux)                │
│                                                          │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  SUPABASE (Auth & User DB)                              │
│  ├── PostgreSQL (users, conversations, metadata)        │
│  ├── Auth (email/password)                              │
│  └── Row Level Security (RLS)                           │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  SENTRY (Monitoring)                                     │
│  ├── Error tracking (backend + frontend)                │
│  ├── Performance monitoring                             │
│  └── User actions audit (admin actions)                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ STRUCTURE BASE DE DONNÉES

### Neo4j (Knowledge Graph)

**Nodes (Entités):**
```cypher
// Certifications
(:Certification {
  id, name, level, organization, 
  prerequisites[], description, 
  language, version, date
})

// Équipement
(:Equipment {
  id, name, type, usage, 
  description, image_url
})

// Procédures
(:Procedure {
  id, name, type, steps[], 
  safety_level, depth_limit, 
  description
})

// Concepts Théoriques
(:Concept {
  id, name, category, 
  explanation, formulas[], 
  related_laws[]
})

// Exercices
(:Exercise {
  id, name, type, difficulty,
  prerequisites[], description,
  location  // piscine, mer, etc.
})

// Documents Sources (métadonnées)
(:Document {
  id, filename, organization,
  language, version, date,
  page_count, status
})
```

**Relationships:**
```cypher
// Prérequis
(:Certification)-[:REQUIRES]->(:Certification)
(:Exercise)-[:REQUIRES]->(:Exercise)
(:Certification)-[:REQUIRES]->(:Exercise)

// Usage
(:Procedure)-[:USES]->(:Equipment)
(:Exercise)-[:USES]->(:Equipment)

// Relations conceptuelles
(:Concept)-[:RELATES_TO]->(:Concept)
(:Procedure)-[:APPLIES]->(:Concept)

// Limites de profondeur
(:Certification)-[:DEPTH_LIMIT {max_meters: 60}]->(:Depth)
(:Procedure)-[:REQUIRED_AT]->(:Depth)

// Source
(:Certification|Equipment|Procedure|Concept)-[:FROM]->(:Document)
```

### Supabase PostgreSQL

**Tables:**

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'instructor', 'student')),
  subscription_tier TEXT CHECK (tier IN ('free', 'instructor', 'center')),
  subscription_status TEXT DEFAULT 'active',
  preferred_language TEXT DEFAULT 'fr',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,  -- Auto-generated from first question
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  sources JSONB,  -- Citations extraites
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents Metadata (pour admin UI)
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename TEXT NOT NULL,
  organization TEXT NOT NULL,  -- FFESSM, SSI
  language TEXT NOT NULL,
  version TEXT,
  upload_date TIMESTAMPTZ DEFAULT NOW(),
  uploaded_by UUID REFERENCES users(id),
  processing_status TEXT DEFAULT 'pending',
  neo4j_nodes_count INT DEFAULT 0,
  neo4j_relationships_count INT DEFAULT 0,
  file_path TEXT,
  file_size_bytes BIGINT
);

-- Admin Audit Log
CREATE TABLE admin_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  resource_type TEXT,
  resource_id TEXT,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Row Level Security (RLS):**
```sql
-- Users can only see their own conversations
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_conversations ON conversations
  FOR SELECT USING (auth.uid() = user_id);

-- Only admins can access documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY admin_documents ON documents
  FOR ALL USING (
    auth.uid() IN (SELECT id FROM users WHERE role = 'admin')
  );
```

---

## 📐 PHASES DE DÉVELOPPEMENT

### **PHASE 0: Setup Environnement (2-3 jours)**

#### 0.1 Configuration Locale (Mac M1 Max - 32GB RAM)

**✅ Prérequis déjà installés:**
- Python (installé et fonctionnel)
- React / Node.js (installé et fonctionnel)
- Docker + Docker Compose (installé et fonctionnel)

**Configuration rapide:**
- [ ] Créer `.env` depuis `env.template`
- [ ] Configurer Supabase project (gratuit) **→ À faire lors de Phase 1**
  - Créer projet sur supabase.com
  - Noter `SUPABASE_URL` et `SUPABASE_ANON_KEY`
  - Créer tables (users, conversations, messages, documents)
  - Activer Email Auth
- [ ] Configurer Sentry projects (gratuit)
  - Backend project
  - Frontend project
  - Noter DSNs
- [ ] Démarrer stack Docker **sur Mac M1 Max (déjà fonctionnel)**
  - `docker-compose -f docker/docker-compose.dev.yml up -d`
  - Vérifier Neo4j: http://localhost:7474
  - Vérifier Backend API: http://localhost:8000/docs
  - Vérifier Frontend: http://localhost:5173
  - **Tester Mistral 7B en local** (GPU Metal, 32GB RAM unifié)

**Note:** Phase 0 sera **plus rapide** (1-2 jours au lieu de 2-3) car environnement de dev déjà opérationnel ✅

#### 0.2 Configuration DigitalOcean
- [ ] Créer GPU Droplet (16GB RAM, 100GB SSD)
  - Ubuntu 22.04
  - Installer Docker + Docker Compose
  - Installer NVIDIA drivers + CUDA
- [ ] Configuration réseau
  - Firewall: ports 80, 443, 22
  - Domaine: api.diveteacher.com → Droplet IP
  - SSL: Certbot Let's Encrypt
- [ ] Volumes persistants
  - `/data/uploads` (documents)
  - `/data/neo4j` (graphe)
  - `/data/ollama` (modèles)

#### 0.3 Pull Mistral Model
```bash
# Local (Mac M1 Max - 32GB RAM unifié)
# Ollama utilisera Metal (GPU intégré Apple Silicon)
docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M

# Vérifier le modèle
docker exec rag-ollama ollama list

# Test rapide
docker exec rag-ollama ollama run mistral:7b-instruct-q5_K_M "Explique la loi de Dalton en plongée"

# DigitalOcean (GPU) - À faire lors du déploiement Phase 9
docker exec rag-ollama ollama pull mistral:7b-instruct-q5_K_M
```

**Note:** Mac M1 Max est parfait pour le dev local - Metal GPU + 32GB RAM unifié permettent de tourner Mistral 7B confortablement.

---

### **PHASE 1: Authentification Multi-Utilisateurs (3-4 jours)**

#### 1.1 Backend: Supabase Integration
- [ ] Installer dépendances Python
  ```bash
  # backend/requirements.txt
  supabase==2.3.0
  gotrue==2.3.0
  ```
- [ ] Créer `backend/app/integrations/supabase.py`
  - Client Supabase
  - Fonction `verify_token()`
  - Fonction `get_user_role()`
- [ ] Créer middleware auth
  - `backend/app/core/auth.py`
  - Decorator `@require_auth`
  - Decorator `@require_admin`
- [ ] Protéger endpoints
  - `/api/upload` → admin only
  - `/api/query` → authenticated users
  - `/api/chat/*` → authenticated users

#### 1.2 Frontend: Auth UI
- [ ] Installer `@supabase/supabase-js`
- [ ] Créer composants auth
  - `frontend/src/components/Auth/Login.jsx`
  - `frontend/src/components/Auth/Signup.jsx`
  - `frontend/src/components/Auth/AuthProvider.jsx` (context)
- [ ] Créer routes protégées
  - `/login`, `/signup` → public
  - `/chat` → authenticated
  - `/admin` → admin only
- [ ] Stocker token dans localStorage
- [ ] Auto-refresh token

#### 1.3 User Roles & Permissions
- [ ] Définir permissions par rôle
  ```javascript
  ROLES = {
    admin: ['upload', 'delete', 'view_graph', 'manage_users'],
    instructor: ['query', 'save_chat', 'export'],
    student: ['query', 'save_chat']
  }
  ```
- [ ] Implémenter RBAC (Role-Based Access Control)

---

### **PHASE 2: Interface Admin - Gestion Documents (4-5 jours)**

#### 2.1 Backend: Admin API Endpoints
- [ ] `POST /api/admin/upload`
  - Upload document (PDF/PPT)
  - Validation taille (max 200MB pour gros manuels)
  - Sauvegarde temporaire
  - Lancer traitement background
- [ ] `GET /api/admin/documents`
  - Liste tous documents uploadés
  - Filtres: organisation, langue, status
  - Pagination
- [ ] `GET /api/admin/documents/{id}`
  - Détails document
  - Stats Neo4j (nodes, relationships créés)
  - Logs de processing
- [ ] `DELETE /api/admin/documents/{id}`
  - Suppression document
  - Suppression nodes/relationships Neo4j associés
  - Suppression fichier physique
- [ ] `GET /api/admin/documents/{id}/status`
  - Statut processing temps réel
  - Progress bar (0-100%)

#### 2.2 Processing Pipeline Amélioré
- [ ] Modifier `backend/app/core/processor.py`
  - Support documents longs (200+ pages)
  - Chunking intelligent par chapitre
  - Extraction images/schemas
  - Progress tracking (0%, 25%, 50%, 75%, 100%)
- [ ] Gestion métadonnées
  - Détecter langue (FR/EN)
  - Extraire organisation (FFESSM/SSI) depuis filename ou contenu
  - Parser version et date si présente
- [ ] Intégration Supabase
  - Créer entry dans table `documents` au début
  - Update status: pending → processing → completed/failed
  - Stocker stats Neo4j

#### 2.3 Frontend: Admin Dashboard
- [ ] Page `/admin/documents`
  - Table documents avec colonnes:
    - Filename
    - Organisation (FFESSM/SSI)
    - Langue
    - Date upload
    - Status (badge coloré)
    - Actions (voir détails, supprimer)
  - Bouton "Upload Document"
  - Filtres et recherche
- [ ] Modal Upload
  - Drag & drop fichier
  - Sélection organisation (dropdown)
  - Sélection langue (dropdown)
  - Progress bar upload
  - Progress bar processing (polling status)
- [ ] Page `/admin/documents/{id}`
  - Métadonnées détaillées
  - Preview PDF (iframe ou react-pdf)
  - Stats Neo4j
    - X nodes créés
    - Y relationships créés
    - Breakdown par type (Certification: 12, Equipment: 45, etc.)
  - Logs de processing
  - Timeline étapes
- [ ] Composants réutilisables
  - `DocumentTable.jsx`
  - `UploadModal.jsx`
  - `DocumentDetailsCard.jsx`
  - `StatusBadge.jsx`

#### 2.4 Extraction Images/Schemas
- [ ] Dockling: Extraire images des PDFs
  - Sauvegarder dans `/uploads/{doc_id}/images/`
  - Créer nodes (:Image) dans Neo4j
  - Lien avec concepts/procédures
- [ ] Stockage images
  - Option 1: DigitalOcean Spaces (S3-compatible)
  - Option 2: Local `/uploads` avec Nginx serve
- [ ] Affichage dans réponses
  - Détection "schema" ou "image" dans requête
  - Retourner URL image dans réponse
  - Frontend affiche image inline

---

### **PHASE 3: Chat Multi-Conversations (3-4 jours)**

#### 3.1 Backend: Conversations API
- [ ] `POST /api/chat/conversations`
  - Créer nouvelle conversation
  - Auto-générer titre depuis première question
- [ ] `GET /api/chat/conversations`
  - Liste conversations user (triées par date)
  - Inclure dernier message comme preview
- [ ] `GET /api/chat/conversations/{id}`
  - Charger tous messages de la conversation
  - Paginer si > 100 messages
- [ ] `POST /api/chat/conversations/{id}/messages`
  - Ajouter message user
  - Appeler RAG pipeline
  - Sauvegarder réponse assistant
  - Extraire citations
- [ ] `DELETE /api/chat/conversations/{id}`
  - Supprimer conversation complète

#### 3.2 Modifications RAG Pipeline
- [ ] Modifier `backend/app/core/rag.py`
  - Ajouter paramètre `conversation_id`
  - Charger contexte conversation (derniers N messages)
  - Inclure contexte dans prompt
  - Extraire citations exactes
    ```python
    citations = {
      "school": "FFESSM",  # ou SSI
      "text": "extrait exact du document...",
      "confidence": 0.95
    }
    ```
- [ ] System prompt spécialisé plongée
  ```
  Tu es un assistant expert en plongée sous-marine. 
  Tu dois répondre uniquement basé sur les documents FFESSM et SSI.
  
  Règles:
  - Réponds précisément aux questions
  - Cite toujours les extraits exacts
  - Indique l'école (FFESSM ou SSI)
  - Si l'information n'est pas dans les documents, dis-le clairement
  - Inclus les images/schemas si pertinents
  - Pour les procédures, liste les étapes dans l'ordre
  - Pour les prérequis, vérifie le graphe de connaissances
  ```

#### 3.3 Frontend: Chat Amélioré
- [ ] Sidebar conversations
  - Liste conversations (titre + preview)
  - Bouton "Nouvelle conversation"
  - Search conversations
  - Delete conversation (avec confirmation)
- [ ] Zone chat principale
  - Messages user (alignés droite, bleu)
  - Messages assistant (alignés gauche, gris)
  - Citations en italique avec badge école
  - Images inline si présentes
  - Markdown rendering
- [ ] Input zone
  - Textarea avec auto-resize
  - Bouton envoyer
  - Indicateur "typing..." quand streaming
  - Compteur caractères
- [ ] Gestion état
  - Context API ou Zustand pour conversations
  - Optimistic updates
  - Retry en cas d'erreur

---

### **PHASE 4: Graphe Prérequis & Visualisation (Admin) (4-5 jours)**

#### 4.1 Arbre Prérequis - Backend
- [ ] API endpoints
  - `GET /api/admin/graph/prerequisites`
    - Retourne arbre complet prérequis
    - Format: certifications + exercices
  - `POST /api/admin/graph/prerequisites`
    - Ajouter relation prérequis manuelle
    - Validation cycles (pas de dépendances circulaires)
  - `DELETE /api/admin/graph/prerequisites/{id}`
    - Supprimer relation prérequis
- [ ] Algorithmes graphe
  - Détection chemins prérequis (Cypher queries)
  - Suggestion prérequis manquants (ML pattern detection)
  - Validation cohérence

#### 4.2 Visualisation Graphe - Frontend Admin
- [ ] Page `/admin/knowledge-graph`
- [ ] Intégrer bibliothèque visualisation
  - Option 1: **vis-network** (léger, performant)
  - Option 2: **react-force-graph** (D3.js, beautiful)
  - Option 3: **cytoscape.js** (pour graphes complexes)
- [ ] Features visualisation
  - Nodes colorés par type (Certification=bleu, Equipment=vert, etc.)
  - Relations avec labels
  - Zoom/pan
  - Click node → voir détails
  - Filtres par organisation (FFESSM/SSI)
  - Filtres par type (Certifications only, etc.)
  - Search node
- [ ] Mode édition
  - Double-click → éditer node
  - Drag entre nodes → créer relation
  - Right-click → delete
  - Sauvegarder changements

#### 4.3 Export Graphe
- [ ] `GET /api/admin/graph/export`
  - Format JSON
  - Format CSV
  - Format GraphML (pour Gephi, Cytoscape desktop)

---

### **PHASE 5: Internationalisation FR/EN (2-3 jours)**

#### 5.1 Backend i18n
- [ ] Structure traductions
  ```
  backend/locales/
  ├── fr.json
  └── en.json
  ```
- [ ] Messages d'erreur bilingues
- [ ] System prompts bilingues (détection langue question)

#### 5.2 Frontend i18n
- [ ] Installer `react-i18next`
- [ ] Créer fichiers traductions
  ```
  frontend/src/locales/
  ├── fr/
  │   ├── common.json
  │   ├── auth.json
  │   ├── chat.json
  │   └── admin.json
  └── en/
      ├── common.json
      ├── auth.json
      ├── chat.json
      └── admin.json
  ```
- [ ] Créer composant LanguageToggle
  - Switch FR/EN dans header
  - Icônes drapeaux
  - Sauvegarder préférence user (Supabase)
- [ ] Traduire tous composants
  - Labels, boutons, messages
  - Placeholders
  - Tooltips
  - Error messages

---

### **PHASE 6: Branding & UI/UX Plongée (2-3 jours)**

#### 6.1 Design System
- [ ] Palette couleurs thème océan
  ```css
  --primary: #0077BE (bleu océan)
  --secondary: #00A8CC (cyan)
  --accent: #FF6B35 (corail)
  --dark: #003459 (bleu profond)
  --light: #E8F4F8 (bleu clair)
  ```
- [ ] Typographie
  - Headers: "Poppins" ou "Inter" (modernes)
  - Body: "Open Sans" ou "Roboto"
- [ ] Composants
  - Boutons avec effet ripple
  - Cards avec ombres douces
  - Inputs avec focus bleu océan
  - Badges arrondis

#### 6.2 Logo & Assets
- [ ] Logo "DiveTeacher"
  - Typography only pour V1
  - Typo ocean-themed (bleu gradient)
  - Générer avec Figma ou Canva
- [ ] Favicon
- [ ] Images placeholders
  - Background hero (plongeur sous l'eau)
  - Empty states (no conversations, no documents)

#### 6.3 Landing Page (si nécessaire)
- [ ] Section hero
  - Titre: "Maîtrisez la plongée avec l'IA"
  - Subtitle: "Assistant intelligent basé sur FFESSM & SSI"
  - CTA: "Commencer gratuitement"
- [ ] Features
  - 3 cards: Instructeurs, Élèves, Centres
- [ ] Pricing (simple)
  - Free tier: 10 questions/mois
  - Instructor: 29€/mois illimité
  - Center: 99€/mois + 5 comptes
- [ ] Footer
  - Links, contact, mentions légales

---

### **PHASE 7: Monitoring & Sentry (1-2 jours)**

#### 7.1 Backend Monitoring
- [ ] Sentry init déjà en place ✅
- [ ] Ajouter custom events
  - Document uploaded
  - Document processed (success/fail)
  - Query executed (avec latency)
  - User signed up
  - Admin action (audit)
- [ ] Performance tracking
  - RAG query time
  - Mistral inference time
  - Neo4j query time

#### 7.2 Frontend Monitoring
- [ ] Sentry React init
- [ ] Error boundaries
- [ ] User feedback widget
- [ ] Performance marks
  - Time to first render
  - Time to interactive
  - Chat message latency

#### 7.3 Admin Monitoring Dashboard
- [ ] Page `/admin/monitoring`
- [ ] Metrics cards
  - Total users
  - Total conversations
  - Total documents
  - Avg query time
  - Error rate
- [ ] Charts (simple)
  - Queries per day (line chart)
  - Users signup (bar chart)
  - Top errors (table)

---

### **PHASE 8: Testing & Validation (3-4 jours)**

#### 8.1 Tests Manuels
- [ ] Scénario 1: Upload document FFESSM MFT
  - Admin login
  - Upload PDF 150 pages
  - Vérifier processing (progress bar)
  - Check Neo4j nodes créés
  - Check graphe visualisation
- [ ] Scénario 2: Questions théorie
  - User login (instructor)
  - Nouvelle conversation
  - Question: "Explique la loi de Dalton en plongée"
  - Vérifier citation FFESSM
  - Vérifier streaming fluide
  - Check conversation sauvegardée
- [ ] Scénario 3: Questions prérequis
  - Question: "Quels sont les prérequis pour le N2 FFESSM?"
  - Vérifier arbre prérequis utilisé
  - Vérifier réponse précise
- [ ] Scénario 4: Questions avec image
  - Question: "Montre-moi le schéma de dissociation buco-nasale"
  - Vérifier image affichée inline
- [ ] Scénario 5: Multi-langue
  - Toggle EN
  - Question en anglais sur doc SSI
  - Vérifier réponse en anglais
  - Toggle FR
  - Vérifier UI traduite

#### 8.2 Tests Performance
- [ ] Load testing
  - 10 users simultanés
  - 100 queries/min
  - Vérifier latence < 2s
- [ ] GPU monitoring
  - Vérifier VRAM usage (< 8GB)
  - Vérifier GPU utilization (> 70%)
- [ ] Neo4j performance
  - Queries < 500ms
  - Index optimizations

#### 8.3 Tests Documents Réels
- [ ] Uploader 3-5 documents réels
  - MFT FFESSM (gros)
  - Cours N4 (moyen)
  - Doc SSI (anglais)
- [ ] Tester 20-30 questions réelles
  - Théorie
  - Procédures
  - Prérequis
  - Images/schemas
- [ ] Valider qualité réponses
  - Précision
  - Citations exactes
  - Pas d'hallucinations

---

### **PHASE 9: Déploiement Production (2-3 jours)**

#### 9.1 DigitalOcean Production Setup
- [ ] Configuration docker-compose.prod.yml
  - Production environment variables
  - Health checks
  - Restart policies
- [ ] Nginx reverse proxy
  - SSL/TLS (Let's Encrypt)
  - Rate limiting
  - CORS headers
  - Gzip compression
- [ ] Backup automatique
  - Neo4j daily backup
  - Documents weekly backup
  - Supabase auto-backup ✅

#### 9.2 Vercel Deployment
- [x] Compte Vercel payant avec API key ✅
- [x] Domaines: **diveteacher.io** (principal) + diveteacher.app (redirect) ✅
- [ ] Connect GitHub repo (diveteacher - privé)
- [ ] Configure environment variables
  ```
  VITE_API_URL=https://api.diveteacher.io
  VITE_SUPABASE_URL=...
  VITE_SUPABASE_ANON_KEY=...
  VITE_SENTRY_DSN=...
  ```
- [ ] Deploy production
- [ ] Tester domaine principal: https://diveteacher.io
- [ ] Configurer redirect: diveteacher.app → diveteacher.io

#### 9.3 DNS & Domaines
- [x] Domaines déjà achetés: **diveteacher.io** (principal) et **diveteacher.app** (Vercel)
- [ ] Configurer DNS
  - **diveteacher.io** → Vercel (frontend principal)
  - **api.diveteacher.io** → DigitalOcean GPU IP (backend)
  - **www.diveteacher.io** → Redirect to diveteacher.io
  - **diveteacher.app** → Redirect to diveteacher.io (rerouting)
  - **www.diveteacher.app** → Redirect to diveteacher.io

#### 9.4 Monitoring Production
- [ ] Sentry alerts configurées
- [ ] Uptime monitoring (UptimeRobot gratuit)
- [ ] Log aggregation (si nécessaire)

---

## 📋 CHECKLIST PRÉ-LANCEMENT

### Fonctionnel
- [ ] Upload documents fonctionne (admin)
- [ ] Processing documents complet → Neo4j
- [ ] Auth multi-users (signup, login, logout)
- [ ] Chat streaming fluide
- [ ] Conversations sauvegardées
- [ ] Citations exactes avec école
- [ ] Images affichées
- [ ] Graphe visualisation (admin)
- [ ] Arbre prérequis consulté
- [ ] Bilingue FR/EN switch
- [ ] UI/UX plongée (couleurs, logo)

### Performance
- [ ] Latence query < 3s (moyenne)
- [ ] GPU VRAM < 8GB
- [ ] Neo4j queries < 500ms
- [ ] Frontend load < 2s

### Sécurité
- [ ] Auth Supabase sécurisée
- [ ] RLS activé sur toutes tables
- [ ] Admin endpoints protégés
- [ ] Documents sources privés (non accessibles direct)
- [ ] HTTPS partout
- [ ] Rate limiting API

### Monitoring
- [ ] Sentry backend OK
- [ ] Sentry frontend OK
- [ ] Admin dashboard metrics
- [ ] Alerts configurées

### Documentation
- [ ] README.md mis à jour
- [ ] GOAL.md mis à jour avec DiveTeacher
- [ ] API documentation (/docs)
- [ ] Guide admin (upload documents)
- [ ] Guide utilisateur (usage chat)

---

## 🚀 ROADMAP POST-V1 (V2, V3...)

### V2 - Monétisation (SaaS Payant) 💳

**Stripe Integration (Prioritaire V2):**
- [ ] Stripe account setup (diverteacher)
- [ ] Stripe API integration (backend)
  - Créer customers
  - Créer subscriptions
  - Gérer paiements récurrents
  - Webhooks (subscription events)
- [ ] Pricing tiers
  - **Free:** 10 questions/mois (trial)
  - **Instructor:** 29€/mois (illimité, 1 user)
  - **Center:** 99€/mois (illimité, 5 users)
  - **Enterprise:** Sur devis (illimité users, white-label)
- [ ] Billing dashboard (frontend)
  - Page abonnement
  - Gestion carte bancaire (Stripe Checkout)
  - Historique factures
  - Upgrade/downgrade plans
- [ ] Usage limits enforcement
  - Compteur questions/mois
  - Blocage automatique si limite atteinte
  - Notifications avant limite
- [ ] Supabase integration
  - Table `subscriptions` (link Stripe)
  - Table `usage_tracking` (questions count)
  - Webhooks Stripe → Supabase
- [ ] Email notifications (SendGrid/Postmark)
  - Confirmation paiement
  - Renouvellement abonnement
  - Échec paiement
  - Upgrade confirmation

**Prérequis techniques:**
- [ ] SSL/HTTPS obligatoire (déjà sur Vercel ✅)
- [ ] Webhooks endpoint sécurisé
- [ ] Logs paiements (audit)
- [ ] RGPD compliance (données bancaires via Stripe uniquement)

### V2 - Features Avancées
- [ ] Export conversations PDF
- [ ] Bookmarks/favoris questions
- [ ] Recherche dans conversations
- [ ] Suggestions questions populaires
- [ ] Mode "quiz" (test connaissances)

### V3 - Expansion Écoles
- [ ] PADI documents
- [ ] NAUI
- [ ] CMAS international
- [ ] TDI/SDI (technique)

### V3 - AI Features
- [ ] Voice input (speech-to-text)
- [ ] Génération plans de cours (instructeurs)
- [ ] Résumés automatiques sessions
- [ ] Recommendations personnalisées

### V4 - Mobile
- [ ] React Native app
- [ ] Offline mode (cached responses)
- [ ] Push notifications

---

## 📊 MÉTRIQUES SUCCÈS V1

### Techniques
- ✅ Uptime > 99%
- ✅ Latence moyenne < 3s
- ✅ Taux erreur < 1%
- ✅ GPU utilization 50-80%

### Utilisateurs (3 mois)
- 🎯 50+ users inscrits
- 🎯 10+ instructeurs actifs
- 🎯 1000+ conversations
- 🎯 5000+ messages échangés

### Qualité
- 🎯 Satisfaction > 4/5
- 🎯 Précision réponses > 90%
- 🎯 Zéro hallucinations critiques
- 🎯 Citations exactes > 95%

---

## 💰 ESTIMATION COÛTS MENSUELS V1

### Infrastructure
| Service | Coût |
|---------|------|
| DigitalOcean GPU Droplet | $120 |
| Vercel (Frontend) | $0 (gratuit) |
| Supabase | $0 (gratuit < 50k users) |
| Sentry | $0 (gratuit < 5k events/mois) |
| Domaine (.com) | $12/an = $1/mois |
| **TOTAL** | **~$121/mois** |

### Post-Lancement (avec revenue)
- Revenue estimé: 10 instructeurs × 29€ = **290€/mois**
- Marge brute: 290€ - 121$ (~110€) = **~180€/mois**
- Break-even: ~5 utilisateurs payants

---

## 🎯 PROCHAINES ÉTAPES IMMÉDIATES

1. **Valider ce plan** avec vos ajustements
2. **Créer compte Supabase** (5 min)
3. **Créer comptes Sentry** (5 min)
4. **Commencer Phase 0** (setup environnement)

---

**Questions ?** 🤔

