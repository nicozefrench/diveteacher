# Setup Guide - RAG Knowledge Graph

## Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Vercel account
- (Optional) DigitalOcean account

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd rag-kg-boilerplate
```

### 2. Configure Environment

```bash
cp env.template .env
nano .env
```

**Minimum required changes:**
- `NEO4J_PASSWORD`: Set a strong password

### 3. Start Services

```bash
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

Wait ~30 seconds for services to start.

### 4. Pull LLM Model

```bash
# Pull llama3:8b (recommended, ~4.5GB)
docker exec rag-ollama ollama pull llama3:8b

# Verify
docker exec rag-ollama ollama list
```

### 5. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: from .env)

---

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production setup.

**Quick summary:**

### Backend (DigitalOcean)

```bash
# On your droplet
curl -fsSL https://raw.githubusercontent.com/your-repo/deploy/digitalocean-setup.sh | bash
cd /opt/rag-app
git clone <your-repo-url> .
cp env.template .env
nano .env  # Configure for production
docker-compose -f docker/docker-compose.prod.yml up -d
docker exec rag-ollama ollama pull llama3:8b
```

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

Set environment variables in Vercel dashboard:
- `VITE_API_URL`: Your DigitalOcean API URL
- `VITE_SENTRY_DSN`: Your Sentry DSN

---

## Troubleshooting

### Neo4j connection failed

```bash
# Check Neo4j logs
docker-compose -f docker/docker-compose.dev.yml logs neo4j

# Verify password matches .env
```

### Ollama model not found

```bash
# Pull model
docker exec rag-ollama ollama pull llama3:8b
```

### Frontend can't reach backend

Check `VITE_API_URL` in `.env` and restart frontend:

```bash
docker-compose -f docker/docker-compose.dev.yml restart frontend
```

---

## Next Steps

1. Upload a test PDF via frontend
2. Wait for processing to complete
3. Ask questions in chat interface
4. Check Neo4j Browser to see knowledge graph

---

For detailed documentation, see:
- [GOAL.md](GOAL.md) - Project objectives
- [AI-AGENT-GUIDE.md](AI-AGENT-GUIDE.md) - Guide for AI assistants
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment

