# RAG Knowledge Graph Boilerplate

**A production-ready foundation for building intelligent document Q&A applications**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://react.dev/)

---

## 🎯 What is this?

A **complete, reusable boilerplate** for building RAG (Retrieval-Augmented Generation) applications with:
- **Document Processing:** Upload PDF/PPT → Auto-process → Knowledge Graph
- **Knowledge Graph:** Neo4j with Graphiti for intelligent entity/relationship extraction
- **LLM Agnostic:** Ollama (local), Claude, or OpenAI - your choice
- **Modern UI:** React + TailwindCSS + shadcn/ui with streaming responses
- **Production Ready:** Docker, Vercel, DigitalOcean deployment included

**Perfect for:** Private document Q&A, research assistants, legal/compliance tools, technical documentation systems

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Document Upload** | Drag & drop PDF/PPT files with real-time progress |
| 🧠 **Knowledge Graph** | Neo4j + Graphiti for intelligent entity extraction |
| 🤖 **LLM Agnostic** | Ollama (local), Claude, OpenAI - switch via env var |
| 💬 **Streaming Chat** | Real-time token streaming for better UX |
| 🎨 **Modern UI** | React + TailwindCSS + shadcn/ui components |
| 🐳 **Docker Ready** | One command to start (dev + prod configs) |
| 🚀 **Deploy Ready** | Vercel (frontend) + DigitalOcean (backend) |
| 📊 **Monitoring** | Sentry integration for error tracking |
| 🔐 **Secure** | All secrets via environment variables |

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- Git
- (Optional) Vercel account for deployment
- (Optional) DigitalOcean account for backend hosting

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/your-username/rag-kg-boilerplate.git
cd rag-kg-boilerplate

# Copy environment template
cp .env.template .env

# Edit .env with your settings
nano .env
```

### 2. Start All Services

```bash
# Start backend + Neo4j + Ollama
docker-compose -f docker/docker-compose.dev.yml up -d

# Wait ~30 seconds for services to start
# Check status
docker-compose -f docker/docker-compose.dev.yml ps
```

### 3. Pull LLM Model (First Time Only)

```bash
# Pull Ollama model (llama3:8b recommended)
docker exec rag-ollama ollama pull llama3:8b

# Verify
docker exec rag-ollama ollama list
```

### 4. Access Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React app |
| **Backend API** | http://localhost:8000 | FastAPI docs |
| **Neo4j Browser** | http://localhost:7474 | Graph visualization |
| **Ollama** | http://localhost:11434 | LLM server |

### 5. Test the System

1. **Upload a document:** Go to http://localhost:5173, drag & drop a PDF
2. **Wait for processing:** Status will update automatically
3. **Ask a question:** Type in chat interface, get streaming response

---

## 📂 Project Structure

```
rag-kg-boilerplate/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── api/               # API routes
│   │   │   ├── upload.py      # File upload endpoint
│   │   │   ├── query.py       # RAG query endpoint (streaming)
│   │   │   └── health.py      # Health checks
│   │   ├── core/              # Core business logic
│   │   │   ├── llm.py         # LLM abstraction layer
│   │   │   ├── rag.py         # RAG chain logic
│   │   │   └── processor.py   # Document processing
│   │   ├── integrations/      # External services
│   │   │   ├── neo4j.py       # Neo4j client
│   │   │   ├── graphiti.py    # Graphiti integration
│   │   │   ├── dockling.py    # PDF/PPT processing
│   │   │   └── sentry.py      # Error tracking
│   │   └── models/            # Pydantic models
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container
│   └── .env.template          # Environment variables
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Chat.jsx       # Chat interface
│   │   │   ├── FileUpload.jsx # Drag & drop upload
│   │   │   ├── StreamingMessage.jsx
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── hooks/
│   │   │   ├── useStreamingQuery.js  # SSE hook
│   │   │   └── useFileUpload.js
│   │   ├── lib/
│   │   │   └── api.js         # API client
│   │   └── App.jsx            # Main app
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── vercel.json            # Vercel deployment config
│   └── Dockerfile.dev         # Frontend container (dev)
│
├── docker/
│   ├── docker-compose.dev.yml      # Local development
│   ├── docker-compose.prod.yml     # Production (DigitalOcean)
│   └── nginx/                      # Reverse proxy config
│
├── deploy/
│   ├── digitalocean-setup.sh       # DO droplet setup
│   ├── vercel-deploy.sh            # Vercel deployment
│   └── pull-ollama-models.sh       # LLM model setup
│
├── docs/
│   ├── SETUP.md                    # Detailed setup guide
│   ├── DEPLOYMENT.md               # Production deployment
│   ├── ARCHITECTURE.md             # System design
│   ├── API.md                      # API reference
│   └── TROUBLESHOOTING.md          # Common issues
│
├── examples/
│   └── sample-docs/                # Example PDFs for testing
│
├── .env.template                   # Environment variables template
├── .gitignore
├── LICENSE
├── README.md                       # This file
├── GOAL.md                         # Project objectives
└── AI-AGENT-GUIDE.md              # Guide for AI assistants
```

---

## 🔧 Configuration

### Environment Variables

All configuration is via `.env` file. See `.env.template` for all options.

**Key variables:**

```bash
# LLM Provider (choose one)
LLM_PROVIDER=ollama  # or 'claude' or 'openai'
OLLAMA_MODEL=llama3:8b

