# Cloud Migration Guide - Ollama from Baremetal to Docker GPU

**Date:** November 5, 2025  
**Context:** Migration from Mac M1 Max (Metal GPU) to DigitalOcean GPU Droplet (NVIDIA)  
**Status:** 📋 **READY FOR FUTURE MIGRATION**

---

## 🎯 OBJECTIF

Migrer Ollama de l'architecture hybride actuelle (native Mac) vers une architecture full-Docker en production avec GPU NVIDIA, **sans modifier une seule ligne de code**.

---

## 📐 ARCHITECTURE ACTUELLE vs CIBLE

### Actuel (Dev Local - Mac M1 Max)

```
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
│ └─ Neo4j                        │
└─────────────────────────────────┘
```

**Performance:** 7-14 tok/s (Metal GPU)

### Cible (Production - DigitalOcean GPU Droplet)

```
┌─────────────────────────────────┐
│ Docker Stack                    │
│ ├─ Ollama → :11434 (NVIDIA GPU)│
│ ├─ Backend → http://ollama:11434
│ ├─ Frontend                     │
│ └─ Neo4j                        │
└─────────────────────────────────┘
```

**Performance attendue:** 40-60 tok/s (NVIDIA GPU)

---

## 🔑 POINTS CLÉS - Pourquoi C'est Sans Risque

### 1. API Ollama Identique

L'API REST d'Ollama est **strictement identique** qu'elle tourne:
- En natif sur Mac (Metal GPU)
- Dans Docker CPU
- Dans Docker GPU (NVIDIA)

**Même endpoints, même format JSON, même comportement.**

### 2. Abstraction par URL

Le backend ne connaît qu'**une seule variable d'environnement:**

```bash
OLLAMA_BASE_URL=<url_ollama>
```

Cette URL change selon l'environnement:
- **Dev:** `http://host.docker.internal:11434` (pointe vers Mac host)
- **Prod:** `http://ollama:11434` (pointe vers container Docker)

**Zéro modification de code nécessaire.**

### 3. Docker Compose Overrides

Pattern standard Docker Compose avec fichiers multiples:
- `docker-compose.dev.yml` → Overrides dev (pas de service Ollama)
- `docker-compose.prod.yml` → Overrides prod (service Ollama avec NVIDIA GPU)

---

## 🚀 CE QUI SE PASSE LORS DE LA MIGRATION CLOUD

### Changements Effectifs

#### 1. Ollama passe de Natif → Docker avec GPU

**Local (avant):**
```bash
# Terminal 1
ollama serve  # Natif sur Mac, port :11434, Metal GPU
```

**Cloud (après):**
```bash
# Tout dans Docker
docker compose -f docker-compose.prod.yml up -d
# Ollama dans container avec NVIDIA GPU, port :11434
```

#### 2. Une Seule Variable Change

**`.env` (local - actuel):**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
```

**`.env.prod` (cloud - futur):**
```bash
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
```

#### 3. Commande de Lancement Différente

**Local (actuel):**
```bash
# Terminal 1: Ollama natif
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS="*"
ollama serve

# Terminal 2: Services Docker
docker compose -f docker/docker-compose.dev.yml up -d
```

**Cloud (futur):**
```bash
# Une seule commande, tout dans Docker
docker compose -f docker/docker-compose.prod.yml up -d
```

### Ce Qui NE Change PAS

| Composant | Status |
|-----------|--------|
| **Code backend/frontend** | ✅ Identique (0 ligne modifiée) |
| **API calls à Ollama** | ✅ Identique (même format JSON) |
| **Modèles utilisés** | ✅ Identiques (qwen2.5:7b-instruct-q8_0) |
| **Base de données Neo4j** | ✅ Identique (même config) |
| **Logique RAG** | ✅ Identique |
| **Performance GPU** | ✅ GPU dans les 2 cas (Metal local → NVIDIA cloud) |

---

## 📋 PROCÉDURE DE MIGRATION (Step-by-Step)

### Phase 1: Préparation (Sur Mac Local)

#### Étape 1.1: Tester la Config Production Localement

```bash
# Tester docker-compose.prod.yml en local (CPU, mais valide la config)
docker compose -f docker/docker-compose.prod.yml up

