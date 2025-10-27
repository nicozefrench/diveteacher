# 📊 Status Report - DiveTeacher RAG Knowledge Graph
**Date:** 27 Octobre 2025, 18:50  
**Phase:** 0.9 - Graphiti Implementation (IN PROGRESS)  
**Dernière Session:** Tentative d'intégration OpenAI GPT-5-nano avec Graphiti

---

## 🎯 Executive Summary

### TL;DR
Le système est dans un état **partiellement fonctionnel mais bloqué au niveau Graphiti**. Docling et Neo4j fonctionnent correctement, mais l'ingestion Graphiti échoue à cause de plusieurs problèmes techniques liés à l'intégration OpenAI GPT-5-nano.

### État Général: 🟡 PARTIALLY WORKING

| Composant | Status | Health |
|-----------|--------|---------|
| **Neo4j** | ✅ WORKING | Healthy, 144 entities + 185 relations (données anciennes) |
| **Docling** | ⚠️ INTERMITTENT | Fonctionne mais erreur tqdm sporadique |
| **Graphiti Ingestion** | ❌ BROKEN | Échec à 100% (0 episodes créés) |
| **OpenAI GPT-5-nano** | ⚠️ PARTIAL | API fonctionne, mais problèmes d'intégration |
| **Backend API** | ✅ WORKING | Healthy, répond sur :8000 |
| **Frontend** | ✅ WORKING | Running sur :5173 |
| **Ollama** | ⚠️ UNHEALTHY | Container unhealthy (non critique pour Graphiti) |

### Bloqueurs Critiques
1. **Vector Dimension Mismatch** (Neo4j): Embeddings OpenAI (1536 dim) ≠ Config attendue
2. **Custom LLM Client** (Graphiti): Tentative d'adaptation `max_tokens` → `max_completion_tokens` introduit bugs
3. **Docling tqdm Thread Lock**: Erreur sporadique `type object 'tqdm' has no attribute '_lock'`

### Impact Utilisateur
- ❌ **Upload de PDF:** Échoue à l'étape d'ingestion Graphiti (75% de progression)
- ❌ **Knowledge Graph:** Aucune nouvelle donnée depuis plusieurs heures
- ⚠️ **Recherche RAG:** Fonctionne sur anciennes données (144 entities) mais stale

---

## 📦 Components Status Détaillé

### ✅ Ce Qui Fonctionne

#### 1. Infrastructure Docker
```
✅ rag-backend:    Up 16 min (healthy)  → :8000
✅ rag-neo4j:      Up 4 hours (healthy) → :7475 (browser), :7688 (bolt)
✅ rag-frontend:   Up 7 hours           → :5173
⚠️ rag-ollama:     Up 2 hours (unhealthy) → :11434
```
**Validation:**
- Backend API répond correctement aux healthchecks
- Neo4j accessible et opérationnel
- Frontend React s'affiche correctement

#### 2. Neo4j Database
```cypher
MATCH (n) RETURN count(n)
→ 329 nodes (144 entities + 185 relations)
```
**État:**
- ✅ Neo4j 5.26.0 fonctionne
- ✅ Indexes créés (episode_content, entity_name_idx, episode_date_idx)
- ✅ Contraintes Graphiti présentes
- ⚠️ **Données obsolètes** (dernière ingestion réussie: session précédente)

#### 3. Docling Pipeline (Backend)
**Fichiers:**
- `backend/app/services/document_processor.py`
- `backend/app/services/document_chunker.py`

**Capacités Testées:**
- ✅ Conversion PDF → Markdown
- ✅ HierarchicalChunker (256 tokens max)
- ✅ Extraction de 72 chunks pour Nitrox.pdf (35 pages)
- ⚠️ **Erreur sporadique:** `tqdm._lock` (non bloquante, retry fonctionne)

**Logs Typiques:**
```
✅ Docling conversion: 72 chunks in 45s
⚠️ Occasional: type object 'tqdm' has no attribute '_lock'
```

#### 4. Backend API Endpoints
**Testés et Fonctionnels:**
- `POST /api/upload` → 200 OK (accepte PDF, lance processing)
- `GET /api/health` → 200 OK
- `GET /api/graph/stats` → 200 OK (retourne stats Neo4j)
- `GET /api/upload/status/{id}` → ⚠️ Erreur JSON serialization (mineur)

---

