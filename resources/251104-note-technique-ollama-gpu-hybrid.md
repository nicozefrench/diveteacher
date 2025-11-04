# Note Technique - Résolution Problème GPU Ollama (Dev Local Mac → Cloud)

**Date:** 2025-11-04  
**Contexte:** Développement système RAG avancé avec migration prévue vers DigitalOcean GPU Droplet  
**Assistant:** Claude Sonnet 4.5

---

## 🚨 PROBLÈME IDENTIFIÉ

### Situation Actuelle
- **Environnement:** Mac M1 Max avec GPU Metal intégré
- **Configuration:** Ollama dans Docker via `diveteacher-ollama:latest`
- **Résultat:** `ollama ps` montre **"100% CPU"** au lieu de **"100% GPU"**

### Diagnostic
```bash
docker exec rag-ollama ollama ps
# OUTPUT: PROCESSOR: 100% CPU ❌
# ATTENDU: PROCESSOR: 100% GPU ✅
```

### Cause Racine
**Docker Desktop sur Mac ne supporte PAS le GPU passthrough pour Metal.**

C'est une **limitation connue et non-contournable** de Docker Desktop sur macOS:
- Les containers Docker ne peuvent pas accéder au GPU Metal
- Aucune configuration Docker ne peut résoudre ce problème
- Même avec Rosetta, cela reste du CPU

**Impact:**
- Tests locaux **10-20x plus lents** qu'avec GPU
- Impossibilité de valider les performances réelles avant déploiement
- Cycles de développement rallentis

---

## ✅ SOLUTION RETENUE: Approche Hybride

### Principe
| Environnement | Ollama | Services RAG | Raison |
|---------------|--------|--------------|---------|
| **Dev Local** | Natif (hors Docker) | Docker | Performance Metal GPU |
| **Production** | Docker avec GPU | Docker | Cohérence infrastructure |

### Architecture de Communication

```
DEV LOCAL:
┌─────────────────┐
│ Ollama Natif    │ ← Installé via brew, tourne sur Mac
│ :11434 (Metal)  │
└────────┬────────┘
         │ HTTP API
         ↓
┌─────────────────────────────────┐
│ Docker Services                 │
│ ├─ Backend → http://host.docker.internal:11434
│ ├─ Frontend                     │
│ └─ Neo4j/ChromaDB/etc           │
└─────────────────────────────────┘

PRODUCTION (DigitalOcean):
┌─────────────────────────────────┐
│ Docker Stack                    │
│ ├─ Ollama → http://ollama:11434 (NVIDIA GPU)
│ ├─ Backend → http://ollama:11434
│ ├─ Frontend                     │
│ └─ Neo4j/ChromaDB/etc           │
└─────────────────────────────────┘
```

---

## 🔑 POINTS CLÉS - Pourquoi Cela Fonctionne

### 1. API Ollama Identique
L'API REST d'Ollama est **strictement identique** qu'elle tourne:
- En natif sur Mac
- Dans Docker CPU
- Dans Docker GPU

**Même endpoints, même format JSON, même comportement.**

### 2. Abstraction par URL
Votre backend ne doit connaître qu'**une seule variable d'environnement:**
```bash
OLLAMA_BASE_URL=<url_ollama>
```

Cette URL change selon l'environnement:
- Dev: `http://host.docker.internal:11434` (pointe vers Mac host)
- Prod: `http://ollama:11434` (pointe vers container Docker)

**Zéro modification de code nécessaire.**

### 3. Docker Compose Overrides
Utilisation du pattern standard Docker Compose avec fichiers multiples:
- `docker-compose.yml` → Configuration commune (backend, frontend, DBs)
- `docker-compose.dev.yml` → Overrides dev (pas de service Ollama)
- `docker-compose.prod.yml` → Overrides prod (service Ollama avec GPU)

**Une seule commande différente:**
```bash
# Dev
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Prod
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## 🛠️ MISE EN ŒUVRE (Guidelines Génériques)

### Phase 1: Installation Locale

1. **Installer Ollama nativement**
   ```bash
   brew install ollama
   ollama serve  # Lance le serveur sur :11434
   ollama pull <votre_modele>
   ```

2. **Vérifier GPU**
   ```bash
   ollama ps  # Doit montrer "100% GPU" avec Metal
   ```

### Phase 2: Adapter Docker Compose

1. **Extraire service Ollama dans un override**
   - Créer `docker-compose.dev.yml` SANS service Ollama
   - Créer `docker-compose.prod.yml` AVEC service Ollama + config GPU

2. **Configurer l'accès host depuis Docker (dev)**
   ```yaml
   # docker-compose.dev.yml
   services:
     backend:  # ou votre service qui appelle Ollama
       extra_hosts:
         - "host.docker.internal:host-gateway"
       environment:
         - OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```

3. **Configurer accès container (prod)**
   ```yaml
   # docker-compose.prod.yml
   services:
     ollama:
       image: ollama/ollama:latest
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: all
                 capabilities: [gpu]
     
     backend:
       environment:
         - OLLAMA_BASE_URL=http://ollama:11434
       depends_on:
         - ollama
   ```

### Phase 3: Variables d'Environnement

Créer deux fichiers `.env`:

```bash
# .env.dev (local)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# .env.prod (cloud)
OLLAMA_BASE_URL=http://ollama:11434
```

**Important:** Tous vos services doivent lire `OLLAMA_BASE_URL` depuis l'environnement, jamais en dur.

---

## 📊 WORKFLOW QUOTIDIEN

### Développement Local
```bash
# Terminal 1: Ollama natif
ollama serve

