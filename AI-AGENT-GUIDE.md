# AI Agent Guide - RAG Knowledge Graph Boilerplate

**For:** Claude Sonnet 4.5, GPT-4, and other AI assistants  
**Purpose:** Understand this boilerplate to help developers build RAG applications  
**Last Updated:** October 26, 2025

---

## 🎯 What You Need to Know

You are helping a developer work with a **production-ready boilerplate** for building intelligent document Q&A applications using RAG (Retrieval-Augmented Generation) + Knowledge Graph technology.

### **Core Concept**
```
User uploads PDF/PPT
  ↓
Dockling: Document → Markdown
  ↓
Graphiti: Markdown → Neo4j Knowledge Graph (entities + relationships)
  ↓
User asks question
  ↓
RAG: Query Neo4j → Get relevant context
  ↓
LLM: Context + Question → Grounded answer (streaming)
  ↓
Frontend displays answer token-by-token
```

---

## 📋 Quick Reference

### **Project Structure (Key Files)**

```
backend/app/
├── main.py              # FastAPI app entry point
├── api/
│   ├── upload.py        # POST /upload - Handle file uploads
│   ├── query.py         # POST /query - RAG streaming endpoint
│   └── health.py        # GET /health - Service status
├── core/
│   ├── llm.py           # LLM abstraction (Ollama/Claude/OpenAI)
│   ├── rag.py           # RAG chain (retrieve → augment → generate)
│   └── processor.py     # Document processing pipeline
└── integrations/
    ├── neo4j.py         # Neo4j client wrapper
    ├── graphiti.py      # Graphiti KG extraction
    ├── dockling.py      # PDF/PPT → Markdown
    └── sentry.py        # Error tracking

frontend/src/
├── components/
│   ├── Chat.jsx         # Main chat interface
│   ├── FileUpload.jsx   # Drag & drop uploader
│   └── StreamingMessage.jsx  # Real-time message display
└── hooks/
    ├── useStreamingQuery.js  # SSE hook for streaming
    └── useFileUpload.js      # Upload with progress
```

### **Key Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI (Python 3.11+) | API server, async I/O |
| **Frontend** | React 18 + Vite | Modern UI, fast builds |
| **Styling** | TailwindCSS + shadcn/ui | Utility-first CSS + components |
| **Database** | Neo4j 5.x | Knowledge graph storage |
| **KG Extraction** | Graphiti | Entity/relationship extraction |
| **Doc Processing** | Dockling | PDF/PPT → Markdown |
| **LLM** | Ollama (default) | Local LLM runtime |
| **Monitoring** | Sentry | Error tracking |
| **Deployment** | Vercel (FE) + DigitalOcean (BE) | Cloud hosting |
| **Containerization** | Docker + Docker Compose | Service orchestration |

---

## 🔑 Critical Design Decisions

### **1. LLM Agnostic Architecture**

**File:** `backend/app/core/llm.py`

```python
class LLMProvider:
    """Abstract base class for LLM providers"""
    
    async def stream_completion(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream tokens from LLM"""
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    """Ollama (local, free)"""
    async def stream_completion(self, prompt: str):
        # Use Ollama API for streaming

class ClaudeProvider(LLMProvider):
    """Anthropic Claude (API, paid)"""
    async def stream_completion(self, prompt: str):
        # Use Anthropic SDK for streaming

class OpenAIProvider(LLMProvider):
    """OpenAI GPT (API, paid)"""
    async def stream_completion(self, prompt: str):
        # Use OpenAI SDK for streaming

def get_llm_provider() -> LLMProvider:
    """Factory: Select provider from env var LLM_PROVIDER"""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":
        return OllamaProvider()
    elif provider == "claude":
        return ClaudeProvider()
    elif provider == "openai":
        return OpenAIProvider()
```

**Why:** Developers can switch LLMs via environment variable without code changes.

### **2. Streaming Responses (SSE)**

**Backend:** `backend/app/api/query.py`