# Vérifier que tous les services démarrent
# Note: Ollama sera sur CPU (pas de NVIDIA sur Mac), mais la config est validée
```

#### Étape 1.2: Pousser le Code

```bash
git push origin main
```

#### Étape 1.3: Configurer les Variables d'Environnement Production

Créer `.env.prod` avec:
```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<production-password>

# Gemini
GEMINI_API_KEY=<your-production-key>

# OpenAI
OPENAI_API_KEY=<your-production-key>

# Sentry
SENTRY_DSN_BACKEND=<your-production-dsn>
SENTRY_ENVIRONMENT=production
```

### Phase 2: Sur le Droplet DigitalOcean

#### Étape 2.1: Provisionner le GPU Droplet

**Specs Recommandées:**
| Setting | Value | Reason |
|---------|-------|--------|
| **Image** | Ubuntu 22.04 LTS x64 | Stable, Docker support |
| **Plan** | GPU-Optimized Droplets | Needed for Qwen 2.5 7B |
| **GPU Type** | Basic AI/ML (8GB VRAM min) | Qwen 2.5 7B Q8_0 needs ~8.1GB |
| **RAM** | 16GB minimum | Backend + Neo4j + Ollama |
| **CPU** | 4+ vCPUs | Processing documents |
| **Storage** | 100GB SSD | Models + Neo4j data |

**Coût estimé:** ~$100-150/month

#### Étape 2.2: Vérifier GPU Disponible

```bash
# Sur le droplet
nvidia-smi

# Doit afficher:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI XXX.XX       Driver Version: XXX.XX       CUDA Version: 11.8     |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# ...
```

#### Étape 2.3: Vérifier Docker GPU Support

```bash
# Tester nvidia-docker2
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi

# Doit afficher la même sortie nvidia-smi que ci-dessus
# Si erreur → installer nvidia-docker2:
# sudo apt-get install -y nvidia-docker2
# sudo systemctl restart docker
```

#### Étape 2.4: Cloner le Repo

```bash
git clone https://github.com/nicozefrench/diveteacher.git /opt/diveteacher
cd /opt/diveteacher
```

#### Étape 2.5: Configurer l'Environnement

```bash
# Copier le fichier .env.prod préparé
cp .env.prod .env

# OU créer directement sur le serveur
nano .env
# (coller les variables d'environnement production)
```

#### Étape 2.6: Lancer les Services

```bash
# Lancer en production (mode détaché)
docker compose -f docker/docker-compose.prod.yml up -d

# Suivre les logs
docker compose -f docker/docker-compose.prod.yml logs -f
```

#### Étape 2.7: Attendre le Démarrage d'Ollama

```bash
# Suivre les logs Ollama (~30-60 secondes)
docker logs -f rag-ollama-prod

# Doit afficher:
# time=... level=INFO source=routes.go msg="Listening on [::]:11434"
# time=... level=INFO source=types.go msg="inference compute" id=0 library=cuda ...
```

#### Étape 2.8: Charger le Modèle

```bash
# Pull le modèle dans le container Ollama
docker exec rag-ollama-prod ollama pull qwen2.5:7b-instruct-q8_0

# Durée: ~5-10 minutes (8.1 GB)
```

#### Étape 2.9: VÉRIFICATION CRITIQUE - GPU Active

```bash
docker exec rag-ollama-prod ollama ps

# ✅ SUCCÈS si affiche:
# NAME                        ID              SIZE      PROCESSOR           UNTIL
# qwen2.5:7b-instruct-q8_0    2d9500c94841    8.9 GB    100% GPU            ...
#                                                        ^^^^^^^^
#                                                        CRITICAL: Doit être "100% GPU"
```

**Si `ollama ps` affiche "100% GPU" → ✅ Migration réussie!**

**Si `ollama ps` affiche "100% CPU" → ❌ Problème GPU, voir Troubleshooting ci-dessous**

---

## ⏱️ TEMPS DE MIGRATION ESTIMÉ

| Étape | Durée |
|-------|-------|
| Setup droplet (si nouveau) | ~5 min |
| Transfert code | ~1 min |
| Configuration .env | ~2 min |
| Premier `docker compose up` | ~3-5 min (pull images) |
| Chargement modèle Ollama | ~5-10 min (8.1 GB) |
| Tests de validation | ~5 min |
| **TOTAL** | **~20-30 minutes** |

Redéploiements suivants: **~2-3 minutes** (juste rebuild backend si besoin).

---

## 🔧 TROUBLESHOOTING

### ❌ Si `ollama ps` montre CPU au lieu de GPU

**Cause:** Docker ne peut pas accéder au GPU NVIDIA.

**Fix:**
```bash
# 1. Vérifier NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi

# 2. Si erreur → installer nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 3. Re-tester
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi

# 4. Si OK, redémarrer Ollama
docker compose -f docker/docker-compose.prod.yml restart ollama
docker exec rag-ollama-prod ollama ps  # Doit montrer 100% GPU
```

### ❌ Si containers ne démarrent pas

```bash
# Checker les logs
docker compose -f docker/docker-compose.prod.yml logs

# Problème courant: ports déjà utilisés
sudo netstat -tulpn | grep :11434
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :7687

# Si port utilisé, tuer le processus:
sudo kill -9 <PID>
```

### ❌ Si backend ne peut pas joindre Ollama

```bash
# Vérifier networking Docker
docker network ls
docker network inspect diveteacher_default

# Tester depuis le backend
docker exec rag-backend curl http://ollama:11434/api/tags

# Si timeout → vérifier que ollama est dans le même réseau
docker compose -f docker/docker-compose.prod.yml ps
```

### ❌ Si performance < 40 tok/s (GPU sous-utilisé)

```bash
# Vérifier utilisation GPU
nvidia-smi

# Si GPU à 100% mais tok/s faible → VRAM insuffisante
# Vérifier mémoire disponible:
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# Si VRAM < 10GB libre → upgrader GPU Droplet
```

---

## ✅ CHECKLIST DE VALIDATION POST-MIGRATION

### Tests Automatiques

```bash
# 1. Tous les containers running
docker ps --format "table {{.Names}}\t{{.Status}}"
# ✅ Doit montrer: rag-backend-prod, rag-neo4j-prod, rag-ollama-prod (tous "Up")

# 2. GPU utilisé par Ollama
docker exec rag-ollama-prod ollama ps
# ✅ Doit afficher: PROCESSOR: 100% GPU

# 3. GPU visible par nvidia-smi
nvidia-smi
# ✅ Doit montrer Ollama dans la liste des processus GPU

# 4. API Ollama répond
curl http://localhost:11434/api/tags
# ✅ Doit retourner JSON avec la liste des modèles

# 5. Backend peut joindre Ollama
docker exec rag-backend curl http://ollama:11434/api/tags
# ✅ Doit retourner JSON

# 6. Health check backend
curl http://localhost:8000/api/health
# ✅ Doit retourner: {"status": "healthy", "ollama_model": "qwen2.5:7b-instruct-q8_0"}
```

### Test RAG Query

```bash
# Test simple RAG query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is DiveTeacher?",
    "stream": false
  }'

# ✅ Doit retourner une réponse JSON avec answer, num_sources, etc.
# ✅ Durée attendue: <20 secondes (GPU NVIDIA)
```

### Validation Performance

```bash
# Benchmark Ollama
time docker exec rag-ollama-prod ollama run qwen2.5:7b-instruct-q8_0 "Hello" --verbose 2>/dev/null

# ✅ Performance attendue: 40-60 tok/s (NVIDIA GPU)
# ❌ Si < 10 tok/s → GPU pas utilisé, revoir troubleshooting
```

---

## 📊 CHECKLIST COMPLÈTE

### Pré-Migration

- [ ] Test local avec `docker-compose.prod.yml` (valide config)
- [ ] Variables d'environnement `.env.prod` préparées
- [ ] GPU Droplet provisionné (8GB VRAM min)
- [ ] SSH access au droplet configuré
- [ ] `nvidia-smi` fonctionne sur le droplet
- [ ] `docker --gpus all` fonctionne sur le droplet

### Post-Déploiement

- [ ] Tous les containers running (`docker ps`)
- [ ] `ollama ps` affiche "100% GPU"
- [ ] `nvidia-smi` montre Ollama utilisant le GPU
- [ ] API Ollama répond (`curl http://localhost:11434/api/tags`)
- [ ] Backend health check OK (`curl http://localhost:8000/api/health`)
- [ ] RAG query fonctionne (test avec `curl`)
- [ ] Performance 40-60 tok/s (benchmark Ollama)