### ❌ Ce Qui Ne Fonctionne Pas

#### 1. Graphiti Ingestion Pipeline (CRITIQUE)

**Fichier Problématique:** `backend/app/integrations/graphiti.py`

**Symptôme:**
```
[1/72] ❌ Failed chunk 0 after 8.22s: 'ExtractedEntities' object has no attribute 'get'
[2/72] ❌ Failed chunk 1 after 11.32s: 'ExtractedEntities' object has no attribute 'get'
...
[48/72] ❌ Failed chunk 47 after 35.38s: Invalid input for 'vector.similarity.cosine()': 
         The supplied vectors do not have the same number of dimensions.
```

**Résultat:** 0 episodes créés, 72 chunks sur 72 échouent

**Chronologie des Tentatives (Session Actuelle):**

**Tentative 1:** Graphiti par défaut (sans config explicite)
```
❌ Error: max_tokens not supported by gpt-5-nano, use max_completion_tokens
```

**Tentative 2:** Custom `Gpt5NanoClient` créé (`backend/app/integrations/custom_llm_client.py`)
- ✅ Fix: Signature `_generate_response(self, messages, response_model, max_tokens, model_size)`
- ✅ Fix: Conversion `max_tokens` → `max_completion_tokens`
- ✅ Fix: Conversion Pydantic object → dict via `model_dump()`
- ❌ **Nouveau problème:** Vector dimension mismatch (1536 ≠ expected)

**Tentative 3:** Toujours en cours (dernier log)
```
Neo.ClientError.Statement.ArgumentError: 
The supplied vectors do not have the same number of dimensions.
```

#### 2. OpenAI Integration Issues

**Configuration Actuelle:**
```python
# backend/app/integrations/graphiti.py
llm_config = LLMConfig(
    api_key=settings.OPENAI_API_KEY,
    model="gpt-5-nano",           # ✅ Correct
    small_model="gpt-5-nano",     # ✅ Correct
    max_tokens=4096               # ⚠️ Converti en max_completion_tokens
)

embedder_config = OpenAIEmbedderConfig(
    api_key=settings.OPENAI_API_KEY,
    embedding_model="text-embedding-3-small",  # ✅ Correct
    embedding_dim=1536            # ⚠️ PROBLÈME: Mismatch avec Neo4j?
)
```

**Problèmes Identifiés:**

**A. API Parameter Mismatch**
- OpenAI `gpt-5-nano` utilise `max_completion_tokens` (Responses/Assistants API)
- Graphiti `LLMConfig` utilise `max_tokens` (Chat Completions API legacy)
- **Solution Tentée:** Custom `Gpt5NanoClient` qui translate les paramètres
- **Résultat:** Signature correcte, mais nouveaux bugs downstream

**B. Vector Dimension Mismatch**
```
Expected: ?? dimensions (config Neo4j?)
Actual: 1536 dimensions (text-embedding-3-small standard)
```
**Hypothèse:** 
- Neo4j indexes créés avec dimension différente (session précédente?)
- Graphiti attend dimension spécifique non alignée avec text-embedding-3-small
- Besoin de recréer indexes Neo4j avec bonne dimension?

**C. Pydantic Object Serialization**
- Graphiti `node_operations.py:130` appelle `.get()` sur `ExtractedEntities`
- OpenAI `beta.chat.completions.parse()` retourne objet Pydantic
- **Solution Tentée:** Convertir avec `model_dump()` dans custom client
- **Résultat:** Fix partiel, mais erreur vector dimension apparue après

#### 3. Docling tqdm Thread Lock (Intermittent)

**Symptôme:**
```
❌ Docling conversion error: type object 'tqdm' has no attribute '_lock'
```

**Occurrence:** Sporadique (~20% uploads)

**Impact:** 
- Upload échoue à 10% (stage: conversion)
- Retry fonctionne généralement
- Non critique car non systématique

**Cause Probable:**
- Conflit version tqdm dans container Docker
- `python:3.11-slim` base image + tqdm threading
- Déjà documenté dans `PHASE-0.7-DOCLING-IMPLEMENTATION.md`

**Status:** ⚠️ Connu mais non résolu (workaround: retry)

---

## 🔍 Analyse Comparative vs. Plan PHASE-0.9

### Plan Original (PHASE-0.9-GRAPHITI-IMPLEMENTATION.md)

**Objectifs Définis:**
1. ✅ Mise à jour Graphiti vers 0.17.x (fait: requirements.txt)
2. ❌ Configuration LLM OpenAI GPT-5-nano (tentative, bugs critiques)
3. ❌ Mistral 7b (Ollama) pour RAG (pas encore testé, container unhealthy)
4. ❌ Utilisation native `graphiti.search()` (bloqué par ingestion)
5. ❌ Community building périodique (non implémenté, intentionnel)
6. ❌ Tests E2E complets (bloqués par ingestion)

### Tâches Complétées vs. Planifiées

| Phase Plan | Tâches | Status Réel | Écart |
|------------|--------|-------------|-------|
| **A - Préparation** | Update deps, backup, audit | ✅ DONE | Conforme |
| **B - Config Graphiti** | LLM config, embedder, crossencoder | ⚠️ PARTIAL | Custom client créé mais buggy |
| **C - RAG Integration** | Modify rag.py, test search | ❌ BLOCKED | Bloqué par B |
| **D - Tests E2E** | Upload PDF, verify Neo4j, query | ❌ BLOCKED | 0% complete |
| **E - Documentation** | Update docs, metrics | ❌ NOT STARTED | 0% |

### Déviations Majeures

**1. Custom LLM Client Non Prévu**
- Plan original: Utiliser Graphiti default OpenAI client
- Réalité: Créé `Gpt5NanoClient` custom (75 lignes) pour adapter API parameters
- Raison: `gpt-5-nano` incompatible avec `max_tokens` (need `max_completion_tokens`)

**2. Vector Dimension Issues Non Anticipées**
- Plan: Assume text-embedding-3-small (1536) compatible
- Réalité: Neo4j vector similarity crash avec dimension mismatch
- Besoin: Investigation config Neo4j indexes + potentiel recreate

**3. Docling tqdm Regression**
- Plan: Assume Docling stable (Phase 0.7 complétée)
- Réalité: Erreur tqdm sporadique réapparue
- Impact: Mineur (retry works) mais frustrant

---

## 🧪 Tests Effectués (Session Actuelle)

