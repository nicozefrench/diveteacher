# Production Deployment Guide - DiveTeacher

> **🤖 AI Agent Notice:** This documentation is optimized for Claude Sonnet 4.5 agents.  
> **⚠️ CRITICAL:** This is PHASE 9 ONLY - Do NOT execute until Phases 0-8 are complete and tested locally.  
> **Cost Impact:** ~$120/month (DigitalOcean GPU + Vercel Pro)  
> **📚 Complete GPU Guide:** See `resources/251028-rag-gpu-deployment-guide.md` for detailed Qwen 2.5 7B Q8_0 deployment

---

## 📋 Document Purpose (AI Agent Context)

This guide covers **production deployment only** (Phase 9 of 9).

**Prerequisites Before Reading This:**
1. ✅ Phases 0-8 complete (100% local development done)
2. ✅ All features tested and working on Mac M1 Max
3. ✅ User confirmed ready to deploy and pay $120/month
4. ✅ Supabase project created (Phase 1)
5. ✅ Sentry projects created (Phase 0/7)

**AI Agent Decision Tree:**
- **IF** user asks "deploy to production" AND Phases 0-8 NOT done → **STOP, redirect to SETUP.md**
- **IF** user asks "deploy to production" AND Phases 0-8 done → **Proceed with this guide**

---

## 🎯 Deployment Architecture

### Overview
```
User Browser
    ↓
[diveteacher.io - Vercel]
    ↓ HTTPS
[api.diveteacher.io - DigitalOcean GPU Droplet]
    ├── FastAPI Backend (Docker)
    ├── Neo4j 5.25.1 (Docker)
    ├── Ollama + Mistral 7B (Docker)
    └── PostgreSQL (Supabase Cloud)
```

### Component Locations
| Component | Service | Location | Cost |
|-----------|---------|----------|------|
| **Frontend** | Vercel Pro | Global CDN | Included in account |
| **Backend API** | DigitalOcean GPU | SFO3/NYC3 | $100-150/month |
| **Neo4j Graph** | Docker on DO GPU | Same droplet | Included |
| **Ollama + Qwen 2.5 7B Q8_0** | Docker on DO GPU | Same droplet | Included ✅ |
| **PostgreSQL** | Supabase Cloud | AWS us-east-1 | Free (< 500MB) |
| **Auth** | Supabase Cloud | AWS us-east-1 | Free (< 50k users) |
| **Monitoring** | Sentry Cloud | Global | Free (< 5k events) |

**Note:** For complete Qwen 2.5 7B Q8_0 GPU deployment instructions, performance tuning, and cost optimization strategies, see: **`resources/251028-rag-gpu-deployment-guide.md`**

**Total Monthly Cost:** ~$120 (only DigitalOcean GPU droplet)

---

## 🚀 Part 1: Backend Deployment (DigitalOcean GPU)

### 1.1 Create GPU Droplet

#### Access DigitalOcean Dashboard
```bash
# AI Agent: Guide user to create droplet with these exact specs
open https://cloud.digitalocean.com/droplets/new
```

#### Droplet Configuration
| Setting | Value | Reason |
|---------|-------|--------|
| **Image** | Ubuntu 22.04 LTS x64 | Stable, Docker support |
| **Plan** | GPU-Optimized Droplets | Needed for Mistral 7B |
| **GPU Type** | Basic AI/ML (8GB VRAM) | Mistral needs 5.2GB + overhead |
| **RAM** | 16GB minimum | Backend + Neo4j + Ollama |
| **CPU** | 4+ vCPUs | Processing documents |
| **Storage** | 100GB SSD | Models + Neo4j data |
| **Datacenter** | SFO3 (San Francisco) | Close to US West users |
| **VPC** | Default | Not critical for V1 |
| **SSH Keys** | Add your public key | Secure access |
| **Hostname** | diveteacher-prod-gpu | Identifiable |
| **Backups** | Enable (optional, +20%) | Recommended for production |

**Cost:** ~$100-150/month depending on exact GPU tier

#### After Creation
```bash
# Note the public IP address (shown in dashboard)
# Example: 147.182.XXX.XXX
export DROPLET_IP="147.182.XXX.XXX"
```

---

### 1.2 Initial Server Setup

#### Connect to Droplet
```bash
ssh root@$DROPLET_IP
```

**Expected:** Login successful, Ubuntu 22.04 prompt

#### Update System
```bash
apt update && apt upgrade -y
```

#### Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify
docker --version
# Expected: Docker version 24.0+ ...

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker compose version
# Expected: Docker Compose version v2.23+
```

#### Install NVIDIA Docker (For GPU Access)
```bash
# Add NVIDIA repo
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Docker runtime
apt update
apt install -y nvidia-docker2

# Restart Docker
systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
# Expected: GPU info displayed
```

#### Install Nginx (Reverse Proxy)
```bash
apt install nginx -y
systemctl enable nginx
```

#### Install Certbot (SSL Certificates)
```bash
apt install certbot python3-certbot-nginx -y
```

#### Create Application Directory
```bash
mkdir -p /opt/diveteacher
cd /opt/diveteacher
```

---

### 1.3 Configure DNS (Before SSL)

**AI Agent Task:** Guide user to configure DNS records

#### Required DNS Records
| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | api.diveteacher.io | $DROPLET_IP | 300 |
| A | diveteacher.io | (Vercel IP - see Vercel) | 300 |
| CNAME | www.diveteacher.io | diveteacher.io | 300 |

**Instructions:**
1. Go to domain registrar (Vercel Domains or external)
2. Add A record: `api.diveteacher.io` → `$DROPLET_IP`
3. Wait 5 minutes for propagation
4. Verify:
```bash
dig api.diveteacher.io +short
# Expected: $DROPLET_IP
```

---

### 1.4 Clone Repository & Configure

#### Clone DiveTeacher
```bash
cd /opt/diveteacher
git clone https://github.com/nicozefrench/diveteacher.git .

# If private repo, authenticate first:
# git config --global credential.helper store
# Then enter GitHub token when prompted
```

#### Create Production .env
```bash
cp env.template .env
nano .env
```

**Production .env Configuration:**
```bash
# ============================================
# API Configuration
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false  # CRITICAL: false in production

# ============================================
# LLM Configuration
# ============================================
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434  # Internal Docker network
OLLAMA_MODEL=mistral:7b-instruct-q5_K_M

# Optional: Add API keys for fallback
ANTHROPIC_API_KEY=  # Leave empty if not using
OPENAI_API_KEY=     # Leave empty if not using

# ============================================
# Neo4j Configuration
# ============================================
NEO4J_URI=bolt://neo4j:7687  # Internal Docker network
NEO4J_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD  # ⚠️ CHANGE THIS!

# ============================================
# Graphiti Configuration
# ============================================
GRAPHITI_PROVIDER=ollama
GRAPHITI_MODEL=mistral:7b-instruct-q5_K_M

# ============================================
# Supabase Configuration (From Phase 1)
# ============================================
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...  # Public anon key
SUPABASE_SERVICE_KEY=eyJhbGc...  # Secret service role key

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_URL=https://diveteacher.io
CORS_ORIGINS=https://diveteacher.io,https://www.diveteacher.io

# ============================================
# File Upload Configuration
# ============================================
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=pdf,ppt,pptx

# ============================================
# Processing Configuration
# ============================================
DOCLING_TIMEOUT=300
PROCESSING_WORKERS=4  # GPU droplet can handle more

# ============================================
# RAG Configuration
# ============================================
RAG_CONTEXT_WINDOW=4000
RAG_MAX_TOKENS=2000
RAG_TEMPERATURE=0.1  # Low for accuracy
RAG_TOP_K=5

# ============================================
# Sentry Configuration (From Phase 0/7)
# ============================================
SENTRY_DSN_BACKEND=https://xxxxx@o000000.ingest.us.sentry.io/0000000
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of transactions
```

**AI Agent Checklist - .env File:**
- [ ] `DEBUG=false` (critical for security)
- [ ] Strong Neo4j password (not default)
- [ ] Correct Supabase URL and keys (from Phase 1)
- [ ] Correct Sentry DSN (from Phase 0/7)
- [ ] `FRONTEND_URL=https://diveteacher.io` (not localhost)
- [ ] `CORS_ORIGINS` includes production domain

---

### 1.5 Configure Nginx Reverse Proxy

#### Create Nginx Config
```bash
nano /etc/nginx/sites-available/diveteacher
```

**Nginx Configuration:**
```nginx
# DiveTeacher API - Production
# AI Agent: This proxies HTTPS requests to Docker backend

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name api.diveteacher.io;
    
    # Certbot verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.diveteacher.io;
    
    # SSL certificates (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/api.diveteacher.io/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/api.diveteacher.io/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Max upload size (matches backend)
    client_max_body_size 100M;
    
    # Proxy to Docker backend
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        
        # WebSocket support (for SSE streaming)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts (long for document processing)
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Health check endpoint (no auth needed)
    location /api/health {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}
```