---

## 💰 COÛTS ESTIMÉS

### DigitalOcean GPU Droplet

| Component | Specs | Monthly Cost |
|-----------|-------|--------------|
| GPU Droplet | Basic AI/ML (8GB VRAM) | ~$100-150 |
| Storage | 100GB SSD | Included |
| Bandwidth | 5TB | Included |
| Backups (opt) | +20% | +$20-30 |

**Total:** ~$120-180/month

### Comparaison avec Alternatives

| Provider | GPU | VRAM | Monthly | Notes |
|----------|-----|------|---------|-------|
| **DigitalOcean** | NVIDIA A100 | 8GB | ~$150 | ✅ Recommandé |
| AWS EC2 g4dn.xlarge | NVIDIA T4 | 16GB | ~$180 | Plus cher, plus VRAM |
| GCP n1-standard-4 + T4 | NVIDIA T4 | 16GB | ~$200 | Plus cher |
| Runpod | NVIDIA A100 | 40GB | ~$100 | Moins stable |

---

## 🎯 POURQUOI C'EST SANS RISQUE

1. **API identique** - Ollama API reste la même (natif Mac ou Docker cloud)
2. **Abstraction propre** - Code dépend de l'interface (`OLLAMA_BASE_URL`), pas de l'implémentation
3. **Testable avant prod** - `docker compose -f docker-compose.prod.yml up` valide la config localement
4. **Rollback immédiat** - En cas de problème, revenir à l'ancienne config en <5 minutes
5. **Zero downtime possible** - Déployer sur nouveau droplet, tester, puis switcher DNS

---

## 📚 RÉFÉRENCES

### Documentation

- **Ollama Baremetal Migration:** `Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md`
- **Docker Compose Dev:** `docker/docker-compose.dev.yml`
- **Docker Compose Prod:** `docker/docker-compose.prod.yml` (à créer lors de la migration)
- **Note Technique Hybrid:** `resources/251104-note-technique-ollama-gpu-hybrid.md`

### Ressources Externes

- Docker Compose Overrides: https://docs.docker.com/compose/multiple-compose-files/
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Docker GPU Support (NVIDIA): https://docs.docker.com/config/containers/resource_constraints/#gpu
- DigitalOcean GPU Droplets: https://docs.digitalocean.com/products/droplets/how-to/gpu/

---

## 🎓 CONTEXTE POUR AI ASSISTANT

### Situation Actuelle (November 2025)

- **Dev Local:** Ollama natif sur Mac M1 Max (Metal GPU)
- **Architecture:** Hybride (Ollama natif + services Docker)
- **Performance:** 7-14 tok/s (Metal GPU)
- **Raison:** Docker Desktop sur Mac ne supporte pas Metal GPU

### Migration Future (Quand Prêt pour Production)

- **Production Cloud:** Ollama dans Docker avec NVIDIA GPU sur DigitalOcean
- **Architecture:** Full Docker (Ollama + Backend + Frontend + Neo4j)
- **Performance attendue:** 40-60 tok/s (NVIDIA GPU)
- **Changements code:** ZÉRO (uniquement `OLLAMA_BASE_URL` env var)

### Principe Clé

**Dépendre d'interfaces (API Ollama), pas d'implémentations (natif vs Docker).**

Ce pattern est standard dans l'industrie ML/GPU pour développement cross-platform (Mac → Linux cloud).

---

**📝 Note:** Ce guide doit être conservé et mis à jour lors de la migration cloud effective. Il garantit une migration sans risque et sans modification de code.

**Status:** ✅ **READY - Documentation complète pour migration future**

---

*Guide créé: November 5, 2025*  
*Basé sur: Devplan/251105-OLLAMA-BAREMETAL-MIGRATION.md + resources/251104-note-technique-ollama-gpu-hybrid.md*

