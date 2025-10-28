# ⚠️ STATUS REPORT: Problème Warm-up Docling

**Date:** 28 Octobre 2025, 21:19  
**Status:** ⚠️ BLOQUÉ  
**Priorité:** HAUTE

---

## 📋 RÉSUMÉ EXÉCUTIF

Le plan complet a été exécuté avec succès SAUF le warm-up Docling qui échoue systématiquement avec l'erreur `No module named 'integrations'` malgré plusieurs tentatives de fix.

---

## ✅ CE QUI A ÉTÉ FAIT

### Phase 1: Diagnostic Ollama ✅
- ✅ Ollama démarre correctement
- ✅ Modèle `qwen2.5:7b-instruct-q8_0` (8.1 GB) présent et installé
- ✅ API Ollama répond (`{"version":"0.12.6"}`)

### Phase 2: Fix Docker Compose ✅
- ✅ Healthcheck Ollama modifié:
  - `retries: 5 → 10`
  - `start_period: 60s` ajouté
- ✅ Dépendance backend → ollama changée:
  - `service_healthy → service_started`
  - Backend peut démarrer même si Ollama n'est pas "healthy"

### Phase 3: Logs de validation warm-up ✅
- ✅ Ajout de validation du singleton dans `warmup_docling.py`:
  ```python
  # Vérifie que DoclingSingleton._instance is not None
  ```

### Phase 4 & 5: Rebuild backend ✅
- ✅ Backend rebuild avec `--no-cache` (2 fois)
- ✅ Docker image à jour

---

## ❌ LE PROBLÈME

### Erreur Actuelle
```
2025-10-28 20:19:27,664 - ERROR - ❌ WARM-UP FAILED: No module named 'integrations'
```

### Fichier `backend/warmup_docling.py` (ligne 35)
```python
from app.integrations.dockling import DoclingSingleton
```

### Cause Racine
Le module `app.integrations` n'est **PAS accessible** depuis `warmup_docling.py` car ce script est exécuté **DEPUIS LA RACINE** (`/app/`) alors que le module est dans `/app/app/integrations/`.

### Structure actuelle
```
/app/
├── warmup_docling.py         ← Exécuté ici (workdir /app)
├── app/                       ← Module Python
│   └── integrations/
│       └── dockling.py        ← Cible
└── docker-entrypoint.sh
```

Le problème: `warmup_docling.py` est un **script Python indépendant** exécuté avec `python3 /app/warmup_docling.py`, donc l'import relatif `app.integrations` ne fonctionne PAS.

---

## 🎯 SOLUTIONS PROPOSÉES

### Solution A (RAPIDE): Désactiver le warm-up temporairement
**Avantage:** Permet de tester le pipeline immédiatement  
**Inconvénient:** Premier upload prendra 15 minutes  
**Impact:** MVP testable maintenant, optimisation plus tard

**Modification:**
```bash
# docker-entrypoint.sh - Ligne 12
export SKIP_WARMUP=true  # ← Ajouter cette ligne
```

### Solution B (PROPRE): Déplacer warmup dans le module Python
**Avantage:** Solution architecturalement correcte  
**Inconvénient:** Nécessite refactoring

**Structure proposée:**
```
/app/app/
├── warmup/
│   ├── __init__.py
│   └── docling.py       ← Code du warm-up ici
```

**Appel depuis entrypoint:**
```bash
python3 -m app.warmup.docling
```

### Solution C (IMMÉDIATE): Fix import path

**Modification `warmup_docling.py`:**
```python
import sys
sys.path.insert(0, '/app')  # Ajouter le chemin

from app.integrations.dockling import DoclingSingleton  # Maintenant ça marche
```

---

## 🚀 RECOMMANDATION

**Pour le test immédiat:**
1. **Appliquer Solution A** (SKIP_WARMUP=true)
2. **Tester l'ingestion avec `test.pdf`**
3. **Le premier upload prendra 10-15 minutes** (téléchargement models Docling)
4. **Les uploads suivants seront rapides** (<1 min car models cachés)

**Pour la production:**
- Implémenter Solution B (refactoring propre)

---

## 📊 ÉTAT ACTUEL DES SERVICES

```
Container rag-ollama    STARTED (pas healthy mais API fonctionne)
Container rag-neo4j     HEALTHY
Container rag-backend   STARTED (API prête malgré warm-up failed)
Container rag-frontend  STARTED
```

**Backend API:** http://localhost:8000/api/health  
**Frontend UI:** http://localhost:5173

---

## ✅ SYSTÈME FONCTIONNEL

**Malgré le warm-up failed, le système EST fonctionnel:**
- ✅ Backend API répond
- ✅ Neo4j connecté
- ✅ Indexes RAG créés
- ✅ Ollama accessible
- ⚠️ Docling téléchargera les models on-demand (premier upload = lent)

---

## 🎯 PROCHAINES ÉTAPES

**Choix 1: Tester maintenant (SKIP_WARMUP)**
1. Appliquer Solution A
2. Rebuild + restart
3. Tester ingestion avec `test.pdf`
4. Accepter 10-15 min pour le premier upload

**Choix 2: Fix propre d'abord (Solution C)**
1. Modifier `warmup_docling.py` avec `sys.path`
2. Rebuild + restart
3. Vérifier warm-up réussit
4. Tester ingestion

---

## 💡 DÉCISION ATTENDUE

**Question:** Quelle solution appliquer ?
- **A)** SKIP_WARMUP (test immédiat, optimisation plus tard)
- **C)** Fix sys.path (5 min, solution propre)
- **B)** Refactoring complet (20 min, architecture idéale)