# Terminal 2: Services Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up
```

### Test Pre-Production (optionnel)
```bash
# Teste la config prod en local (CPU mais valide la config)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Déploiement Production
```bash
# Sur votre droplet DigitalOcean
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d
```

---

## ⚠️ POINTS D'ATTENTION

### Ce Qui Ne Change Pas
- ✅ Votre code backend/frontend (zéro ligne à modifier)
- ✅ Les appels API à Ollama (même format)
- ✅ Les modèles utilisés (même compatibilité)
- ✅ La logique RAG (identique)

### Ce Qui Change
- 🔄 **Uniquement** la variable `OLLAMA_BASE_URL`
- 🔄 **Uniquement** le fichier docker-compose utilisé

### Prérequis Cloud
Avant migration DigitalOcean, vérifier:
1. **NVIDIA drivers** installés: `nvidia-smi`
2. **NVIDIA Docker runtime** configuré: `docker run --gpus all nvidia/cuda:11.8.0-base nvidia-smi`
3. **Suffisamment de VRAM** pour votre modèle (ex: 7B → ~8GB VRAM)

Sur les **GPU Droplets DigitalOcean**, tout est pré-configuré.

---

## 🎯 VALIDATION MIGRATION

### Checklist Pré-Migration
- [ ] Test local avec docker-compose.prod.yml (CPU, vérifie config)
- [ ] Variables d'environnement prod configurées (passwords, secrets)
- [ ] GPU Droplet provisionné et accessible SSH
- [ ] `nvidia-smi` fonctionne sur le droplet
- [ ] `docker --gpus` fonctionne sur le droplet

### Checklist Post-Déploiement
```bash
# Sur le droplet, après déploiement
docker ps  # Tous les containers running?
docker exec rag-ollama ollama ps  # Affiche "100% GPU"?
nvidia-smi  # GPU utilisé par Ollama?
curl http://localhost:11434/api/tags  # API répond?
```

Si `ollama ps` montre **"100% GPU"** → ✅ Migration réussie!

---

## 💡 POURQUOI CETTE APPROCHE EST SÛRE

### 1. Pattern Standard
C'est une pratique **commune** en développement cloud:
- Bases de données en Docker, cache Redis en local pour certains
- Services lourds (ML, GPU) souvent natifs en dev pour performance
- Abstractions par variables d'environnement = best practice

### 2. Même Interface, Implémentation Différente
Architecture **hexagonale** en pratique:
- Votre code dépend de l'**interface** Ollama API
- Pas de l'**implémentation** (natif vs Docker)

### 3. Testable
Vous pouvez tester la config prod **avant déploiement**:
```bash
docker-compose -f docker-compose.prod.yml up
```
Tourne sur CPU mais valide networking, variables, dépendances.

### 4. Rollback Facile
Si problème en prod, rollback = **zéro code change**, juste env vars.

---

## 🚀 ALTERNATIVES NON-RECOMMANDÉES

### ❌ Tout en Docker (Ollama CPU) en Dev
**Problème:** Tests 10-20x plus lents, impossible de valider perf réelles

### ❌ Développer Directement sur GPU Cloud
**Problème:** Coûts élevés, latence réseau, pas de dev offline

### ❌ Attendre Docker Desktop GPU Support
**Problème:** Pas de timeline Apple/Docker, peut ne jamais arriver

---

## 📚 RESSOURCES COMPLÉMENTAIRES

### Docker Compose Overrides
- https://docs.docker.com/compose/multiple-compose-files/

### Ollama API Documentation
- https://github.com/ollama/ollama/blob/main/docs/api.md

### Docker GPU Support (NVIDIA)
- https://docs.docker.com/config/containers/resource_constraints/#gpu

### DigitalOcean GPU Droplets
- https://docs.digitalocean.com/products/droplets/how-to/gpu/

---

## 🎓 APPRENTISSAGES POUR SONNET 4.5

### Contexte Utilisateur
- Dev système RAG avancé sur Mac M1 Max
- Stack: Ollama (7B Q8), Neo4j, Backend/Frontend custom
- Cible: DigitalOcean GPU Droplet
- Problème: Ollama en Docker = CPU only sur Mac

### Solution Appliquée
- **Approche hybride** avec abstractions propres
- **Zéro impact** sur le code métier
- **Pattern standard** Docker Compose overrides
- **Migration sans friction** via variables d'environnement

### Principe Architectural Clé
> "Dépendre d'interfaces (API Ollama), pas d'implémentations (natif/Docker)"

Cette note devrait servir de référence pour des problématiques similaires GPU/ML en développement cross-platform.

---

**📝 Note:** Cette approche est **recommandée** et **standard** dans l'industrie pour le développement ML/GPU sur Mac avec déploiement cloud Linux. Elle n'introduit aucun risque technique lors de la migration.