```python
from fastapi.responses import StreamingResponse

@router.post("/query")
async def rag_query(question: str):
    async def event_stream():
        # 1. Query Neo4j for context
        context = await neo4j_client.retrieve_context(question)
        
        # 2. Build RAG prompt
        prompt = build_rag_prompt(context, question)
        
        # 3. Stream LLM response
        async for token in llm_provider.stream_completion(prompt):
            yield f"data: {json.dumps({'token': token})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

**Frontend:** `frontend/src/hooks/useStreamingQuery.js`

```javascript
function useStreamingQuery() {
  const [response, setResponse] = useState("");
  
  const query = async (question) => {
    const eventSource = new EventSource(`/api/query?q=${question}`);
    
    eventSource.onmessage = (event) => {
      const { token } = JSON.parse(event.data);
      setResponse((prev) => prev + token);  // Append token
    };
    
    eventSource.onerror = () => eventSource.close();
  };
  
  return { response, query };
}
```

**Why:** Real-time token streaming provides better UX (no waiting for full response).

### **3. Knowledge Graph (Neo4j + Graphiti)**

**File:** `backend/app/integrations/graphiti.py`

```python
async def ingest_document(file_path: str, metadata: dict):
    """
    Process document and build knowledge graph
    
    Steps:
    1. Dockling: PDF → Markdown
    2. Graphiti: Extract entities + relationships
    3. Neo4j: Store graph nodes + edges
    """
    # 1. Convert to markdown
    markdown = await dockling.convert(file_path)
    
    # 2. Extract knowledge graph
    kg = graphiti.build_graph(
        text=markdown,
        metadata=metadata  # Document source, date, etc.
    )
    
    # 3. Store in Neo4j
    await neo4j_client.ingest_graph(kg)
```

**RAG Retrieval:** `backend/app/integrations/neo4j.py`

```python
async def retrieve_context(question: str, top_k: int = 5):
    """
    Query Neo4j for relevant context
    
    Cypher query example:
    MATCH (n)-[r]->(m)
    WHERE n.text CONTAINS $keyword
    RETURN n.text, type(r), m.text
    LIMIT $top_k
    """
    # Vector similarity search + graph traversal
    results = await neo4j_driver.execute_query(
        query=RETRIEVAL_QUERY,
        parameters={"question": question, "top_k": top_k}
    )
    
    # Format context for LLM
    context = format_context_for_rag(results)
    return context
```

**Why:** 
- **Graphiti** extracts structured knowledge automatically
- **Neo4j** enables graph traversal for better context retrieval
- **RAG** grounds LLM responses in actual document content

### **4. File Upload & Storage**

**Backend:** `backend/app/api/upload.py`

```python
@router.post("/upload")
async def upload_document(file: UploadFile):
    # 1. Save original file (persistent volume)
    file_path = f"/uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(await file.read())
    
    # 2. Generate upload ID
    upload_id = str(uuid.uuid4())
    
    # 3. Start background processing
    background_tasks.add_task(
        process_document, 
        file_path=file_path, 
        upload_id=upload_id
    )
    
    return {"upload_id": upload_id, "status": "processing"}