#### Enable Site
```bash
ln -s /etc/nginx/sites-available/diveteacher /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remove default site
nginx -t  # Test configuration
systemctl reload nginx
```

**Expected Output:**
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### 1.6 Configure SSL Certificate

#### Obtain Certificate from Let's Encrypt
```bash
certbot --nginx -d api.diveteacher.io
```

**Prompts (AI Agent Guide):**
1. **Email:** Enter valid email for renewal notifications
2. **Terms:** Agree (Y)
3. **Newsletter:** Choose (Y/N, doesn't matter)
4. **Redirect:** Choose (2) Redirect HTTP to HTTPS

**Expected Output:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/api.diveteacher.io/fullchain.pem
```

#### Test Auto-Renewal
```bash
certbot renew --dry-run
```

**Expected:** "Congratulations, all simulated renewals succeeded"

---

### 1.7 Start Production Services

#### Build and Start Docker Containers
```bash
cd /opt/diveteacher
docker compose -f docker/docker-compose.prod.yml up -d --build
```

**Expected Output:**
```
[+] Building ...
[+] Running 4/4
 ✔ Container rag-neo4j-prod      Started
 ✔ Container rag-ollama-prod     Started
 ✔ Container rag-backend-prod    Started
```

**Note:** Production compose file has `-prod` suffixes to avoid conflicts

#### Wait for Services to Start
```bash
sleep 60  # Wait 1 minute
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected:**
```
NAMES                STATUS
rag-backend-prod     Up 60 seconds (healthy)
rag-neo4j-prod       Up 60 seconds (healthy)
rag-ollama-prod      Up 60 seconds
```

---

### 1.8 Pull Mistral Model (Production)

#### Pull Model into Production Ollama
```bash
docker exec rag-ollama-prod ollama pull mistral:7b-instruct-q5_K_M
```

**Duration:** ~5-10 minutes (5.2GB)

#### Verify
```bash
docker exec rag-ollama-prod ollama list
```

**Expected:**
```
NAME                          ID              SIZE
mistral:7b-instruct-q5_K_M    xxxxxxxxxxxxx   5.2GB
```

---

### 1.9 Verify Backend Deployment

#### Test Health Endpoint (Internal)
```bash
curl http://localhost:8000/api/health | jq '.'
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "neo4j": "connected",
    "ollama": "available"
  }
}
```

#### Test Health Endpoint (External HTTPS)
```bash
curl https://api.diveteacher.io/api/health | jq '.'
```

**Expected:** Same JSON output as above

**AI Agent Success Criteria:**
- ✅ HTTPS works (not HTTP)
- ✅ Neo4j connected
- ✅ Ollama available
- ✅ No SSL certificate errors

---

## 🌐 Part 2: Frontend Deployment (Vercel)

### 2.1 Prepare Repository

#### Ensure Latest Code Pushed
```bash
# On local Mac M1 Max
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
git add .
git commit -m "feat: production deployment Phase 9"
git push origin main
```

#### Verify vercel.json Exists
```bash
cat frontend/vercel.json
```

**Expected Content:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

### 2.2 Deploy to Vercel

**AI Agent: Guide user through Vercel UI**

#### Option A: Vercel Dashboard (Recommended)
1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import from GitHub: `nicozefrench/diveteacher`
4. **Root Directory:** `frontend`
5. **Framework Preset:** Vite
6. **Build Command:** `npm run build` (auto-detected)
7. **Output Directory:** `dist` (auto-detected)
8. Click "Deploy"

#### Option B: Vercel CLI
```bash
# On local machine
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter/frontend
vercel --prod
```

**Prompts:**
- Setup: Yes
- Scope: Choose your Vercel account
- Link to existing: No
- Project name: diveteacher
- Directory: ./
- Override build: No

**Expected Output:**
```
✅ Production: https://diveteacher-xxxxx.vercel.app
```

---

### 2.3 Configure Vercel Environment Variables

#### Access Environment Variables
1. Vercel Dashboard → diveteacher project
2. Settings → Environment Variables
3. Add the following:

| Key | Value | Environment |
|-----|-------|-------------|
| `VITE_API_URL` | `https://api.diveteacher.io` | Production |
| `VITE_SENTRY_DSN` | `https://yyyyy@...sentry.io/1111111` | Production |
| `VITE_SUPABASE_URL` | `https://xxxxx.supabase.co` | Production |
| `VITE_SUPABASE_ANON_KEY` | `eyJhbGc...` | Production |

**AI Agent Warning:** Use production URLs, not localhost!

#### Redeploy After Adding Env Vars
```bash
# Trigger redeploy from Vercel dashboard
# OR via CLI:
vercel --prod
```

---

### 2.4 Configure Custom Domain

#### Add diveteacher.io to Vercel
1. Vercel Dashboard → diveteacher project
2. Settings → Domains
3. Add Domain: `diveteacher.io`
4. Add Domain: `www.diveteacher.io`

#### Update DNS (If Not Done Already)
**Vercel will provide DNS records:**
- A record for `diveteacher.io` → Vercel IP (e.g., 76.76.21.21)
- CNAME for `www.diveteacher.io` → `cname.vercel-dns.com`

#### Add diveteacher.app (Redirect)
1. Add Domain: `diveteacher.app`
2. Configure redirect: `diveteacher.app` → `diveteacher.io` (308 permanent)

**AI Agent Note:** DNS propagation takes 5-60 minutes

#### Verify
```bash
curl -I https://diveteacher.io
# Expected: HTTP/2 200

curl -I https://www.diveteacher.io
# Expected: HTTP/2 200

curl -I https://diveteacher.app
# Expected: HTTP/2 308 (redirect to .io)
```

---

## 🔒 Part 3: Security Configuration

### 3.1 Firewall (DigitalOcean)

#### Configure UFW Firewall
```bash
# On DigitalOcean droplet
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh  # Port 22
ufw allow http  # Port 80 (Certbot)
ufw allow https  # Port 443 (API)
ufw enable

# Verify
ufw status
```

**Expected:**
```
Status: active
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 3.2 Update Backend CORS

#### Verify CORS in .env
```bash
cat /opt/diveteacher/.env | grep CORS_ORIGINS
```

**Expected:**
```
CORS_ORIGINS=https://diveteacher.io,https://www.diveteacher.io
```

#### Restart Backend if Changed
```bash
cd /opt/diveteacher
docker compose -f docker/docker-compose.prod.yml restart backend
```

### 3.3 Secure Neo4j

#### Change Default Password (If Not Done)
```bash
# Already set in .env, but verify it's strong
cat /opt/diveteacher/.env | grep NEO4J_PASSWORD
# Should NOT be: diveteacher_dev_2025 or neo4j
```

#### Neo4j NOT Exposed to Internet
```bash
# Verify Neo4j ports NOT open externally
ufw status | grep 747
# Expected: No output (not exposed)
```

**AI Agent Note:** Neo4j only accessible from within Docker network

---

## 🧪 Part 4: Production Testing

### 4.1 End-to-End Test

#### Test 1: Access Frontend
```bash
open https://diveteacher.io
```

**Expected:** DiveTeacher app loads, no console errors

#### Test 2: Upload Document (Admin)
1. Login as admin (Supabase account from Phase 1)
2. Navigate to admin panel
3. Upload test PDF (< 10MB)
4. **Expected:** Upload succeeds, processing starts

#### Test 3: Monitor Backend Logs
```bash
# On DigitalOcean droplet
docker logs rag-backend-prod -f
```

**Expected:** See document processing logs, no errors

#### Test 4: Query Knowledge Graph
1. In chat interface, ask: "What is in the document?"
2. **Expected:** Streaming response with content from uploaded PDF
3. **Expected:** Response includes FFESSM or SSI badge (if applicable)

#### Test 5: Verify Neo4j Graph
```bash
# SSH tunnel to access Neo4j browser securely
ssh -L 7474:localhost:7474 root@$DROPLET_IP

# Then open locally:
open http://localhost:7474
# Login: neo4j / [your production password]

# Run query:
MATCH (n) RETURN count(n) as total_nodes
```

**Expected:** total_nodes > 0

### 4.2 Performance Test

#### Test API Response Time
```bash
# From local machine
time curl -s https://api.diveteacher.io/api/health
```

**Expected:** < 500ms

#### Test Mistral Inference Speed
```bash
# On droplet
time docker exec rag-ollama-prod ollama run mistral:7b-instruct-q5_K_M "Say hello" --verbose 2>/dev/null
```

**Expected:** First token < 2 seconds (GPU accelerated)

---

## 📊 Part 5: Monitoring & Maintenance

### 5.1 Check Sentry Integration

#### Trigger Test Error (Backend)
```bash
curl https://api.diveteacher.io/api/test-error
```

#### Verify in Sentry
1. Go to https://sentry.io
2. Open diveteacher-backend project
3. **Expected:** See error event appear within 1 minute

#### Trigger Test Error (Frontend)
1. Open https://diveteacher.io
2. Open browser console
3. Type: `throw new Error("Test error")`
4. **Expected:** Error appears in Sentry frontend project

### 5.2 Set Up Log Rotation

```bash
# Create logrotate config
cat > /etc/logrotate.d/nginx-diveteacher <<EOF
/var/log/nginx/access.log
/var/log/nginx/error.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx
    endscript
}
EOF
```

### 5.3 Docker Health Checks

#### Create Monitoring Script
```bash
cat > /opt/diveteacher/health-check.sh <<'EOF'
#!/bin/bash
# DiveTeacher Health Check Script

