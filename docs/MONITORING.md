# 🔍 Monitoring & Scripts Guide

> **Purpose:** Documentation complète de tous les scripts de monitoring, debugging et testing  
> **Last Updated:** October 29, 2025, 08:30 CET  
> **Status:** 🟢 Production-Ready Monitoring System

**📚 Related Docs:**
- **[TESTING-LOG.md](TESTING-LOG.md)** - Historique des tests exécutés
- **[FIXES-LOG.md](FIXES-LOG.md)** - Tracker de tous les bugs et fixes

---

## 📋 Table of Contents

- [Vue d'Ensemble](#vue-densemble)
- [Scripts de Monitoring](#scripts-de-monitoring)
- [Scripts de Testing](#scripts-de-testing)
- [Scripts de Maintenance](#scripts-de-maintenance)
- [Commandes Docker Utiles](#commandes-docker-utiles)
- [Debugging Avancé](#debugging-avancé)
- [Best Practices](#best-practices)

---

## Vue d'Ensemble

### Architecture de Monitoring

```
Monitoring System
├── Real-Time Monitoring
│   ├── monitor_ingestion.sh    - Logs Graphiti en temps réel
│   └── monitor_ollama.sh        - Performance Ollama + Docker
├── Testing
│   ├── test_rag_query.sh        - Tests RAG query (bash)
│   └── test_rag_query.py        - Tests RAG query (Python)
└── Maintenance
    └── clean_neo4j.sh           - Nettoyage complet Neo4j
```

### Objectifs

✅ **Visibilité en temps réel** sur l'ingestion de documents  
✅ **Performance monitoring** pour Ollama et Docker  
✅ **Testing automatisé** pour le pipeline RAG  
✅ **Maintenance** de la base de données Neo4j  
✅ **Debugging** avec logs colorisés et filtrés

---

## Scripts de Monitoring

### 1. 🔄 monitor_ingestion.sh

**📍 Localisation:** `scripts/monitor_ingestion.sh`  
**🎯 Objectif:** Surveiller l'ingestion Graphiti en temps réel avec logs colorisés

#### Usage

```bash
# Surveiller toute l'activité Graphiti
./scripts/monitor_ingestion.sh

# Filtrer par upload_id spécifique
./scripts/monitor_ingestion.sh <upload_id>

# Exemple avec UUID
./scripts/monitor_ingestion.sh a1b2c3d4-e5f6-7890-abcd-1234567890ab
```

#### Ce qu'il fait

1. **Se connecte aux logs Docker** du container `rag-backend`
2. **Filtre les logs** avec patterns:
   - `diveteacher.graphiti` - Logs Graphiti
   - `diveteacher.processor` - Logs processor
   - `Claude Haiku` - Logs LLM
   - `Episode`, `Entity` - Logs entités/relations
   - `Step [0-9]/[0-9]` - Progression (Step 1/4, 2/4, etc.)
   - Émojis: `✅`, `❌`, `📊`, `🔧`, `📥`, `📝`

3. **Colorise les logs**:
   - 🟢 **Vert**: Lignes avec ✅ (succès)
   - 🔴 **Rouge**: Lignes avec ❌ (erreurs)
   - 🔵 **Bleu**: Lignes avec "Step" (progression)
   - 🟡 **Jaune**: Lignes avec "Graphiti" ou "Claude"

#### Exemple de sortie

```
🔍 Starting Real-Time Ingestion Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Monitoring Graphiti ingestion logs...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[upload_abc123] Step 1/4: Validation ✅
[upload_abc123] Step 2/4: Conversion 🔄
[upload_abc123] 🔧 Starting Graphiti ingestion...
[upload_abc123] 📥 Processing chunk 1/72...
[upload_abc123] ✅ Entity extracted: "Plongée Niveau 1"
[upload_abc123] Step 3/4: Chunking ✅
[upload_abc123] Step 4/4: Ingestion 🔄
[upload_abc123] 📊 Ingestion complete: 72 chunks → 45 entities
[upload_abc123] ✅ Document processing complete!
```

#### Quand l'utiliser

- ✅ Pendant l'upload d'un document
- ✅ Pour debugger des problèmes d'ingestion
- ✅ Pour vérifier la progression en temps réel
- ✅ Pour identifier des erreurs Graphiti/Claude

#### Limitations

- Nécessite `grep --line-buffered` (disponible sur macOS/Linux)
- Logs uniquement du container `rag-backend`
- Pas de persistance des logs (temps réel seulement)

---

### 2. 📊 monitor_ollama.sh

**📍 Localisation:** `scripts/monitor_ollama.sh`  
**🎯 Objectif:** Monitoring complet de la performance Ollama + Docker

#### Usage

```bash
# Monitoring avec backend par défaut (localhost:8000)
./scripts/monitor_ollama.sh

# Monitoring avec backend custom
./scripts/monitor_ollama.sh http://192.168.1.100:8000
```

#### Ce qu'il fait

**1. Docker Container Status** ✅
- Vérifie si le container `rag-ollama` est running
- Affiche le statut (Up X minutes, healthy/unhealthy)

**2. Docker Resource Usage** 📊
- Memory usage (current / limit)
- CPU percentage
- Network I/O
- Block I/O
- **Alerte**: Si memory > 14GB / 16GB → Warning

**3. Ollama API Status** 🔌
- Test de connexion à `http://localhost:11434/api/version`
- Vérifie que l'API répond

**4. Loaded Model Information** 🤖
- Liste des modèles chargés (`ollama list`)
- Pour chaque modèle:
  - Nom et version
  - Taille (GB)
  - Famille (Qwen, Mistral, etc.)
- **Validation**: Vérifie si Qwen 2.5 7B est chargé

**5. Backend API Health** 💚
- Test de connexion au backend FastAPI
- Vérifie `/api/health`
- Status, model loaded, health

**6. Quick Performance Benchmark** ⚡
- Test simple avec prompt "Hello"
- Mesure:
  - Tokens générés
  - Durée (secondes)
  - Tokens/seconde (tok/s)
- **Contexte local**: 10-15 tok/s (CPU) vs 40-60 tok/s (GPU production)

**7. Docker Desktop Configuration** 🐋
- Memory limit configuré
- Recommandations selon environnement

#### Exemple de sortie

```
=====================================================================
      Ollama Performance Monitor - Qwen 2.5 7B Q8_0
=====================================================================

1. Docker Container Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ollama container is running
   Status: Up 2 hours (healthy)

2. Docker Resource Usage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Memory: 8.7GiB / 16GiB
   CPU: 5.2%
   Network I/O: 1.2MB / 850KB
   Block I/O: 450MB / 120MB
   
   ✅ Memory usage is healthy (54% of limit)

3. Ollama API Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ollama API is responding
   Version: 0.1.17

4. Loaded Model Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Model: qwen2.5:7b-instruct-q8_0
   Size: 8.1 GB
   Family: qwen2.5
   
   ✅ Target model (Qwen 2.5 7B Q8_0) is loaded

5. Backend API Health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Backend API is healthy
   Model: qwen2.5:7b-instruct-q8_0
   Status: healthy

6. Quick Performance Benchmark
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 Running quick inference test...
   Tokens: 25
   Duration: 2.1s
   Performance: 11.9 tok/s
   
   ℹ️  Local Dev (CPU): 10-15 tok/s is NORMAL
   🚀 Production (GPU): Target 40-60 tok/s

7. Docker Desktop Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Docker Memory Limit: 16GB
   ✅ Sufficient for Qwen 2.5 7B Q8_0 (~10GB VRAM)
```

#### Quand l'utiliser

- ✅ Avant de tester le RAG query
- ✅ Pour vérifier la performance Ollama
- ✅ Pour debugger des problèmes de mémoire
- ✅ Pour valider que le bon modèle est chargé
- ✅ Pour identifier des bottlenecks

#### Limitations

- Nécessite `curl`, `jq`, `docker`
- Benchmark simple (pas de test RAG complet)
- Performance locale != production (CPU vs GPU)

---

## Scripts de Testing

### 3. 🧪 test_rag_query.sh

**📍 Localisation:** `scripts/test_rag_query.sh`  
**🎯 Objectif:** Tester le pipeline RAG query complet (bash, sans dépendances)

#### Usage

```bash
# Test avec backend par défaut (localhost:8000)
./scripts/test_rag_query.sh

# Test avec backend custom
./scripts/test_rag_query.sh http://192.168.1.100:8000
```

#### Ce qu'il fait

**Test 1: Health Check** ✅
- `GET /api/query/health`
- Vérifie:
  - Status: "healthy"
  - Model loaded
  - Response time < 1s

**Test 2: Non-Streaming Query** 📝
- `POST /api/query/`
- Payload:
  ```json
  {
    "question": "What is machine learning?",
    "facts": [
      "Machine learning is a subset of AI...",
      "ML algorithms can identify patterns..."
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }
  ```
- Vérifie:
  - Status 200
  - Response contient "answer"
  - Response contient "sources_count"

**Test 3: Streaming Query (SSE)** 🌊
- `POST /api/query/stream`
- Same payload
- Parse SSE events (`data: {...}`)
- Reconstruit la réponse token par token
- Vérifie:
  - Tokens reçus
  - Event "done" reçu
  - Stats (token_count, duration, tok/s)

**Test 4: Error Handling** ❌
- `POST /api/query/` avec payload invalide (facts vide)
- Vérifie:
  - Status 400
  - Error message approprié

#### Exemple de sortie

```
🧪 Testing RAG System at http://localhost:8000
==================================

Test 1: Health Check
--------------------
✅ Health check passed
   Status: healthy
   Model: qwen2.5:7b-instruct-q8_0

Test 2: Non-Streaming Query
-----------------------------
✅ Non-streaming query passed
   Answer received (125 characters)
   Sources: 2 facts used

Test 3: Streaming Query (SSE)
------------------------------
Machine learning is a subset of artificial intelligence...
[streaming response...]

📊 Stats:
{
  "token_count": 85,
  "duration_seconds": 7.2,
  "tokens_per_second": 11.8
}

✅ Streaming query test passed

Test 4: Error Handling
----------------------
✅ Error handling works correctly

==================================
✅ All 4 tests passed!
```

#### Quand l'utiliser

- ✅ Après avoir uploadé des documents
- ✅ Pour valider le pipeline RAG
- ✅ Pour tester les changements backend
- ✅ Pour vérifier la performance
- ✅ Avant de déployer en production

#### Limitations

- Nécessite `curl`, `jq`
- Pas de tests avec knowledge graph réel
- Payload de test simple

---

### 4. 🐍 test_rag_query.py

**📍 Localisation:** `scripts/test_rag_query.py`  
**🎯 Objectif:** Tests RAG query avancés (Python, avec httpx)

#### Usage

```bash
# Installer httpx (si nécessaire)
pip install httpx

# Lancer les tests
python3 scripts/test_rag_query.py
```

#### Ce qu'il fait

Même tests que `test_rag_query.sh` mais:
- ✅ Code Python plus lisible
- ✅ Meilleure gestion des erreurs
- ✅ Stats détaillées
- ✅ Possibilité d'étendre avec pytest

#### Quand l'utiliser

- ✅ Pour des tests plus complexes
- ✅ Si bash n'est pas disponible
- ✅ Pour intégration CI/CD (future)

#### Limitations

- Nécessite Python + httpx
- Plus lourd que le script bash

---

## Scripts de Maintenance

### 5. 🧹 clean_neo4j.sh

**📍 Localisation:** `scripts/clean_neo4j.sh`  
**🎯 Objectif:** Nettoyage complet de Neo4j + Graphiti

#### Usage

```bash
# Nettoyer complètement Neo4j
./scripts/clean_neo4j.sh
```

#### Ce qu'il fait

**Étape 1: Vérification de l'état actuel** 🔍
- Connexion à Neo4j via backend Docker
- Compte total de nœuds
- Liste des types de nœuds (Episodes, Entities, etc.)
- Liste des types de relations

**Étape 2: Nettoyage** 🗑️
- **Supprime tous les nœuds et relations**: `MATCH (n) DETACH DELETE n`
- **Supprime les contraintes**: `DROP CONSTRAINT <name>`
- **Supprime les indexes**: `DROP INDEX <name>`

**Étape 3: Vérification finale** ✅
- Vérifie que count(nodes) = 0
- Vérifie que count(relations) = 0
- Affiche confirmation

#### Exemple de sortie

```
============================================================
🧹 NETTOYAGE COMPLET NEO4J + GRAPHITI
============================================================

📋 Étape 1: Vérification de l'état actuel...

🔍 Connexion à Neo4j...
📍 URI: bolt://neo4j:7688
👤 User: neo4j

📊 Nœuds avant nettoyage: 1247

📋 Types de nœuds présents:
   - ['Episode']: 72 nœuds
   - ['Entity']: 1125 nœuds
   - ['EpisodicNode']: 50 nœuds

📋 Types de relations présentes:
   - HAS_ENTITY: 2340 relations
   - RELATES_TO: 890 relations

============================================================
🗑️  DÉBUT DU NETTOYAGE
============================================================

🗑️  Suppression de tous les nœuds et relations...
   ✅ Tous les nœuds et relations supprimés

🗑️  Suppression des contraintes...
   - Suppression: entity_uuid_unique
   ✅ Contraintes supprimées

🗑️  Suppression des index...
   - Suppression: episode_content
   - Suppression: entity_name_idx
   ✅ Index supprimés

============================================================
📊 VÉRIFICATION FINALE
============================================================

📊 Nœuds après nettoyage: 0
📊 Relations après nettoyage: 0

============================================================
✅ NEO4J EST MAINTENANT COMPLÈTEMENT VIDE!
✅ PRÊT POUR DE NOUVEAUX TESTS!
============================================================
```

#### Quand l'utiliser

- ✅ Avant de recommencer les tests from scratch
- ✅ Après des tests avec données corrompues
- ✅ Pour nettoyer des anciennes ingestions
- ✅ Quand le knowledge graph est incohérent

#### ⚠️ ATTENTION

- **Destructif**: Supprime TOUTES les données Neo4j
- **Irréversible**: Pas de backup automatique
- **Impact**: Nécessite de ré-ingest tous les documents

---

## Commandes Docker Utiles

### Logs en temps réel

```bash
# Backend logs
docker logs -f rag-backend

# Ollama logs
docker logs -f rag-ollama

# Neo4j logs
docker logs -f rag-neo4j

# Frontend logs (si Docker)
docker logs -f rag-frontend
```

### Restart services

```bash
# Restart backend seul
docker compose -f docker/docker-compose.dev.yml restart backend

# Restart tous les services
docker compose -f docker/docker-compose.dev.yml restart

# Restart avec rebuild
docker compose -f docker/docker-compose.dev.yml up -d --build backend
```

### Stats Docker

```bash
# Stats en temps réel
docker stats

# Stats one-shot
docker stats --no-stream

# Stats specific container
docker stats rag-ollama --no-stream
```

### Accès shell container

```bash
# Backend shell
docker exec -it rag-backend bash

# Neo4j cypher-shell
docker exec -it rag-neo4j cypher-shell -u neo4j -p <password>

# Ollama shell
docker exec -it rag-ollama bash
```

---

## Debugging Avancé

### Debug Docling Conversion

```bash
# Logs Docling seulement
docker logs -f rag-backend | grep -E "Docling|dockling|Conversion"

# Vérifier warm-up
docker logs rag-backend | grep -E "WARMING|DOCLING|Singleton"

# Vérifier cache modèles
docker exec rag-backend ls -lh /root/.cache/
```

### Debug Graphiti Ingestion

```bash
# Logs Graphiti + Claude
docker logs -f rag-backend | grep -E "Graphiti|Claude|Episode|Entity"

# Logs avec upload_id
docker logs -f rag-backend | grep "upload_abc123"

# Ou utiliser le script
./scripts/monitor_ingestion.sh upload_abc123
```

### Debug Ollama Performance

```bash
# Vérifier modèles chargés
docker exec rag-ollama ollama list

# Test inference direct
docker exec rag-ollama ollama run qwen2.5:7b-instruct-q8_0 "Hello"

# Stats Docker
docker stats rag-ollama --no-stream

# Ou utiliser le script
./scripts/monitor_ollama.sh
```

### Debug Neo4j Queries

```bash
# Compter nœuds
docker exec rag-backend python3 -c "
from app.integrations.neo4j import neo4j_client
result = neo4j_client.driver.execute_query('MATCH (n) RETURN count(n) as count')
print(result.records[0]['count'])
"

# Lister types
docker exec rag-backend python3 -c "
from app.integrations.neo4j import neo4j_client
result = neo4j_client.driver.execute_query('MATCH (n) RETURN DISTINCT labels(n) as labels')
for record in result.records:
    print(record['labels'])
"
```

---

## Best Practices

### Monitoring

1. **✅ Utiliser les scripts fournis** plutôt que `docker logs` brut
2. **✅ Filtrer par upload_id** pour debugging spécifique
3. **✅ Monitorer la mémoire** avec `monitor_ollama.sh` régulièrement
4. **✅ Vérifier warm-up** après chaque rebuild backend

### Testing

1. **✅ Tester après chaque changement** backend
2. **✅ Valider performance** avec benchmarks
3. **✅ Nettoyer Neo4j** avant tests importants
4. **✅ Documenter les résultats** dans TESTING-LOG.md

### Debugging

1. **✅ Commencer par les scripts** avant logs bruts
2. **✅ Isoler le problème** (Docling? Graphiti? Ollama?)
3. **✅ Vérifier configuration** (.env, docker-compose)
4. **✅ Redémarrer services** si comportement erratique

### Maintenance

1. **✅ Nettoyer Neo4j régulièrement** pendant dev
2. **✅ Surveiller taille Docker volumes**
3. **✅ Backup .env avant changements**
4. **✅ Documenter changements** dans TESTING-LOG.md

---

## Références

- **[TESTING-LOG.md](TESTING-LOG.md)** - Historique des tests et résultats
- **[TIMEOUT-FIX-GUIDE.md](TIMEOUT-FIX-GUIDE.md)** - Fix timeout Docling
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture système
- **[API.md](API.md)** - Documentation API endpoints
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Guide dépannage

---

**🎯 Next:** Voir [TESTING-LOG.md](TESTING-LOG.md) pour l'historique complet des tests