# Neo4j Database
NEO4J_PASSWORD=your_secure_password

# Monitoring (Optional)
SENTRY_DSN_BACKEND=https://...
SENTRY_DSN_FRONTEND=https://...

# Frontend (Vercel deployment)
VITE_API_URL=https://api.your-domain.com
```

### Switching LLM Providers

```bash
# Use Ollama (local, free)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3:8b

# Use Claude (API, paid)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...

# Use OpenAI (API, paid)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

---

## 🌐 Deployment

### Frontend: Vercel (Free Tier)

```bash
cd frontend

# Option 1: GitHub integration (recommended)
# Push to GitHub → Vercel auto-deploys

# Option 2: CLI
npm install -g vercel
vercel --prod

# Set environment variables in Vercel dashboard:
# VITE_API_URL=https://api.your-domain.com
# VITE_SENTRY_DSN=...
```

### Backend: DigitalOcean ($12-40/month)

```bash
# 1. Create Droplet (Ubuntu 22.04)
# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Run setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/deploy/digitalocean-setup.sh | bash

# 4. Configure .env
cd /opt/rag-app
nano .env

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Pull Ollama model
docker exec rag-ollama ollama pull llama3:8b
```

**Detailed guides:** See `docs/DEPLOYMENT.md`

---

## 📊 Monitoring

### Sentry Integration

**Backend errors:** Automatically captured and sent to Sentry
**Frontend errors:** React error boundaries + Sentry SDK
**Performance:** Transaction tracing for API calls

**Setup:**
1. Create Sentry project (free tier available)
2. Copy DSN to `.env`
3. Errors automatically tracked

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker/docker-compose.test.yml up --abort-on-container-exit
```

---

## 🤝 Contributing

This is a boilerplate template - fork and customize for your needs!

**To contribute back:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [GOAL.md](GOAL.md) | Project objectives and features |
| [AI-AGENT-GUIDE.md](AI-AGENT-GUIDE.md) | Guide for AI assistants (Claude, etc.) |
| [docs/SETUP.md](docs/SETUP.md) | Detailed installation guide |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design deep-dive |
| [docs/API.md](docs/API.md) | Backend API reference |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues + solutions |

---

## 💡 Use Cases

### Research Assistant
Upload academic papers → Ask questions → Get cited answers

### Legal Compliance Tool
Upload contracts/policies → Query compliance requirements → Audit-ready responses

### Technical Documentation
Upload developer docs → Natural language queries → Code examples with context

### Business Intelligence
Upload reports/presentations → Executive summaries → Data-driven insights

---

## 🔮 Roadmap

- [x] Core RAG pipeline (MVP)
- [x] Knowledge graph integration
- [x] LLM abstraction layer
- [x] Docker deployment
- [x] Vercel + DigitalOcean setup
- [x] Sentry monitoring
- [ ] Multi-user authentication
- [ ] Document collections
- [ ] Knowledge graph visualization
- [ ] Batch document processing
- [ ] Advanced search filters
- [ ] Export conversations

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful components
- [Neo4j](https://neo4j.com/) - Graph database
- [Graphiti](https://github.com/getzep/graphiti) - Knowledge graph extraction
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Dockling](https://github.com/DS4SD/dockling) - Document processing

---

## 🆘 Support

**Issues:** [GitHub Issues](https://github.com/your-username/rag-kg-boilerplate/issues)  
**Questions:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## ⭐ Star History

If this boilerplate helps you, please consider giving it a star! ⭐

---

**Status:** 🚀 **Ready for production use**  
**Maintained by:** [Your Name](https://github.com/your-username)  
**Last Updated:** October 26, 2025