echo "🔍 DiveTeacher Health Check - $(date)"
echo ""

# Check Docker containers
echo "📦 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=rag-"
echo ""

# Check API health
echo "🏥 API Health:"
curl -s https://api.diveteacher.io/api/health | jq '.'
echo ""

# Check disk space
echo "💾 Disk Space:"
df -h / | tail -1
echo ""

# Check Neo4j nodes
echo "🕸️ Neo4j Graph:"
docker exec rag-neo4j-prod cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n) RETURN count(n) as total_nodes" 2>/dev/null || echo "Neo4j check failed"
echo ""

echo "✅ Health check complete"
EOF

chmod +x /opt/diveteacher/health-check.sh
```

#### Run Daily Health Checks
```bash
# Add to crontab
crontab -e

# Add this line:
0 8 * * * /opt/diveteacher/health-check.sh >> /var/log/diveteacher-health.log 2>&1
```

---

## 🔄 Part 6: Backup & Recovery

### 6.1 Neo4j Backup

#### Manual Backup
```bash
cd /opt/diveteacher
docker compose -f docker/docker-compose.prod.yml stop neo4j

# Backup data volume
tar -czf neo4j-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  /var/lib/docker/volumes/diveteacher_neo4j-data-prod/_data

docker compose -f docker/docker-compose.prod.yml start neo4j
```

#### Automated Daily Backups
```bash
# Create backup script
cat > /opt/diveteacher/backup-neo4j.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=/opt/diveteacher/backups
mkdir -p $BACKUP_DIR

