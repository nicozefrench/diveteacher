# Deployment Guide - RAG Knowledge Graph

## Overview

This boilerplate uses a hybrid deployment:
- **Frontend**: Vercel (free tier, CDN, auto-deploy)
- **Backend**: DigitalOcean Droplet (Nginx + Docker)

---

## Prerequisites

- DigitalOcean account (or any VPS provider)
- Vercel account
- Domain name (optional but recommended)

---

## Part 1: Backend Deployment (DigitalOcean)

### 1.1 Create Droplet

- **Image**: Ubuntu 22.04 LTS
- **Plan**: CPU-Optimized 4GB RAM ($24/month) or Basic 2GB ($12/month)
- **Datacenter**: Choose closest to users
- **Add SSH key**: Your public key

### 1.2 Connect to Droplet

```bash
ssh root@your-droplet-ip
```

### 1.3 Run Setup Script

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/main/deploy/digitalocean-setup.sh | bash
```

This installs: Docker, Docker Compose, Nginx, Certbot, and creates directories.

### 1.4 Clone Repository

```bash
cd /opt/rag-app
git clone https://github.com/your-username/rag-kg-boilerplate.git .
```

### 1.5 Configure Environment

```bash
cp env.template .env
nano .env
```

**Critical changes:**
```bash
NEO4J_PASSWORD=your_strong_password_here
FRONTEND_URL=https://your-app.vercel.app
SENTRY_DSN_BACKEND=your_sentry_dsn
SENTRY_ENVIRONMENT=production
DEBUG=false
```

### 1.6 Start Services

```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

### 1.7 Pull Ollama Model

```bash
docker exec rag-ollama-prod ollama pull llama3:8b
```

### 1.8 Configure SSL (if using domain)

```bash
# Point your domain to droplet IP first
sudo certbot --nginx -d api.your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

### 1.9 Verify Deployment

```bash
# Check services
docker ps

# Test API
curl http://localhost/api/health
```

---

## Part 2: Frontend Deployment (Vercel)

### 2.1 Push to GitHub

```bash
# From local machine
cd rag-kg-boilerplate
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/rag-kg-boilerplate.git
git push -u origin main
```

### 2.2 Import to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. **Root Directory**: `frontend`
4. **Framework Preset**: Vite
5. Click "Deploy"

### 2.3 Configure Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```
VITE_API_URL=https://api.your-domain.com
VITE_SENTRY_DSN=your_sentry_frontend_dsn
```

### 2.4 Redeploy

After adding env vars, trigger a redeploy.

---

## Part 3: Post-Deployment

### 3.1 Update Backend CORS

Update `.env` on DigitalOcean:

```bash
CORS_ORIGINS=https://your-app.vercel.app
```

Restart backend:

```bash
docker-compose -f docker/docker-compose.prod.yml restart backend
```

### 3.2 Test End-to-End

1. Visit your Vercel URL
2. Upload a PDF
3. Wait for processing
4. Ask a question

---

## Monitoring

### Sentry Setup

1. Create account at sentry.io
2. Create **two projects**: backend (Python) + frontend (React)
3. Copy DSNs to `.env` and Vercel env vars

### Check Logs

```bash
# Backend logs
docker-compose -f docker/docker-compose.prod.yml logs -f backend

# Neo4j logs
docker-compose -f docker/docker-compose.prod.yml logs -f neo4j

# Nginx logs
sudo tail -f /var/log/nginx/access.log
```

---

## Backup Strategy

### Neo4j Backup

```bash
# On DigitalOcean droplet
cd /opt
sudo tar -czf neo4j-backup-$(date +%Y%m%d).tar.gz neo4j-data/

# Download to local
scp root@your-droplet-ip:/opt/neo4j-backup-*.tar.gz ./
```

### Automated Backups

Add to crontab:

```bash
0 2 * * * cd /opt && tar -czf neo4j-backup-$(date +\%Y\%m\%d).tar.gz neo4j-data/
```

---

## Scaling

### Increase Droplet Resources

If performance is slow:
1. Resize droplet (DigitalOcean dashboard)
2. Restart services

### Multiple Workers

Edit `.env`:

```bash
PROCESSING_WORKERS=4  # Increase for faster document processing
```

---

## Troubleshooting

### Issue: Vercel can't reach backend

**Solution**: Check CORS settings and firewall rules.

### Issue: Ollama out of memory

**Solution**: Use smaller model or increase droplet RAM.

```bash
# Use smaller model
docker exec rag-ollama-prod ollama pull llama3.2:1b
```

---

## Cost Estimate

| Service | Plan | Cost |
|---------|------|------|
| Vercel (frontend) | Free | $0 |
| DigitalOcean (backend) | 2GB Basic | $12/mo |
| DigitalOcean (backend) | 4GB CPU-Opt | $24/mo |
| Domain (optional) | - | $10-15/yr |
| Sentry (monitoring) | Free tier | $0 |

**Total**: $12-24/month for fully hosted RAG application

---

## Security Checklist

- [ ] Strong Neo4j password set
- [ ] SSL certificate configured (HTTPS)
- [ ] Firewall rules configured (ports 80, 443, 22 only)
- [ ] .env file not committed to git
- [ ] Sentry error tracking enabled
- [ ] Regular Neo4j backups scheduled
- [ ] API rate limiting configured (TODO: add to FastAPI)
- [ ] Docker images updated regularly

---

For support, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

