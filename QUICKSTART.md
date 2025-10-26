# 🚀 QuickStart - RAG Knowledge Graph

Get up and running in **5 minutes**!

## Step 1: Setup (2 min)

```bash
# Clone
git clone <your-repo>
cd rag-kg-boilerplate

# Configure
cp env.template .env
# Edit NEO4J_PASSWORD in .env

# Start
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

## Step 2: Pull LLM Model (2 min)

```bash
docker exec rag-ollama ollama pull llama3:8b
```

Wait for download (~4.5GB).

## Step 3: Test (1 min)

1. Open http://localhost:5173
2. Upload a PDF
3. Wait for "✓ Processed"
4. Ask a question in chat

## ✅ Done!

**Next:**
- [Full Setup Guide](docs/SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [AI Agent Guide](AI-AGENT-GUIDE.md)

**Endpoints:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs
- Neo4j: http://localhost:7474

**Troubleshooting:**
```bash
# Check all services
docker-compose -f docker/docker-compose.dev.yml ps

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f
```