# Keep last 7 days
find $BACKUP_DIR -name "neo4j-backup-*.tar.gz" -mtime +7 -delete

# Create backup
tar -czf $BACKUP_DIR/neo4j-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/docker/volumes/diveteacher_neo4j-data-prod/_data

echo "Backup completed: $(date)"
EOF

chmod +x /opt/diveteacher/backup-neo4j.sh

# Add to crontab (runs at 2 AM daily)
crontab -e
# Add: 0 2 * * * /opt/diveteacher/backup-neo4j.sh >> /var/log/neo4j-backup.log 2>&1
```

### 6.2 Restore from Backup

```bash
# Stop services
cd /opt/diveteacher
docker compose -f docker/docker-compose.prod.yml down

# Restore data
tar -xzf backups/neo4j-backup-YYYYMMDD.tar.gz -C /

# Start services
docker compose -f docker/docker-compose.prod.yml up -d
```

---

## 🚨 Part 7: Troubleshooting Production

### Issue 1: 502 Bad Gateway

**Symptom:** Nginx returns 502, frontend can't reach API

**Diagnosis:**
```bash
# Check backend is running
docker ps --filter "name=rag-backend-prod"

# Check backend logs
docker logs rag-backend-prod --tail 50

# Test backend directly
curl http://localhost:8000/api/health
```

**Solutions:**
1. Backend crashed → Check logs, restart:
```bash
docker compose -f docker/docker-compose.prod.yml restart backend
```

2. Neo4j not connected → Check Neo4j health:
```bash
docker logs rag-neo4j-prod --tail 50
```

### Issue 2: SSL Certificate Expired

**Symptom:** Browser shows SSL error

**Solution:**
```bash
# Renew certificate
certbot renew

