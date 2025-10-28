# 🔧 PLAN COMPLET: Fix Ollama + Warm-up Docling

**Date:** 28 Octobre 2025  
**Objectif:** Réparer Docker Ollama (modèle Qwen2.5-7B-Instruct-Q8_0) + Valider warm-up Docling  
**Status:** PLAN PRÊT - EN ATTENTE D'EXÉCUTION

---

## 📋 TABLE DES MATIÈRES

1. [Analyse de la Situation](#analyse-de-la-situation)
2. [Problèmes Identifiés](#problèmes-identifiés)
3. [Plan de Fix](#plan-de-fix)
4. [Validation Warm-up Docling](#validation-warm-up-docling)
5. [Checklist de Validation](#checklist-de-validation)

---

## 🔍 ANALYSE DE LA SITUATION

### État Actuel Docker Compose

**Fichier:** `docker/docker-compose.dev.yml`

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: rag-ollama
  environment:
    - OLLAMA_HOST=0.0.0.0:11434
    - OLLAMA_ORIGINS=*
    - OLLAMA_KEEP_ALIVE=5m
    - OLLAMA_MAX_LOADED_MODELS=1
    - OLLAMA_NUM_PARALLEL=4
    - OLLAMA_MAX_QUEUE=128
  deploy:
    resources:
      limits:
        memory: 16G
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
    interval: 10s
    timeout: 5s
    retries: 5
  depends_on:
    ollama:
      condition: service_healthy  # ← Backend dépend d'Ollama
```

### Configuration Backend

**Fichier:** `backend/app/core/config.py`

```python
OLLAMA_BASE_URL: str = "http://ollama:11434"
OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q8_0"  # Q8_0 pour qualité RAG optimale
DOCLING_TIMEOUT: int = 900  # 15 minutes
```

### État Warm-up Docling

**Fichier:** `backend/warmup_docling.py`

✅ **Fix déjà implémenté**: Utilise `DoclingSingleton.get_converter()` pour initialiser le singleton directement.

```python
from integrations.dockling import DoclingSingleton

def warmup_docling_models():
    converter = DoclingSingleton.get_converter()  # ✅ Initialise singleton
    logger.info("✅ DocumentConverter initialized - models cached!")
```

---

## ⚠️ PROBLÈMES IDENTIFIÉS

### Problème 1: Ollama Unhealthy

**Symptôme:**
```
dependency failed to start: container rag-ollama is unhealthy
```

**Causes possibles:**
1. **Modèle non téléchargé**: Qwen2.5:7b-instruct-q8_0 n'existe pas dans le container
2. **Healthcheck trop rapide**: 10s interval insuffisant pour premier démarrage
3. **Erreur de nom de modèle**: Format incorrect ou tag manquant

**Diagnostic:**
```bash
# Vérifier si Ollama démarre
docker logs rag-ollama

# Vérifier si le modèle existe
docker exec rag-ollama ollama list

# Tester l'API
docker exec rag-ollama curl http://localhost:11434/api/version
```

### Problème 2: Backend dépend d'Ollama mais Ollama n'est pas critique pour l'ingestion

**Impact:**
- Si Ollama est unhealthy, le backend ne démarre pas
- Mais Ollama n'est utilisé que pour les requêtes RAG (downstream)
- L'ingestion (upstream) fonctionne sans Ollama

**Recommandation Best Practice (Guide Ollama):**
- Ollama devrait être optionnel pour le démarrage du backend
- Seul le endpoint `/api/query` nécessite Ollama

### Problème 3: Warm-up Docling non vérifié dans les logs

**Impact:**
- On ne sait pas si le warm-up s'exécute correctement
- Pas de confirmation visuelle que les modèles Docling sont en cache

---

## 🔧 PLAN DE FIX

### Phase 1: Diagnostic Ollama (5 min)

**Objectif:** Identifier pourquoi Ollama est unhealthy

#### Étape 1.1: Vérifier les logs Ollama

```bash
# Arrêter tous les services
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml down

# Démarrer seulement Ollama
docker compose -f docker/docker-compose.dev.yml up ollama -d

# Surveiller les logs
docker logs -f rag-ollama
```

**Vérifications:**
- [ ] Ollama démarre sans erreur
- [ ] API répond sur `/api/version`
- [ ] Aucune erreur de permission ou réseau

#### Étape 1.2: Vérifier le modèle

```bash
# Attendre 30s pour que Ollama soit prêt
sleep 30

# Lister les modèles installés
docker exec rag-ollama ollama list

# Si vide, le modèle n'est pas téléchargé
```

**Résultat attendu:**
```
NAME                            ID              SIZE      MODIFIED
qwen2.5:7b-instruct-q8_0       abc123          7.87 GB   X hours ago
```

**Si le modèle n'existe pas:**
```bash
# Pull le modèle (peut prendre 10-20 min)
docker exec rag-ollama ollama pull qwen2.5:7b-instruct-q8_0
```

#### Étape 1.3: Tester le healthcheck

```bash
# Tester manuellement
docker exec rag-ollama curl -f http://localhost:11434/api/version

# Résultat attendu: {"version":"0.5.x"}
```

---

### Phase 2: Fix Docker Compose (10 min)

**Objectif:** Corriger la configuration Ollama et dépendances

#### Fix 2.1: Augmenter le délai healthcheck

**Problème:** 10s est trop court pour le premier démarrage d'Ollama.

**Solution:**

```yaml
# docker/docker-compose.dev.yml
ollama:
  # ... (config existante)
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
    interval: 10s
    timeout: 5s
    retries: 10        # ← Augmenter de 5 à 10 (100s total)
    start_period: 60s  # ← Ajouter période de grâce (60s avant de compter les échecs)
```

**Justification (Best Practices Guide):**
- Premier démarrage Ollama: 20-30s
- Chargement initial du modèle: peut prendre 1-2 min
- `start_period: 60s` = le healthcheck ne compte pas comme échec pendant 60s

#### Fix 2.2: Rendre Ollama optionnel pour le backend (RECOMMANDÉ)

**Problème:** Backend ne peut pas démarrer si Ollama est unhealthy, mais Ollama n'est nécessaire que pour `/api/query`.

**Solution Option A (Rapide):** Supprimer la dépendance stricte

```yaml
# docker/docker-compose.dev.yml
backend:
  # ... (config existante)
  depends_on:
    neo4j:
      condition: service_healthy
    # REMOVED: ollama dependency
    # Ollama est optionnel - seulement pour RAG query
```

**Solution Option B (Meilleure):** Dépendance conditionnelle

```yaml
backend:
  depends_on:
    neo4j:
      condition: service_healthy
    ollama:
      condition: service_started  # ← Started, pas healthy
```

**Recommandation:** Utiliser **Option B** pour MVP (le backend attend que Ollama démarre, mais pas qu'il soit healthy).

#### Fix 2.3: Pre-load du modèle Qwen (OPTIONNEL mais RECOMMANDÉ)

**Problème:** Le modèle doit être téléchargé manuellement ou lors du premier appel.

**Solution:** Service d'initialisation

```yaml
# docker/docker-compose.dev.yml
services:
  # ... (ollama service)
  
  # Service d'initialisation Ollama (run once)
  ollama-init:
    image: ollama/ollama:latest
    container_name: rag-ollama-init
    depends_on:
      ollama:
        condition: service_started
    entrypoint: /bin/sh
    command: >
      -c "
      echo '⏳ Waiting for Ollama to be ready...';
      sleep 30;
      echo '📥 Pulling Qwen2.5-7B-Instruct-Q8_0...';
      ollama pull qwen2.5:7b-instruct-q8_0;
      echo '✅ Model ready!';
      ollama list;
      "
    environment:
      - OLLAMA_HOST=ollama:11434
    restart: "no"  # Run once only
```

**Note:** Ce service se termine après le pull du modèle. Il ne bloque pas le démarrage des autres services.

---

### Phase 3: Validation Configuration Backend (5 min)

**Objectif:** Vérifier que le backend utilise la bonne config Ollama

#### Étape 3.1: Vérifier les variables d'environnement

```bash
# Vérifier que le modèle est bien configuré
docker exec rag-backend env | grep OLLAMA

# Résultat attendu:
# OLLAMA_BASE_URL=http://ollama:11434
# OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
```

#### Étape 3.2: Tester le LLM provider

```bash
# Tester le healthcheck du query endpoint
curl http://localhost:8000/api/query/health | jq

# Résultat attendu:
# {
#   "status": "healthy",
#   "provider": "ollama",
#   "model": "qwen2.5:7b-instruct-q8_0",
#   "test_response": "..."
# }
```

#### Étape 3.3: Vérifier les logs backend

```bash
# Chercher les erreurs Ollama
docker logs rag-backend 2>&1 | grep -i ollama

# Chercher les erreurs de connection
docker logs rag-backend 2>&1 | grep -E "connection|refused|timeout"
```

---

## ✅ VALIDATION WARM-UP DOCLING

### Objectif: Vérifier que le warm-up Docling fonctionne correctement

#### Étape 4.1: Ajouter des logs de validation dans warm-up

**Problème actuel:** Pas assez de logs pour confirmer que le singleton est bien initialisé.

**Solution:**

```python
# backend/warmup_docling.py (AMÉLIORATION)

def warmup_docling_models():
    """
    Download and cache Docling models before first document processing
    This prevents timeout issues during the first upload
    """
    logger.info("=" * 60)
    logger.info("🔥 WARMING UP DOCLING MODELS")
    logger.info("=" * 60)
    
    try:
        # Import singleton
        logger.info("📦 Importing DoclingSingleton...")
        from integrations.dockling import DoclingSingleton
        
        logger.info("✅ DoclingSingleton imported successfully")
        
        # ═══════════════════════════════════════════════════════════
        # CRITICAL: Initialize the SINGLETON directly
        # ═══════════════════════════════════════════════════════════
        logger.info("🔄 Initializing DocumentConverter SINGLETON...")
        logger.info("⏳ This may take several minutes on first run...")
        logger.info("📝 Config: OCR=True, Tables=True, Mode=ACCURATE")
        logger.info("")
        
        # This initializes the singleton with the EXACT config used in production
        converter = DoclingSingleton.get_converter()
        
        logger.info("✅ DocumentConverter SINGLETON initialized!")
        logger.info("")
        
        # ═══════════════════════════════════════════════════════════
        # VALIDATION: Verify singleton is properly initialized
        # ═══════════════════════════════════════════════════════════
        logger.info("🔍 VALIDATING SINGLETON STATE:")
        
        # Check if singleton instance exists
        from integrations.dockling import DoclingSingleton as Singleton
        if Singleton._instance is not None:
            logger.info("✅ Singleton._instance is NOT None (GOOD)")
            logger.info(f"✅ Singleton type: {type(Singleton._instance)}")
        else:
            logger.warning("⚠️  Singleton._instance is None (BAD - should not happen)")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 DOCLING WARM-UP COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("ℹ️  Models are now cached and ready for use")
        logger.info("ℹ️  Subsequent document processing will be fast")
        logger.info("ℹ️  Singleton is initialized and shared across requests")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ WARM-UP FAILED: {e}")
        logger.error("=" * 60)
        logger.error("")
        logger.error("⚠️  Document processing may be slower on first upload")
        logger.error("⚠️  Models will be downloaded on-demand")
        logger.error("")
        return False
```

#### Étape 4.2: Vérifier les logs du warm-up

```bash
# Rebuild backend avec les nouveaux logs
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml build backend --no-cache

# Restart backend et surveiller le warm-up
docker compose -f docker/docker-compose.dev.yml up backend -d
docker logs -f rag-backend 2>&1 | grep -E "WARMING|DOCLING|Singleton|✅|❌|🔥|🎉"
```

**Résultat attendu (warm-up réussi):**
```
🔥 WARMING UP DOCLING MODELS
📦 Importing DoclingSingleton...
✅ DoclingSingleton imported successfully
🔄 Initializing DocumentConverter SINGLETON...
⏳ This may take several minutes on first run...
📝 Config: OCR=True, Tables=True, Mode=ACCURATE
✅ DocumentConverter SINGLETON initialized!
🔍 VALIDATING SINGLETON STATE:
✅ Singleton._instance is NOT None (GOOD)
✅ Singleton type: <class 'docling.document_converter.DocumentConverter'>
🎉 DOCLING WARM-UP COMPLETE!
ℹ️  Models are now cached and ready for use
ℹ️  Subsequent document processing will be fast
ℹ️  Singleton is initialized and shared across requests
```

**Résultat attendu (si models déjà en cache - RAPIDE ~3s):**
```
🔥 WARMING UP DOCLING MODELS
📦 Importing DoclingSingleton...
✅ DoclingSingleton imported successfully
🔄 Initializing DocumentConverter SINGLETON...
✅ DocumentConverter SINGLETON initialized!
🔍 VALIDATING SINGLETON STATE:
✅ Singleton._instance is NOT None (GOOD)
🎉 DOCLING WARM-UP COMPLETE!
```

**Si échec:**
```
🔥 WARMING UP DOCLING MODELS
📦 Importing DoclingSingleton...
❌ WARM-UP FAILED: [error message]
⚠️  Document processing may be slower on first upload
⚠️  Models will be downloaded on-demand
```

#### Étape 4.3: Vérifier que le singleton est réutilisé

**Objectif:** Confirmer que les appels suivants à `get_converter()` retournent l'instance en cache.

**Test:**
```bash
# Test 1: Upload un petit document (test.pdf 2 pages)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/test.pdf"

# Surveiller les logs - la conversion devrait être RAPIDE (pas de re-download)
docker logs -f rag-backend 2>&1 | grep -E "\[_convert_sync\]|Getting converter|Converter obtained"
```

**Résultat attendu:**
```
[upload_id] [_convert_sync] 🔄 START conversion: test.pdf
[upload_id] [_convert_sync] 📦 Getting converter singleton...
[upload_id] [_convert_sync] ✅ Converter obtained  # ← INSTANTANÉ si singleton fonctionne
[upload_id] [_convert_sync] 🚀 Starting conversion...
[upload_id] [_convert_sync] ✅ Conversion complete
```

**Si le singleton ne fonctionne pas (BAD):**
```
[upload_id] [_convert_sync] 📦 Getting converter singleton...
Fetching 9 files: 100%|██████████| 9/9 [00:17<00:00, 1.90s/it]  # ← Re-download !
[upload_id] [_convert_sync] ✅ Converter obtained  # ← Trop lent
```

---

## 📋 CHECKLIST DE VALIDATION

### Pre-Flight Checks

- [ ] Git status clean (ou commits sauvegardés)
- [ ] Docker Desktop running avec 16GB RAM alloué
- [ ] Ports disponibles: 7687, 11434, 8000, 5173
- [ ] Fichier `.env` présent avec `NEO4J_PASSWORD` et `DOCLING_TIMEOUT=900`

### Phase 1: Diagnostic Ollama

- [ ] Ollama démarre sans erreur
- [ ] API `/api/version` répond
- [ ] Modèle `qwen2.5:7b-instruct-q8_0` est listé
- [ ] Test `ollama run qwen2.5:7b-instruct-q8_0` fonctionne

### Phase 2: Docker Compose

- [ ] `start_period: 60s` ajouté au healthcheck Ollama
- [ ] `retries: 10` ajouté au healthcheck Ollama
- [ ] Dépendance backend → ollama modifiée en `service_started` (ou supprimée)
- [ ] (Optionnel) Service `ollama-init` ajouté pour pre-load

### Phase 3: Backend Config

- [ ] Variable `OLLAMA_BASE_URL=http://ollama:11434` confirmée
- [ ] Variable `OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0` confirmée
- [ ] Healthcheck `/api/query/health` retourne `status: healthy`
- [ ] Logs backend sans erreur Ollama

### Phase 4: Warm-up Docling

- [ ] Logs de validation ajoutés dans `warmup_docling.py`
- [ ] Backend rebuild avec `--no-cache`
- [ ] Logs warm-up montrent `✅ Singleton._instance is NOT None`
- [ ] Logs warm-up montrent `🎉 DOCLING WARM-UP COMPLETE!`
- [ ] Premier upload test.pdf : conversion rapide (~10s, pas de re-download)
- [ ] Logs `_convert_sync` montrent `✅ Converter obtained` instantanément

---

## 🚀 EXÉCUTION DU PLAN

### Commandes Résumées

```bash
# 1. Arrêter tous les services
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml down

# 2. Démarrer Ollama seul et diagnostiquer
docker compose -f docker/docker-compose.dev.yml up ollama -d
sleep 30
docker exec rag-ollama ollama list

# 3. Si modèle manquant, le télécharger
docker exec rag-ollama ollama pull qwen2.5:7b-instruct-q8_0

# 4. Appliquer les fixes Docker Compose (éditer le fichier)
# - Ajouter start_period: 60s
# - Augmenter retries: 10
# - Modifier depends_on: service_started

# 5. Appliquer les logs de validation warm-up (éditer warmup_docling.py)

# 6. Rebuild backend
docker compose -f docker/docker-compose.dev.yml build backend --no-cache

# 7. Restart tous les services
docker compose -f docker/docker-compose.dev.yml up -d

# 8. Surveiller les logs warm-up
docker logs -f rag-backend 2>&1 | grep -E "WARMING|DOCLING|Singleton|✅|❌|🔥|🎉"

# 9. Tester Ollama
curl http://localhost:8000/api/query/health | jq

# 10. Tester l'ingestion avec test.pdf
curl -X POST http://localhost:8000/api/upload -F "file=@TestPDF/test.pdf"
docker logs -f rag-backend 2>&1 | grep -E "\[_convert_sync\]|Getting converter"
```

---

## 📝 NOTES IMPORTANTES

### Best Practices Ollama (depuis le guide)

1. **Context Window:** Qwen2.5 supporte jusqu'à 128K tokens, mais on utilise 4096 pour l'équilibre performance/mémoire
2. **Temperature:** 0.7 est optimal pour RAG (balance créativité/précision)
3. **Model Tag:** `qwen2.5:7b-instruct-q8_0` est le format correct pour Q8_0
4. **First Load:** Le premier chargement du modèle peut prendre 1-2 min (10GB en VRAM)
5. **Healthcheck:** `/api/version` est plus fiable que `/api/tags` (ne nécessite pas de modèle chargé)

### Timing Attendu

- **Ollama startup:** 20-30s (premier démarrage)
- **Model pull:** 10-20 min (si non présent, 7.87 GB download)
- **Model load (first time):** 1-2 min (chargement en mémoire)
- **Warm-up Docling (first time):** 10-15 min (download models)
- **Warm-up Docling (cached):** 3-5s (instantané)
- **Subsequent conversions:** 10-30s (selon taille document)

### Critères de Succès

✅ **Ollama OK si:**
- Container `rag-ollama` status = `healthy`
- `ollama list` montre `qwen2.5:7b-instruct-q8_0`
- `/api/query/health` retourne `status: healthy`

✅ **Warm-up OK si:**
- Logs montrent `✅ Singleton._instance is NOT None`
- Logs montrent `🎉 DOCLING WARM-UP COMPLETE!`
- Premier upload: conversion en ~10s (pas de `Fetching 9 files`)

✅ **Système OK si:**
- Ingestion end-to-end réussit avec test.pdf (2 pages)
- Logs montrent toutes les étapes (validation → conversion → chunking → graphiti)
- Status API retourne `completed` après ~2-3 min

---

## 🛑 STOP CONDITION

**On s'arrête ici** quand:
1. ✅ Ollama est healthy et le modèle Qwen2.5-7B-Q8_0 est chargé
2. ✅ Backend démarre sans être bloqué par Ollama
3. ✅ Warm-up Docling logs montrent singleton initialisé
4. ✅ Warm-up logs montrent validation réussie

**On NE teste PAS l'ingestion complète** (l'utilisateur veut être présent pour ce test).

---

## 📌 PROCHAINES ÉTAPES (APRÈS VALIDATION)

1. Test ingestion end-to-end avec test.pdf (avec l'utilisateur)
2. Monitoring des logs en temps réel
3. Validation que le singleton Docling fonctionne (pas de re-download)
4. Debug si nécessaire

---

**FIN DU PLAN**

Ce plan est prêt à être exécuté. Tous les fichiers à modifier sont clairement identifiés. Les commandes sont prêtes à copier-coller.