### Test 1: Upload Nitrox.pdf (Tentative 1)
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/Nitrox.pdf" \
  -F "metadata={\"user_id\":\"test_phase_final\"}"
```
**Résultat:**
- ✅ Upload accepted (200 OK)
- ✅ Docling conversion (72 chunks)
- ❌ Graphiti ingestion (0/72 chunks succeeded)
- **Erreur:** `max_tokens not supported`

**Actions:**
- Créé `custom_llm_client.py`
- Modified `graphiti.py` pour utiliser `Gpt5NanoClient`

### Test 2: Upload Nitrox.pdf (Tentative 2)
**Résultat:**
- ✅ Upload accepted
- ✅ Docling conversion
- ❌ Graphiti ingestion (0/72 chunks)
- **Erreur:** `Gpt5NanoClient._generate_response() takes from 2 to 3 positional arguments but 5 were given`

**Actions:**
- Fixed signature: `_generate_response(self, messages, response_model, max_tokens, model_size)`
- Rebuild backend

### Test 3: Upload Nitrox.pdf (Tentative 3)
**Résultat:**
- ✅ Upload accepted
- ⚠️ Docling error (tqdm lock) → Retry OK
- ❌ Graphiti ingestion (48/72 chunks attempted, all failed)
- **Erreur:** `ExtractedEntities object has no attribute 'get'`

**Actions:**
- Added `model_dump()` conversion Pydantic → dict
- Rebuild backend

### Test 4: Upload Nitrox.pdf (Tentative 4 - En Cours)
**Résultat Partiel:**
- ✅ Upload accepted
- ✅ Docling conversion
- ❌ Graphiti ingestion (>48 chunks attempted)
- **Erreur:** `vector.similarity.cosine(): vectors do not have same dimensions`

**Status:** Monitoring stopped, containers still running

### Neo4j Verification
```cypher
MATCH (n) RETURN count(n)
→ 329 nodes

MATCH (e:Episode) RETURN count(e)
→ 0 episodes (!)

MATCH (ent:Entity) RETURN count(ent)
→ 144 entities (anciennes)
```

**Conclusion:** Aucune nouvelle donnée ingérée malgré 4 tentatives

---

## 🔬 Root Cause Analysis

### Problème #1: Vector Dimension Mismatch (HIGHEST PRIORITY)

**Symptôme:**
```
Neo.ClientError.Statement.ArgumentError: 
The supplied vectors do not have the same number of dimensions.
```

**Hypothèses:**

**H1: Neo4j Indexes Configuration Incorrecte**
```python
# Code actuel: backend/app/integrations/graphiti.py
embedder_config = OpenAIEmbedderConfig(
    embedding_dim=1536  # text-embedding-3-small
)
```
- Graphiti crée indexes Neo4j avec dimension spécifique
- Si indexes existants ont dimension différente → mismatch
- **Vérification Nécessaire:** Query Neo4j vector index dimension

**H2: Graphiti Version 0.17.0 Breaking Change**
- Graphiti 0.17.0 potentiellement incompatible avec text-embedding-3-small
- Besoin version spécifique d'embedder?
- **Vérification:** Lire changelog Graphiti 0.17.0

**H3: Custom Client Bug**
- Custom `Gpt5NanoClient` modifie flow embedder
- Embeddings générés avec mauvaise dimension?
- **Vérification:** Log dimension réelle embeddings OpenAI response

**Actions Recommandées:**
1. Query Neo4j pour voir dimension indexes:
   ```cypher
   SHOW INDEXES
   CALL db.index.vector.queryNodes(...)
   ```
2. Drop + Recreate Graphiti indexes avec bonne dimension
3. Vérifier logs OpenAI embeddings response (dimension field)

### Problème #2: Custom LLM Client Complexity

**Analyse:**
La création d'un custom `Gpt5NanoClient` a introduit plusieurs bugs en cascade:

**Bug 1:** Signature incorrecte (fixed)
**Bug 2:** Pydantic object serialization (fixed)
**Bug 3:** Vector dimension mismatch (current)

**Question Fondamentale:**
> Est-ce que `gpt-5-nano` est compatible avec Graphiti 0.17.0?

**Alternatives:**
1. **Utiliser gpt-4o-mini** (modèle supporté, documented dans Graphiti)
2. **Downgrade Graphiti** à version stable avec Ollama
3. **Attendre fix Graphiti** pour gpt-5-nano support

**Trade-offs:**
| Option | Pros | Cons |
|--------|------|------|
| **gpt-4o-mini** | Supporté officiellement, works out of box | Moins rapide que gpt-5-nano (2M TPM) |
| **Ollama Mistral** | Local, 0€, privacy | Plus lent, qualité moindre extraction |
| **Fix custom client** | Garde gpt-5-nano (optimal) | Debugging time, risk nouveaux bugs |

### Problème #3: Docling tqdm (Low Priority)

**Analyse:**
- Bug connu depuis Phase 0.7
- Non bloquant (retry works)
- Fix nécessite investigation approfondie threading/asyncio

**Décision:** 
- ⏸️ **Defer to Phase 1+**
- Workaround actuel acceptable pour dev

---

## 📊 Metrics Actuelles

### Performance

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Backend Startup** | ~10s | <15s | ✅ OK |
| **PDF Upload API** | <1s | <2s | ✅ OK |
| **Docling Conversion** | 45s (72 chunks) | <60s | ✅ OK |
| **Graphiti Ingestion** | N/A (fails) | <5min | ❌ FAIL |
| **Neo4j Episodes** | 0 | >70 | ❌ FAIL |
| **Neo4j Entities** | 144 (stale) | >150 | ⚠️ STALE |

### Code Quality

**Fichiers Modifiés (Session):**
```
✅ backend/app/integrations/graphiti.py         (127 lignes, refactor complet)
✅ backend/app/integrations/custom_llm_client.py (108 lignes, nouveau fichier)
⚠️ backend/requirements.txt                     (updated deps)
```

**Test Coverage:**
- ❌ Aucun test unitaire pour custom_llm_client.py
- ❌ Aucun test d'intégration Graphiti
- ⚠️ Tests manuels uniquement (curl)

**Technical Debt:**
- Custom LLM client (75 lignes) sans tests
- Logs debugging verbeux (à cleaner)
- Neo4j indexes potentiellement corrompus

---

## 🎯 Gap Analysis: Où En Sommes-Nous vs. Objectif?

### Objectif Phase 0.9 (d'après plan)
> "Finaliser l'intégration Graphiti avec Docling et Neo4j pour un knowledge graph temporel fonctionnel"

### État Actuel
**Completion: ~30%**

**Ce qui devrait fonctionner:**
1. ❌ Upload PDF → Graphiti ingestion → Neo4j
2. ❌ Recherche RAG via `graphiti.search()`
3. ❌ Tests E2E passants
4. ❌ Documentation à jour

**Ce qui fonctionne réellement:**
1. ✅ Upload PDF → Docling conversion → Chunks
2. ⚠️ Neo4j database opérationnel (mais données stale)
3. ✅ Backend API endpoints basics

### Bloqueur Principal
**Graphiti Ingestion** est le single point of failure qui bloque tout le reste:
- Sans ingestion → Pas de nouveaux episodes
- Sans episodes → Pas de test search
- Sans search → Pas de validation RAG
- Sans validation → Phase 0.9 incomplete

---

## 🚀 Next Steps Recommandés

### Option A: Quick Win - Fallback to gpt-4o-mini (RECOMMENDED)

**Rationale:**
- gpt-4o-mini est **officiellement supporté** par Graphiti
- Pas de custom client nécessaire
- Documentation existe, examples fournis
- Performance acceptable (not 2M TPM but sufficient for dev)

**Steps:**
1. **Revert Custom Client** (10 min)
   ```bash
   git checkout backend/app/integrations/graphiti.py
   rm backend/app/integrations/custom_llm_client.py
   ```

2. **Update .env** (2 min)
   ```bash
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **Clear Neo4j Graphiti Data** (5 min)
   ```cypher
   // Neo4j Browser http://localhost:7475
   MATCH (n:Entity) DETACH DELETE n;
   MATCH (n:Episode) DETACH DELETE n;
   MATCH (n:Community) DETACH DELETE n;
   ```

4. **Rebuild + Test** (15 min)
   ```bash
   docker compose -f docker/docker-compose.dev.yml build backend
   docker compose -f docker/docker-compose.dev.yml up -d backend
   
   # Test upload
   curl -X POST http://localhost:8000/api/upload \
     -F "file=@TestPDF/Nitrox.pdf" \
     -F "metadata={\"user_id\":\"test_gpt4o_mini\"}"
   ```

5. **Monitor Logs** (10 min)
   ```bash
   docker logs rag-backend -f | grep "Graphiti\|Chunk"
   ```

**Expected Outcome:**
- ✅ Ingestion réussie (72/72 chunks)
- ✅ Episodes créés dans Neo4j
- ✅ Déblocage Phase 0.9

**Risque:** Faible (gpt-4o-mini proven)

---

### Option B: Debug Vector Dimension (THOROUGH)

**Rationale:**
- Comprendre root cause exact
- Potentiellement fix pour gpt-5-nano future use
- Meilleure compréhension Neo4j + Graphiti internals

**Steps:**
1. **Inspect Neo4j Vector Indexes** (15 min)
   ```cypher
   // Check all indexes
   SHOW INDEXES;
   
   // Find vector indexes
   CALL db.indexes() 
   YIELD name, type, properties, labelsOrTypes 
   WHERE type CONTAINS 'VECTOR'
   RETURN name, properties, labelsOrTypes;
   ```

2. **Log OpenAI Embeddings Dimension** (20 min)
   ```python
   # backend/app/integrations/custom_llm_client.py
   # Add debug logging in embedder calls
   logger.info(f"Embeddings dimension: {len(embedding_vector)}")
   ```

3. **Drop + Recreate Graphiti Indexes** (10 min)
   ```python
   # backend script
   client = await get_graphiti_client()
   await client.drop_indices()  # If exists
   await client.build_indices_and_constraints()
   ```

4. **Test avec Dimension Logging** (15 min)
   ```bash
   # Watch logs for dimension values
   docker logs rag-backend -f | grep "dimension"
   ```

5. **Adjust embedder_config if Needed** (10 min)
   ```python
   # If dimension != 1536, adjust
   embedder_config = OpenAIEmbedderConfig(
       embedding_model="text-embedding-3-small",
       embedding_dim=<correct_value>
   )
   ```

**Expected Outcome:**
- ✅ Comprendre exact dimension mismatch
- ✅ Fix embedder config
- ✅ gpt-5-nano functional

**Risque:** Moyen (peut révéler problèmes plus profonds)

---

### Option C: Pivot to Ollama (LONG TERM)

**Rationale:**
- Local, 0€ cost
- Privacy (pas de data sent to OpenAI)
- Mistral 7b sufficient for diving knowledge extraction

**Steps:**
1. **Fix Ollama Container** (20 min)
   ```bash
   docker compose -f docker/docker-compose.dev.yml restart ollama
   docker logs rag-ollama
   # Debug unhealthy status
   ```

2. **Configure Graphiti for Ollama** (30 min)
   ```python
   # backend/app/integrations/graphiti.py
   from graphiti_core.llm_client import OllamaClient
   
   llm_client = OllamaClient(
       base_url="http://ollama:11434",
       model="mistral:7b-instruct-q5_K_M"
   )
   ```

3. **Test Extraction Quality** (1h)
   - Upload plusieurs PDFs
   - Comparer entities extraites vs. attendu
   - Itérer sur prompts si nécessaire

**Expected Outcome:**
- ✅ Full local stack
- ⚠️ Qualité extraction potentiellement moindre
- ✅ 0€ cost long term

**Risque:** Élevé (qualité unknown, plus lent)

---

## 💡 Recommandation Finale

### Priorité Immédiate: **Option A (gpt-4o-mini)**

**Justification:**
1. **Débloque Phase 0.9 rapidement** (<1h total)
2. **Risque minimal** (solution documentée)
3. **Permet validation E2E** (objectif principal)
4. **gpt-5-nano peut être révisité** en Phase 1+ après stabilisation

### Plan Next Session:

**Session 1 (1-2h): Déblocage avec gpt-4o-mini**
1. Revert custom client
2. Clear Neo4j Graphiti data
3. Test ingestion avec gpt-4o-mini
4. Valider E2E: Upload → Ingestion → Search
5. Update `PHASE-0.9-GRAPHITI-IMPLEMENTATION.md` avec résultats

**Session 2 (2-3h): Compléter Phase 0.9**
1. Implémenter RAG search via `graphiti.search()`
2. Tests E2E complets (query quality)
3. Documentation finale
4. Métriques de performance

**Session 3 (optionnel): gpt-5-nano Deep Dive**
1. Si besoin performance 2M TPM absolument
2. Debug vector dimension avec logs détaillés
3. Fix custom client si possible
4. Sinon: Document limitations, defer to future

---

## 📝 Lessons Learned

### Ce Qui A Bien Fonctionné
1. ✅ **Docling stable** (malgré tqdm occasional glitch)
2. ✅ **Neo4j robuste** (4h uptime, pas de crash)
3. ✅ **Logs détaillés** aidant au debugging (chunk par chunk)
4. ✅ **Architecture singleton** Graphiti bien conçue

### Ce Qui A Mal Tourné
1. ❌ **Assumption gpt-5-nano "just works"** avec Graphiti
2. ❌ **Custom client introduit complexity** sans validation tests
3. ❌ **Pas de rollback plan** quand custom client failed
4. ❌ **Vector dimension non vérifié** avant ingestion

### Actions Correctives Futures
1. 📋 **Toujours tester modèles OpenAI** avec Graphiti examples d'abord
2. 📋 **Écrire tests unitaires** pour custom integrations
3. 📋 **Documenter assumptions** (vector dims, API parameters)
4. 📋 **Avoir fallback plan** (ex: gpt-4o-mini as backup)

---

## 📚 Références

### Fichiers Clés Modifiés
- `backend/app/integrations/graphiti.py` (127 lignes)
- `backend/app/integrations/custom_llm_client.py` (108 lignes, nouveau)
- `backend/requirements.txt` (dependencies updated)
- `docker/docker-compose.dev.yml` (.env loading)

### Plans de Développement
- `Devplan/PHASE-0.9-GRAPHITI-IMPLEMENTATION.md` (objectifs)
- `Devplan/PHASE-0.8-NEO4J-IMPLEMENTATION.md` (Neo4j OK)
- `Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md` (Docling OK)

### Documentation Externe
- Graphiti 0.17.0 Docs: https://github.com/getzep/graphiti-core
- OpenAI gpt-5-nano: https://platform.openai.com/docs (rate limits)
- Neo4j Vector Indexes: https://neo4j.com/docs/

---

**Prepared by:** AI Assistant (Cursor)  
**Review Status:** Ready for User Review  
**Next Action:** User decision on Option A/B/C