# Reload Nginx
systemctl reload nginx
```

### Issue 3: Out of Disk Space

**Symptom:** Docker errors, uploads fail

**Diagnosis:**
```bash
df -h
docker system df
```

**Solution:**
```bash
# Clean Docker
docker system prune -a --volumes

# Remove old backups
find /opt/diveteacher/backups -mtime +30 -delete
```

### Issue 4: High Memory Usage

**Symptom:** Ollama OOM errors, slow responses

**Diagnosis:**
```bash
docker stats
```

**Solutions:**
1. Reduce processing workers:
```bash
nano /opt/diveteacher/.env
# Change: PROCESSING_WORKERS=2 (instead of 4)
docker compose -f docker/docker-compose.prod.yml restart backend
```

2. Upgrade droplet (DigitalOcean dashboard)

---

## 📈 Part 8: Scaling & Optimization

### 8.1 Increase Mistral Performance

#### Use Larger Context Window
```bash
nano /opt/diveteacher/.env
# Change:
RAG_CONTEXT_WINDOW=8000  # Was 4000
```

#### Reduce Temperature for More Accuracy
```bash
RAG_TEMPERATURE=0.05  # Was 0.1 (more deterministic)
```

### 8.2 Neo4j Performance Tuning

#### Increase Neo4j Memory
Edit `docker-compose.prod.yml`:
```yaml
services:
  neo4j:
    environment:
      - NEO4J_dbms_memory_heap_initial__size=2G
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
```

Restart:
```bash
docker compose -f docker/docker-compose.prod.yml restart neo4j
```

---

## ✅ Deployment Checklist (AI Agent)

Before declaring Phase 9 complete:

### DigitalOcean
- [ ] GPU droplet created and running
- [ ] Docker + NVIDIA Docker installed
- [ ] Repository cloned to `/opt/diveteacher`
- [ ] Production `.env` configured (strong passwords, production URLs)
- [ ] Nginx configured and running
- [ ] SSL certificate obtained and auto-renewing
- [ ] Docker services started and healthy
- [ ] Mistral model pulled (5.2GB)
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] Backend API accessible via HTTPS

### Vercel
- [ ] Frontend deployed from GitHub
- [ ] Environment variables set (VITE_API_URL, etc.)
- [ ] Custom domain `diveteacher.io` configured
- [ ] Redirect `diveteacher.app` → `diveteacher.io`
- [ ] DNS propagated (ping domains)
- [ ] HTTPS working on all domains

### Testing
- [ ] Frontend loads without errors
- [ ] Admin can login (Supabase auth)
- [ ] Document upload works
- [ ] Chat query returns streaming response
- [ ] Neo4j graph populated after upload
- [ ] Sentry receiving events (backend + frontend)
- [ ] Health check returns "healthy"
- [ ] API response time < 500ms
- [ ] Mistral inference < 2s first token

### Monitoring
- [ ] Sentry projects configured
- [ ] Health check script running daily
- [ ] Neo4j backups scheduled
- [ ] Log rotation configured
- [ ] Nginx access logs working

### Security
- [ ] Strong Neo4j password
- [ ] Supabase service key kept secret
- [ ] CORS restricted to production domains
- [ ] Firewall blocking unused ports
- [ ] SSL certificate valid
- [ ] `.env` file not in git

**Success Criteria:** All boxes checked = Phase 9 complete, DiveTeacher is LIVE! 🎉

---

## 💰 Cost Summary

| Service | Cost | Billing |
|---------|------|---------|
| DigitalOcean GPU Droplet | $100-150/mo | Monthly |
| Vercel Pro (frontend) | Included | Existing account |
| Supabase (auth + DB) | $0 | Free (< 50k users) |
| Sentry (monitoring) | $0 | Free (< 5k events) |
| Domain (diveteacher.io/.app) | Included | Already purchased |
| **Total** | **~$120/mo** | **DigitalOcean only** |

**AI Agent Note:** Costs stay at $0 until Phase 9 is executed.

---

## 📚 Related Documentation

- **SETUP.md** - Local development (Phases 0-8)
- **CURRENT-CONTEXT.md** - Session memory and progress
- **DIVETEACHER-V1-PLAN.md** - Complete development plan

---

**Last Updated:** October 27, 2025  
**Version:** DiveTeacher V1 - Phase 9  
**AI Agent:** Claude Sonnet 4.5 optimized  
**Status:** ⏸️ NOT YET EXECUTED (Phases 0-8 first)