```

**Frontend:** `frontend/src/components/FileUpload.jsx`

```jsx
function FileUpload() {
  const [progress, setProgress] = useState(0);
  
  const handleDrop = async (files) => {
    const formData = new FormData();
    formData.append("file", files[0]);
    
    await fetch("/api/upload", {
      method: "POST",
      body: formData,
      onUploadProgress: (e) => setProgress((e.loaded / e.total) * 100)
    });
  };
  
  return <DropZone onDrop={handleDrop} progress={progress} />;
}
```

**Why:** 
- **Original files stored on DigitalOcean** (persistent)
- **Frontend uploads to backend** (not directly to storage)
- **Background processing** doesn't block uploads

---

## 🛠️ Common Developer Tasks

### **Task 1: Add a New LLM Provider**

**File to modify:** `backend/app/core/llm.py`

```python
class CustomLLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("CUSTOM_LLM_API_KEY")
        self.base_url = os.getenv("CUSTOM_LLM_BASE_URL")
    
    async def stream_completion(self, prompt: str):
        # Implement streaming logic for custom LLM
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                f"{self.base_url}/completions",
                json={"prompt": prompt, "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    yield json.loads(line)["token"]

# Update factory
def get_llm_provider():
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "custom":
        return CustomLLMProvider()
    # ... existing providers
```

**Environment variables to add:**
```bash
LLM_PROVIDER=custom
CUSTOM_LLM_API_KEY=...
CUSTOM_LLM_BASE_URL=https://api.custom-llm.com
```

### **Task 2: Customize Document Processing**

**File to modify:** `backend/app/core/processor.py`

```python
async def process_document(file_path: str, upload_id: str):
    try:
        # 1. Convert to markdown (Dockling)
        markdown = await dockling.convert(file_path)
        
        # 2. Optional: Custom pre-processing
        markdown = custom_preprocessing(markdown)  # Your custom logic
        
        # 3. Extract metadata
        metadata = extract_metadata(file_path)  # Title, author, date, etc.
        
        # 4. Build knowledge graph (Graphiti)
        await graphiti.ingest_document(markdown, metadata)
        
        # 5. Update status
        await update_processing_status(upload_id, "completed")
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        await update_processing_status(upload_id, "failed", str(e))
```

### **Task 3: Add Authentication**

**File to create:** `backend/app/middleware/auth.py`

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token (use PyJWT or similar)
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_from_token(token)

# Apply to routes
@router.post("/query")
async def rag_query(
    question: str, 
    user: dict = Depends(verify_token)  # Protected route
):
    # Only authenticated users can query
    pass
```

**Frontend:** Add Authorization header
```javascript
fetch("/api/query", {
  headers: {
    "Authorization": `Bearer ${localStorage.getItem("token")}`
  }
});
```

### **Task 4: Add Knowledge Graph Visualization**

**Frontend component:** `frontend/src/components/GraphVisualization.jsx`

```jsx
import { ForceGraph2D } from 'react-force-graph';

function GraphVisualization({ documentId }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  
  useEffect(() => {
    // Fetch graph data from backend
    fetch(`/api/graph/${documentId}`)
      .then(res => res.json())
      .then(data => setGraphData(data));
  }, [documentId]);
  
  return (
    <ForceGraph2D
      graphData={graphData}
      nodeLabel="label"
      linkDirectionalArrowLength={3.5}
      linkDirectionalArrowRelPos={1}
    />
  );
}
```

**Backend endpoint:** `backend/app/api/graph.py`

```python
@router.get("/graph/{document_id}")
async def get_document_graph(document_id: str):
    """Return Neo4j graph for visualization"""
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.document_id = $document_id
    RETURN n, r, m
    """
    results = await neo4j_driver.execute_query(query, document_id=document_id)
    
    # Format for react-force-graph
    nodes = [{"id": n.id, "label": n.text} for n in results.nodes]
    links = [{"source": r.start, "target": r.end} for r in results.relationships]
    
    return {"nodes": nodes, "links": links}
```

---

## 🐛 Common Issues & Solutions

### **Issue 1: Ollama model not found**

**Error:** `Model 'llama3:8b' not found`

**Solution:**
```bash
# Pull the model
docker exec rag-ollama ollama pull llama3:8b

# List available models
docker exec rag-ollama ollama list
```

### **Issue 2: Neo4j connection refused**

**Error:** `Unable to connect to bolt://neo4j:7687`

**Solution:**
```bash
# Check Neo4j is running
docker-compose -f docker/docker-compose.dev.yml ps

# Check logs
docker-compose -f docker/docker-compose.dev.yml logs neo4j

# Verify password in .env matches Neo4j config
```

### **Issue 3: Frontend can't reach backend**

**Error:** `Failed to fetch from http://localhost:8000`

**Solution:**
```bash
# Check VITE_API_URL in frontend .env
# Development: http://localhost:8000
# Production: https://api.your-domain.com

# Verify CORS settings in backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Issue 4: Document processing stuck**

**Symptom:** Upload succeeds, status never updates to "completed"

**Debugging:**
```bash
# Check backend logs
docker-compose logs backend

# Check for Dockling errors
docker-compose logs backend | grep dockling

# Check Neo4j disk space
docker exec rag-neo4j df -h /data
```

---

## 🚀 Deployment Guidance

### **Frontend: Vercel**

**When helping with Vercel deployment:**

1. **Environment variables required:**
   ```
   VITE_API_URL=https://api.your-domain.com
   VITE_SENTRY_DSN=https://...
   ```

2. **Build command:** `npm run build`
3. **Output directory:** `dist`
4. **Framework preset:** Vite

**Common issue:** CORS errors
- Ensure backend `CORS_ORIGINS` includes Vercel domain
- Example: `CORS_ORIGINS=https://your-app.vercel.app`

### **Backend: DigitalOcean**

**When helping with DigitalOcean deployment:**

1. **Recommended droplet:** 
   - CPU-Optimized 4GB RAM ($24/month) if using Ollama
   - Basic 2GB RAM ($12/month) if using Claude/OpenAI APIs

2. **Docker Compose file:** `docker/docker-compose.prod.yml`

3. **Persistent volumes:**
   ```yaml
   volumes:
     - /opt/rag-uploads:/uploads          # Original files
     - /opt/neo4j-data:/var/lib/neo4j/data  # Graph database
     - /opt/ollama-models:/root/.ollama     # LLM models
   ```

4. **Nginx reverse proxy:**
   ```nginx
   server {
       listen 80;
       server_name api.your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **SSL certificate:** Use Certbot (Let's Encrypt)
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d api.your-domain.com
   ```

---

## 📚 Key Files to Read First

When a developer asks for help, prioritize reading:

1. **GOAL.md** - Understand project objectives
2. **README.md** - Quick start and structure
3. **backend/app/main.py** - FastAPI app setup
4. **backend/app/core/rag.py** - RAG chain logic
5. **frontend/src/components/Chat.jsx** - UI implementation
6. **.env.template** - All configuration options

---

## 🎯 Your Role as AI Assistant

### **When the developer asks for help:**

1. **Understand the context:**
   - Are they setting up locally or deploying?
   - Which component are they working on (frontend, backend, deployment)?
   - What's their experience level?

2. **Provide specific, actionable guidance:**
   - Exact file paths
   - Complete code examples
   - Terminal commands
   - Environment variable names

3. **Explain the "why":**
   - Why this architecture choice?
   - Why this technology?
   - What are the trade-offs?

4. **Offer alternatives:**
   - "If you want to use X instead of Y, modify file Z like this..."
   - "For production, consider adding authentication..."

5. **Debug systematically:**
   - Check logs first
   - Verify environment variables
   - Test each component independently
   - Use Docker Compose `ps` and `logs` commands

### **Common Questions You'll Receive:**

**"How do I add authentication?"**
→ See "Task 3: Add Authentication" above

**"Can I use a different LLM?"**
→ See "Task 1: Add a New LLM Provider" above

**"How do I deploy to AWS instead of DigitalOcean?"**
→ Same Docker Compose setup, just provision EC2 instance instead of Droplet

**"The frontend isn't showing streamed responses"**
→ Check SSE connection, CORS, and `useStreamingQuery` hook

**"Neo4j is using too much disk space"**
→ Implement document cleanup, limit graph depth, or use AWS RDS Neo4j

---

## 🔮 Future Enhancements (Guide Developers)

### **Multi-tenancy**
- Add `user_id` to all Neo4j nodes
- Filter queries by user
- Separate upload directories per user

### **Advanced RAG Techniques**
- Hybrid search (vector + graph)
- Re-ranking with cross-encoder
- Query expansion with LLM
- Contextual compression

### **Knowledge Graph Improvements**
- Entity linking (connect related entities across documents)
- Temporal graphs (track changes over time)
- Graph algorithms (PageRank, community detection)

---

## ✅ Final Checklist for Developers

When a developer says "I'm deploying to production," ensure:

- [ ] `.env` has production values (no `localhost`)
- [ ] Sentry DSN configured
- [ ] Neo4j password is strong (not default)
- [ ] CORS origins match frontend domain
- [ ] Ollama models are pulled (if using Ollama)
- [ ] Persistent volumes are backed up
- [ ] SSL certificate is configured (Nginx + Certbot)
- [ ] Health checks are working (`/api/health`)
- [ ] Vercel environment variables are set
- [ ] DigitalOcean firewall allows ports 80, 443
- [ ] Test document upload → processing → query end-to-end

---

**You are now ready to help developers build amazing RAG applications! 🚀**

**Remember:** This is a boilerplate - developers will customize it. Guide them towards best practices, but respect their architecture choices.

**Good luck!** 🎉

