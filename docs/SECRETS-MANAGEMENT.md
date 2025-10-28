# 🔐 Environment Variables & Secrets Management Guide

## Local Development (Current Setup)

### How It Works
```
1. .env file on your Mac
   ↓
2. docker-compose.dev.yml reads: env_file: - ../.env
   ↓
3. Docker Compose loads ALL variables into container
   ↓
4. Backend reads via Pydantic Settings (config.py)
```

**Security:**
- ✅ `.env` in `.gitignore` → Never committed to git
- ✅ Secrets stay on your local machine
- ✅ Each developer has their own `.env`

---

## Production Deployment (DigitalOcean)

### The Problem
```
Git Repository (GitHub)
  ├── Code ✅
  ├── Docker configs ✅
  └── .env ❌ (blocked by .gitignore)

When you git push → DigitalOcean pulls code
Result: NO .env file → Services fail ❌
```

### ✅ Solution: Manual `.env` on Server

**Step-by-Step Production Setup:**

#### 1. Initial Server Setup (One Time)
```bash
# SSH into DigitalOcean GPU Droplet
ssh root@your-droplet-ip

# Clone repository
cd /opt
git clone https://github.com/nicozefrench/diveteacher.git rag-system
cd rag-system

# Create production .env (manually)
nano .env

# Copy content from env.production.template
# Replace ALL "REPLACE_ME" values with real secrets:
# - Strong NEO4J_PASSWORD
# - Production ANTHROPIC_API_KEY (separate from dev)
# - Production OPENAI_API_KEY (separate from dev)
# - Supabase production keys
# - Sentry production DSNs
# Save (Ctrl+O, Enter, Ctrl+X)

# Secure the file
chmod 600 .env
chown root:root .env

# Verify it exists
ls -la .env
# Should show: -rw------- 1 root root
```

#### 2. Deploy Services
```bash
# Start production stack
docker-compose -f docker/docker-compose.prod.yml up -d

# Check services
docker-compose -f docker/docker-compose.prod.yml ps

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f backend
```

#### 3. Future Code Updates
```bash
# SSH into server
ssh root@your-droplet-ip
cd /opt/rag-system

# Pull latest code (does NOT touch .env)
git pull origin main

# Rebuild and restart (keeps .env)
docker-compose -f docker/docker-compose.prod.yml up -d --build

# The .env file stays untouched! ✅
```

---

## 🔐 Security Best Practices

### 1. Separate Dev/Prod Keys
```bash
# Local .env (Development)
ANTHROPIC_API_KEY=sk-ant-...-dev
OPENAI_API_KEY=sk-proj-...-dev

# Server .env (Production)
ANTHROPIC_API_KEY=sk-ant-...-prod
OPENAI_API_KEY=sk-proj-...-prod
```

**Why?**
- If dev key leaks → production unaffected
- Different rate limits per environment
- Easier tracking/billing

### 2. Strong Production Passwords
```bash
# ❌ BAD (same as dev)
NEO4J_PASSWORD=diveteacher_dev_2025

# ✅ GOOD (strong, unique)
NEO4J_PASSWORD=Dt_Pr0d_2025_8x9#mK$vL2qR
```

### 3. File Permissions on Server
```bash
# Protect .env file
chmod 600 .env  # Only root can read/write
chown root:root .env

# Verify
ls -la .env
# Should show: -rw------- 1 root root

# Test (as non-root user)
su - deployer
cat /opt/rag-system/.env
# Should show: Permission denied ✅
```

### 4. Backup Strategy
```bash
# Option A: Secure note (1Password, LastPass)
# Store production .env in password manager

# Option B: Encrypted backup
gpg --symmetric --cipher-algo AES256 .env
# Creates .env.gpg (encrypted)
# Store .env.gpg in secure location

# To restore:
gpg --decrypt .env.gpg > .env
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Create `env.production.template` in git (no secrets)
- [ ] Document production requirements
- [ ] Generate production API keys (separate from dev)
- [ ] Choose strong Neo4j password
- [ ] Set up Sentry production project
- [ ] Set up Supabase production project

### Server Setup
- [ ] Create DigitalOcean GPU Droplet
- [ ] SSH access configured
- [ ] Clone git repository
- [ ] Create `.env` manually (from template)
- [ ] Fill in ALL secrets (no REPLACE_ME left)
- [ ] Set `chmod 600 .env`
- [ ] Test Docker Compose starts successfully
- [ ] Verify all services healthy

### Post-Deployment
- [ ] Backup production `.env` to secure location
- [ ] Test API endpoints
- [ ] Monitor Sentry for errors
- [ ] Document rollback procedure
- [ ] Schedule .env backup rotation

---

## 🔄 Alternative: Docker Secrets (Advanced)

**For Docker Swarm/Kubernetes (not needed for single server):**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    secrets:
      - anthropic_key
      - openai_key
      - neo4j_password
    environment:
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key

secrets:
  anthropic_key:
    external: true
  openai_key:
    external: true
  neo4j_password:
    external: true
```

```bash
# Create secrets (one time)
echo "sk-ant-..." | docker secret create anthropic_key -
echo "sk-..." | docker secret create openai_key -
echo "password" | docker secret create neo4j_password -

# Start service
docker stack deploy -c docker-compose.prod.yml diveteacher
```

**Pros:**
- Encrypted at rest
- Automatic rotation support
- Auditing

**Cons:**
- Requires Docker Swarm (overkill for one server)
- More complex setup
- Code changes needed (read from `/run/secrets/*`)

**Recommendation:** Use manual `.env` for simplicity until you need multi-server orchestration.

---

## 🌐 Cloud Provider Integrations

### DigitalOcean App Platform (Managed)
If using DO App Platform instead of Droplet:

```bash
# Via CLI
doctl apps create --spec .do/app.yaml

# Set secrets
doctl apps update $APP_ID \
  --env ANTHROPIC_API_KEY=secret:anthropic_key

# Or via Dashboard:
# Apps → Your App → Settings → Environment Variables
# Add each secret manually
```

### Vercel (Frontend)
```bash
# Via CLI
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production

# Or via Dashboard:
# Project → Settings → Environment Variables
# Add for Production environment
```

### AWS (Future Migration)
- **Secrets Manager:** Store secrets, reference in ECS
- **Parameter Store:** Free tier, similar functionality
- **ECS Task Definitions:** Inject secrets at runtime

---

## ❓ FAQ

### Q: Do I commit `.env` to git?
**A: NO! Never.** It's in `.gitignore` for a reason. Secrets would be exposed.

### Q: How does production get the `.env` then?
**A: Manually create it on the server.** Copy from template, fill secrets, never commit.

### Q: What if I need to update a secret in production?
```bash
# SSH to server
ssh root@your-droplet-ip
cd /opt/rag-system

# Edit .env
nano .env
# Update the secret
# Save

# Restart services
docker-compose -f docker/docker-compose.prod.yml restart backend

# Or reload without downtime
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Q: Can I use environment variables instead of `.env` file?
**A: Yes, but `.env` is cleaner.** Docker Compose supports both:
```bash
# Option 1: .env file (recommended)
docker-compose up -d

# Option 2: Export env vars (messy)
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
# ... 20+ more exports
docker-compose up -d
```

### Q: How do I rotate API keys safely?
```bash
# 1. Generate new keys (Anthropic/OpenAI dashboards)
# 2. Update .env on server
nano .env
# 3. Restart services
docker-compose restart backend
# 4. Verify services work
docker-compose logs backend
# 5. Revoke old keys (after confirmation)
```

---

## 📚 Related Documentation

- `env.production.template` - Production environment template
- `docker/docker-compose.prod.yml` - Production Docker config
- `docs/DEPLOYMENT.md` - Full deployment guide
- `CURRENT-CONTEXT.md` - Session history

---

**Last Updated:** October 28, 2025  
**Phase:** 1.0 Complete  
**Status:** Production-Ready 🟢

