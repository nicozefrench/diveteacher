# Note Technique - Solution GPU Ollama (Dev Local Mac → Cloud GPU)

**Date:** 2025-11-04  
**Contexte:** Développement système RAG avancé avec migration prévue vers DigitalOcean GPU Droplet  
**Assistant:** Claude Sonnet 4.5

---

## 🚨 PROBLÈME

**Docker Desktop sur Mac ne supporte PAS le GPU Metal.**

```bash
docker exec rag-ollama ollama ps
# Résultat: PROCESSOR: 100% CPU ❌
# Attendu:  PROCESSOR: 100% GPU ✅
```

**Conséquence:** Tests locaux 10-20x plus lents, impossible de valider les perfs réelles.

---

## ✅ SOLUTION: Configuration Hybride

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

## 🛠️ MISE EN ŒUVRE

### Étape 1: Installer Ollama Nativement (Mac)

```bash
brew install ollama
ollama serve  # Lance le serveur sur :11434
ollama pull qwen2.5:7b-instruct-q8_0  # Ou votre modèle
ollama ps  # Doit montrer "100% GPU" (Metal)
```

### Étape 2: Adapter Docker Compose

**Structure fichiers:**
```
projet/
├── docker-compose.yml           # Config commune
├── docker-compose.dev.yml       # Overrides local (pas d'Ollama)
├── docker-compose.prod.yml      # Overrides cloud (Ollama + GPU)
├── .env.dev                     # Vars local
└── .env.prod                    # Vars cloud
```

**docker-compose.dev.yml** (extrait):
```yaml
services:
  backend:  # Ou le service qui appelle Ollama
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**docker-compose.prod.yml** (extrait):
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
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

### Étape 3: Variables d'Environnement

**.env.dev:**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
```

**.env.prod:**
```bash
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
```

**Important:** Votre code doit lire `OLLAMA_BASE_URL` depuis l'environnement.

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

## 🚀 CE QUI SE PASSE LORS DE LA MIGRATION CLOUD

### Changements Effectifs

**1. Ollama passe de Natif → Docker avec GPU**
```bash
# Local (avant)
ollama serve  # Natif sur Mac, port :11434

# Cloud (après)
docker-compose up  # Ollama dans container, port :11434
```

**2. Une seule variable change**
```bash
# .env.dev (local)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# .env.prod (cloud)
OLLAMA_BASE_URL=http://ollama:11434
```

**3. Commande de lancement différente**
```bash
# Local
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Cloud
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Ce Qui NE Change PAS

| Composant | Status |
|-----------|--------|
| Code backend/frontend | ✅ Identique (0 ligne modifiée) |
| API calls à Ollama | ✅ Identique (même format JSON) |
| Modèles utilisés | ✅ Identiques (même compatibilité) |
| Base de données | ✅ Identique (même config) |
| Logique RAG | ✅ Identique |
| Performance | ✅ GPU dans les 2 cas (Metal local, NVIDIA cloud) |

### Déroulement Migration (Step-by-Step)

**Sur votre machine locale:**
```bash
# 1. Pousser le code
git push origin main
```

**Sur le Droplet DigitalOcean:**
```bash
# 2. Cloner le repo
git clone <votre-repo> /opt/rag-app
cd /opt/rag-app

# 3. Configurer l'environnement
cp .env.prod .env
# Éditer .env avec les vrais secrets/passwords

# 4. Vérifier GPU disponible
nvidia-smi  # Doit afficher votre GPU NVIDIA

# 5. Lancer en production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 6. Attendre que Ollama démarre (~30 sec)
docker logs -f rag-ollama

# 7. Charger le modèle
docker exec rag-ollama ollama pull qwen2.5:7b-instruct-q8_0

# 8. VÉRIFIER GPU
docker exec rag-ollama ollama ps
# ✅ Doit afficher: PROCESSOR: 100% GPU
```

**Si `ollama ps` affiche "100% GPU" → Migration réussie ✅**

### Temps de Migration Estimé

| Étape | Durée |
|-------|-------|
| Setup droplet (si nouveau) | ~5 min |
| Transfert code | ~1 min |
| Configuration .env | ~2 min |
| Premier `docker-compose up` | ~3-5 min (pull images) |
| Chargement modèle Ollama | ~2-10 min (selon taille) |
| **TOTAL** | **~15-25 minutes** |

Ensuite, les redéploiements suivants: **~2-3 minutes** (juste rebuild).

### Troubleshooting Migration

**❌ Si `ollama ps` montre CPU au lieu de GPU:**
```bash
# Vérifier NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi

# Si erreur → installer nvidia-docker2
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**❌ Si containers ne démarrent pas:**
```bash
# Checker les logs
docker-compose logs

# Problème courant: ports déjà utilisés
sudo netstat -tulpn | grep :11434
```

**❌ Si backend ne peut pas joindre Ollama:**
```bash
# Vérifier networking Docker
docker network ls
docker network inspect <network_name>

# Tester depuis le backend
docker exec rag-backend curl http://ollama:11434/api/tags
```

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

## 💡 POURQUOI C'EST SANS RISQUE

1. **API identique** - Ollama API reste la même (natif ou Docker)
2. **Abstraction propre** - Code dépend de l'interface, pas de l'implémentation
3. **Testable avant prod** - `docker-compose -f docker-compose.prod.yml up` valide la config
4. **Rollback immédiat** - En cas de problème, juste changer l'env var

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

## 🎓 CONTEXTE POUR SONNET 4.5

- **Problème:** Ollama en Docker sur Mac M1 Max = CPU only (limitation Docker Desktop)
- **Solution:** Ollama natif local (GPU Metal) + Docker prod (GPU NVIDIA)
- **Principe:** Dépendre d'interfaces (API Ollama), pas d'implémentations (natif/Docker)
- **Migration:** Change uniquement `OLLAMA_BASE_URL` entre dev et prod
- **Risque:** Aucun - Pattern standard industrie ML/GPU cross-platform

---

**📝 Note:** Cette approche est recommandée et éprouvée pour le développement ML/GPU sur Mac avec déploiement cloud Linux.