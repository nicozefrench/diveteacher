# Ollama Deployment Guide: Mistral 7B on DigitalOcean

## Executive Summary

This guide provides comprehensive instructions for deploying, configuring, debugging, and using Ollama with the Mistral 7B model on a DigitalOcean droplet. It is optimized for AI agents running Claude Sonnet 4.5 to implement and maintain this infrastructure.

## Table of Contents

1. [What is Ollama](#what-is-ollama)
2. [System Requirements](#system-requirements)
3. [Installation on DigitalOcean](#installation-on-digitalocean)
4. [Installing and Running Mistral 7B](#installing-and-running-mistral-7b)
5. [API Usage](#api-usage)
6. [Configuration and Optimization](#configuration-and-optimization)
7. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Security Best Practices](#security-best-practices)
10. [Resources and Links](#resources-and-links)

---

## What is Ollama

Ollama is a lightweight, extensible framework for running large language models locally. It provides:

- **Easy Model Management**: Download and run models with simple commands
- **REST API**: HTTP API for integration with applications
- **Model Library**: Access to various open-source models (Llama, Mistral, CodeLlama, etc.)
- **Resource Efficiency**: Optimized for running models on consumer hardware
- **Cross-platform**: Supports Linux, macOS, and Windows

**Official Repository**: https://github.com/ollama/ollama

**Official Documentation**: https://github.com/ollama/ollama/blob/main/docs/README.md

---

## System Requirements

### Minimum Requirements for Mistral 7B

- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space minimum
- **CPU**: Modern multi-core processor
- **GPU**: Optional but significantly improves performance (NVIDIA GPU with CUDA support)

### Recommended DigitalOcean Droplet Specifications

For Mistral 7B without GPU:
- **Droplet Type**: General Purpose or CPU-Optimized
- **Size**: 16GB RAM / 4 vCPUs minimum
- **OS**: Ubuntu 22.04 LTS (recommended)

For better performance with GPU:
- **Droplet Type**: GPU Droplet (if available in your region)
- **Size**: Varies based on GPU availability

---

## Installation on DigitalOcean

### Step 1: Create and Access Your Droplet

```bash
# SSH into your droplet
ssh root@your_droplet_ip
```

### Step 2: Update System Packages

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git build-essential
```

### Step 3: Install Ollama

**Official Installation Script** (Recommended):

```bash
# Download and run the official installation script
curl -fsSL https://ollama.com/install.sh | sh
```

**Manual Installation** (Alternative):

```bash
# Download the Ollama binary
curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama

# Make it executable
chmod +x /usr/local/bin/ollama

# Create ollama user
sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama

# Create systemd service
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Step 4: Verify Installation

```bash
# Check if Ollama is running
systemctl status ollama

# Test Ollama command
ollama --version

# Check if API is accessible
curl http://localhost:11434/api/version
```

**Expected Output**:
```json
{"version":"0.x.x"}
```

---

## Installing and Running Mistral 7B

### Step 1: Pull the Mistral Model

```bash
# Pull Mistral 7B model
ollama pull mistral

# This will download approximately 4.1GB of data
```

**Available Mistral Variants**:
- `mistral`: Latest Mistral 7B (default)
- `mistral:7b-instruct`: Instruction-tuned version
- `mistral:7b-text`: Base text model

### Step 2: List Available Models

```bash
# List all downloaded models
ollama list
```

**Expected Output**:
```
NAME              ID              SIZE      MODIFIED
mistral:latest    abc123def456    4.1 GB    2 minutes ago
```

### Step 3: Run the Model

**Interactive Mode**:
```bash
# Start interactive chat with Mistral
ollama run mistral
```

**Single Query Mode**:
```bash
# Run a single prompt
ollama run mistral "Explain quantum computing in simple terms"
```

### Step 4: Test Model Performance

```bash
# Simple test prompt
echo "What is the capital of France?" | ollama run mistral

# Measure response time
time ollama run mistral "Write a haiku about programming" --verbose
```

---

## API Usage

Ollama provides a REST API running on `http://localhost:11434` by default.

### Generate Completion

**Endpoint**: `POST /api/generate`

```bash
# Basic completion request
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

**Response**:
```json
{
  "model": "mistral",
  "created_at": "2024-10-27T12:00:00.000Z",
  "response": "The sky appears blue because...",
  "done": true,
  "total_duration": 5000000000,
  "load_duration": 1000000000,
  "prompt_eval_count": 10,
  "eval_count": 50
}
```

### Streaming Responses

```bash
# Stream responses for real-time output
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Tell me a story",
  "stream": true
}'
```

### Chat Completion

**Endpoint**: `POST /api/chat`

```bash
# Chat-style interaction
curl http://localhost:11434/api/chat -d '{
  "model": "mistral",
  "messages": [
    {
      "role": "user",
      "content": "What is machine learning?"
    }
  ],
  "stream": false
}'
```

### Advanced Parameters

```bash
# Request with custom parameters
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Explain AI",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "num_predict": 100,
    "stop": ["Human:", "AI:"]
  }
}'
```

**Key Parameters**:
- `temperature` (0-2): Controls randomness (default: 0.8)
- `top_p` (0-1): Nucleus sampling threshold (default: 0.9)
- `top_k`: Limits token selection pool (default: 40)
- `num_predict`: Maximum tokens to generate (default: -1 for unlimited)
- `repeat_penalty`: Penalty for repetition (default: 1.1)
- `num_ctx`: Context window size (default: 2048)

### List Models via API

```bash
# Get list of available models
curl http://localhost:11434/api/tags
```

### Show Model Information

```bash
# Get detailed model information
curl http://localhost:11434/api/show -d '{
  "name": "mistral"
}'
```

### Python Example

```python
import requests
import json

# API endpoint
url = "http://localhost:11434/api/generate"

# Request payload
payload = {
    "model": "mistral",
    "prompt": "What is the meaning of life?",
    "stream": False
}

# Make request
response = requests.post(url, json=payload)

# Parse response
result = response.json()
print(result['response'])
```

### Node.js Example

```javascript
const axios = require('axios');

async function generateCompletion(prompt) {
  try {
    const response = await axios.post('http://localhost:11434/api/generate', {
      model: 'mistral',
      prompt: prompt,
      stream: false
    });
    
    return response.data.response;
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Usage
generateCompletion('Explain neural networks')
  .then(response => console.log(response));
```

---

## Configuration and Optimization

### Environment Variables

Configure Ollama behavior via environment variables:

```bash
# Edit systemd service
sudo systemctl edit ollama

# Add environment variables
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=5m"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

**Key Environment Variables**:

- `OLLAMA_HOST`: Server bind address (default: 127.0.0.1:11434)
- `OLLAMA_ORIGINS`: CORS origins (default: localhost only)
- `OLLAMA_MODELS`: Model storage path (default: ~/.ollama/models)
- `OLLAMA_KEEP_ALIVE`: Model memory retention time (default: 5m)
- `OLLAMA_NUM_PARALLEL`: Concurrent request limit (default: 1)
- `OLLAMA_MAX_LOADED_MODELS`: Max models in memory (default: 1)
- `OLLAMA_DEBUG`: Enable debug logging (set to 1)

### Expose Ollama to External Access

**⚠️ Security Warning**: Only expose if necessary and use proper security measures.

```bash
# Method 1: Environment variable (recommended)
sudo systemctl edit ollama

[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

sudo systemctl daemon-reload
sudo systemctl restart ollama

# Method 2: Direct command
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

### Configure Firewall

```bash
# Allow Ollama port through UFW
sudo ufw allow 11434/tcp

# Or restrict to specific IP
sudo ufw allow from YOUR_IP to any port 11434
```

### Performance Optimization

#### 1. Increase Context Window

```bash
# Larger context for better long-form generation
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Your prompt here",
  "options": {
    "num_ctx": 4096
  }
}'
```

#### 2. Adjust CPU Threads

```bash
# Set number of CPU threads
Environment="OLLAMA_NUM_THREADS=8"
```

#### 3. Model Quantization

Mistral is available in different quantization levels:

- `Q4_0`: Smallest, fastest (default for mistral:latest)
- `Q4_K_M`: Balanced quality/size
- `Q5_K_M`: Higher quality, larger
- `Q8_0`: Highest quality, largest

```bash
# Pull specific quantization
ollama pull mistral:7b-instruct-q8_0
```

#### 4. Reduce Memory Usage

```bash
# Lower parallel requests
Environment="OLLAMA_NUM_PARALLEL=1"

# Unload models faster
Environment="OLLAMA_KEEP_ALIVE=1m"
```

### Modelfile Customization

Create custom model configurations:

```bash
# Create a Modelfile
cat > Modelfile <<EOF
FROM mistral

# Set custom parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# Set system prompt
SYSTEM """
You are a helpful AI assistant specialized in technical documentation.
Always provide clear, concise, and accurate information.
"""
EOF

# Create custom model
ollama create my-mistral -f Modelfile

# Use custom model
ollama run my-mistral "Your prompt here"
```

---

## Debugging and Troubleshooting

### Common Issues and Solutions

#### Issue 1: Ollama Service Won't Start

**Diagnosis**:
```bash
# Check service status
sudo systemctl status ollama

# View logs
sudo journalctl -u ollama -n 50 --no-pager

# Check if port is in use
sudo lsof -i :11434
```

**Solutions**:
```bash
# Kill conflicting process
sudo kill $(sudo lsof -t -i:11434)

# Restart service
sudo systemctl restart ollama

# Check permissions
sudo chown -R ollama:ollama /usr/share/ollama
```

#### Issue 2: Model Download Fails

**Diagnosis**:
```bash
# Test internet connectivity
ping -c 4 ollama.com

# Check disk space
df -h

# Check available models
curl https://ollama.com/api/tags
```

**Solutions**:
```bash
# Clear partial downloads
rm -rf ~/.ollama/models/*

# Retry download with verbose output
ollama pull mistral --verbose

# Download to specific location
OLLAMA_MODELS=/path/to/storage ollama pull mistral
```

#### Issue 3: Out of Memory Errors

**Diagnosis**:
```bash
# Check memory usage
free -h

# Monitor in real-time
watch -n 1 free -h

# Check swap
swapon --show
```

**Solutions**:
```bash
# Add swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Reduce model memory footprint
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "test",
  "options": {
    "num_ctx": 1024
  }
}'

# Use smaller quantization
ollama pull mistral:7b-instruct-q4_0
```

#### Issue 4: Slow Response Times

**Diagnosis**:
```bash
# Check CPU usage
top -p $(pgrep ollama)

# Monitor disk I/O
iostat -x 1

# Test response time
time curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "test",
  "stream": false
}'
```

**Solutions**:
```bash
# Increase CPU threads
sudo systemctl edit ollama
Environment="OLLAMA_NUM_THREADS=$(nproc)"

# Use SSD storage
# Move models to SSD-backed storage
OLLAMA_MODELS=/mnt/ssd/ollama ollama serve

# Reduce context window
# Use num_ctx: 2048 instead of 4096
```

#### Issue 5: API Connection Refused

**Diagnosis**:
```bash
# Check if service is running
systemctl is-active ollama

# Test local connection
curl http://localhost:11434/api/version

# Check firewall
sudo ufw status

# Check listening ports
sudo netstat -tlnp | grep 11434
```

**Solutions**:
```bash
# Start service if stopped
sudo systemctl start ollama

# Bind to all interfaces
sudo systemctl edit ollama
Environment="OLLAMA_HOST=0.0.0.0:11434"
sudo systemctl restart ollama

# Allow through firewall
sudo ufw allow 11434/tcp

# Check CORS settings
Environment="OLLAMA_ORIGINS=*"
```

#### Issue 6: Model Not Found

**Diagnosis**:
```bash
# List downloaded models
ollama list

# Check model storage
ls -lh ~/.ollama/models/

# Verify model name
ollama list | grep mistral
```

**Solutions**:
```bash
# Pull the model
ollama pull mistral

# Use exact model name
ollama run mistral:latest

# Verify model exists before API call
curl http://localhost:11434/api/tags
```

### Debug Mode

Enable detailed logging:

```bash
# Enable debug mode
sudo systemctl edit ollama

[Service]
Environment="OLLAMA_DEBUG=1"

sudo systemctl daemon-reload
sudo systemctl restart ollama

# View debug logs
sudo journalctl -u ollama -f
```

### Health Check Script

```bash
#!/bin/bash
# ollama-health-check.sh

echo "=== Ollama Health Check ==="

# Check service status
echo -n "Service Status: "
systemctl is-active ollama

# Check API response
echo -n "API Status: "
curl -s http://localhost:11434/api/version > /dev/null && echo "OK" || echo "FAILED"

# Check available models
echo "Available Models:"
ollama list

# Check memory usage
echo "Memory Usage:"
free -h | grep Mem

# Check disk space
echo "Disk Space:"
df -h | grep -E '^/dev/'

# Check CPU usage
echo "CPU Usage (ollama process):"
ps aux | grep ollama | grep -v grep | awk '{print $3"%"}'

echo "=== End Health Check ==="
```

---

## Monitoring and Maintenance

### System Monitoring

```bash
# Monitor resource usage
htop

# Monitor Ollama specifically
watch -n 1 'ps aux | grep ollama | grep -v grep'

# Monitor API requests (logs)
sudo journalctl -u ollama -f | grep "POST"
```

### Log Management

```bash
# View recent logs
sudo journalctl -u ollama -n 100

# Follow logs in real-time
sudo journalctl -u ollama -f

# Filter by time
sudo journalctl -u ollama --since "1 hour ago"

# Export logs
sudo journalctl -u ollama --since today > ollama-logs.txt
```

### Backup and Recovery

```bash
# Backup models
tar -czf ollama-models-backup.tar.gz ~/.ollama/models/

# Backup configuration
sudo cp /etc/systemd/system/ollama.service /backup/ollama.service.bak

# Restore models
tar -xzf ollama-models-backup.tar.gz -C ~/

# Restore configuration
sudo cp /backup/ollama.service.bak /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Automated Monitoring Script

```bash
#!/bin/bash
# ollama-monitor.sh

LOGFILE="/var/log/ollama-monitor.log"
ALERT_THRESHOLD=90  # Memory threshold percentage

while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  
  # Check if service is running
  if ! systemctl is-active --quiet ollama; then
    echo "$TIMESTAMP - ALERT: Ollama service is down" >> $LOGFILE
    sudo systemctl start ollama
  fi
  
  # Check memory usage
  MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' | cut -d. -f1)
  if [ $MEM_USAGE -gt $ALERT_THRESHOLD ]; then
    echo "$TIMESTAMP - ALERT: Memory usage at ${MEM_USAGE}%" >> $LOGFILE
  fi
  
  # Check disk space
  DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
  if [ $DISK_USAGE -gt $ALERT_THRESHOLD ]; then
    echo "$TIMESTAMP - ALERT: Disk usage at ${DISK_USAGE}%" >> $LOGFILE
  fi
  
  # Log status
  echo "$TIMESTAMP - Status: OK (Mem: ${MEM_USAGE}%, Disk: ${DISK_USAGE}%)" >> $LOGFILE
  
  sleep 300  # Check every 5 minutes
done
```

### Performance Benchmarking

```bash
#!/bin/bash
# benchmark-ollama.sh

echo "=== Ollama Performance Benchmark ==="

PROMPTS=(
  "What is 2+2?"
  "Explain quantum computing in one sentence."
  "Write a haiku about technology."
)

for PROMPT in "${PROMPTS[@]}"; do
  echo "Testing prompt: $PROMPT"
  
  START=$(date +%s.%N)
  
  curl -s http://localhost:11434/api/generate -d "{
    \"model\": \"mistral\",
    \"prompt\": \"$PROMPT\",
    \"stream\": false
  }" > /dev/null
  
  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)
  
  echo "Response time: ${DURATION}s"
  echo "---"
done
```

---

## Security Best Practices

### 1. Network Security

```bash
# Restrict access to localhost only (default)
Environment="OLLAMA_HOST=127.0.0.1:11434"

# If external access needed, use reverse proxy
sudo apt install nginx

# Nginx config for Ollama
sudo tee /etc/nginx/sites-available/ollama <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Authentication

Ollama doesn't have built-in authentication. Use a reverse proxy with auth:

```bash
# Install Apache utilities for htpasswd
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd username

# Update Nginx config
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://localhost:11434;
}
```

### 3. SSL/TLS Encryption

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 4. Rate Limiting

```nginx
# Add to Nginx config
limit_req_zone $binary_remote_addr zone=ollama_limit:10m rate=10r/s;

server {
    location / {
        limit_req zone=ollama_limit burst=20 nodelay;
        proxy_pass http://localhost:11434;
    }
}
```

### 5. File Permissions

```bash
# Secure Ollama directories
sudo chown -R ollama:ollama /usr/share/ollama
sudo chmod 700 /usr/share/ollama

# Secure model storage
chmod 700 ~/.ollama
```

### 6. Regular Updates

```bash
# Update Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### 7. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (critical!)
sudo ufw allow 22/tcp

# Allow Ollama only from specific IP
sudo ufw allow from YOUR_IP to any port 11434

# Check rules
sudo ufw status numbered
```

---

## Resources and Links

### Official Resources

- **Ollama GitHub Repository**: https://github.com/ollama/ollama
- **Ollama Documentation**: https://github.com/ollama/ollama/blob/main/docs/README.md
- **Ollama Model Library**: https://ollama.com/library
- **Ollama API Documentation**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Ollama FAQ**: https://github.com/ollama/ollama/blob/main/docs/faq.md
- **Ollama Troubleshooting**: https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md

### Mistral Resources

- **Mistral AI Official**: https://mistral.ai/
- **Mistral 7B on Hugging Face**: https://huggingface.co/mistralai/Mistral-7B-v0.1
- **Mistral Documentation**: https://docs.mistral.ai/

### Model Information

- **Ollama Mistral Page**: https://ollama.com/library/mistral
- **Available Mistral Tags**: https://ollama.com/library/mistral/tags
- **Model Quantization Info**: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#quantization

### API and Integration

- **REST API Reference**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **OpenAI Compatibility**: https://github.com/ollama/ollama/blob/main/docs/openai.md
- **Modelfile Specification**: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
- **Import Models**: https://github.com/ollama/ollama/blob/main/docs/import.md

### DigitalOcean Resources

- **DigitalOcean Documentation**: https://docs.digitalocean.com/
- **Droplet Tutorials**: https://docs.digitalocean.com/products/droplets/
- **Ubuntu on DigitalOcean**: https://marketplace.digitalocean.com/apps/ubuntu

### Community and Support

- **Ollama Discord**: https://discord.gg/ollama
- **Ollama GitHub Issues**: https://github.com/ollama/ollama/issues
- **Ollama Discussions**: https://github.com/ollama/ollama/discussions

### Related Tools

- **Open WebUI** (Web interface for Ollama): https://github.com/open-webui/open-webui
- **Ollama Python Library**: https://github.com/ollama/ollama-python
- **Ollama JavaScript Library**: https://github.com/ollama/ollama-js

### Performance and Optimization

- **GPU Support**: https://github.com/ollama/ollama/blob/main/docs/gpu.md
- **Docker Support**: https://github.com/ollama/ollama/blob/main/docs/docker.md
- **Linux Installation**: https://github.com/ollama/ollama/blob/main/docs/linux.md

---

## Quick Reference Commands

```bash
# Installation
curl -fsSL https://ollama.com/install.sh | sh

# Service Management
sudo systemctl start ollama
sudo systemctl stop ollama
sudo systemctl restart ollama
sudo systemctl status ollama

# Model Management
ollama pull mistral
ollama list
ollama rm mistral
ollama run mistral

# API Testing
curl http://localhost:11434/api/version
curl http://localhost:11434/api/tags
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"test"}'

# Debugging
sudo journalctl -u ollama -f
ollama --version
ps aux | grep ollama

# Performance
free -h
df -h
htop
```

---

## AI Agent Implementation Checklist

- [ ] Verify DigitalOcean droplet meets minimum requirements (16GB RAM)
- [ ] SSH access to droplet configured
- [ ] System packages updated (`apt update && apt upgrade`)
- [ ] Ollama installed via official script
- [ ] Ollama service running and enabled
- [ ] Mistral 7B model downloaded (`ollama pull mistral`)
- [ ] API accessibility verified (localhost:11434)
- [ ] Environment variables configured (if needed)
- [ ] Firewall rules set (if external access required)
- [ ] SSL/TLS configured (if external access required)
- [ ] Monitoring script deployed
- [ ] Backup procedure established
- [ ] Health check routine implemented
- [ ] Performance benchmarked
- [ ] Documentation reviewed

---

## Notes for AI Agent

### Critical Considerations

1. **Resource Management**: Mistral 7B requires significant memory. Monitor RAM usage continuously.

2. **Error Handling**: Implement robust error handling for:
   - Out of memory conditions
   - Network timeouts
   - Model loading failures
   - API connection issues

3. **Concurrent Requests**: Default is 1 parallel request. Adjust `OLLAMA_NUM_PARALLEL` based on available resources.

4. **Context Window**: Default 2048 tokens. Larger contexts require more memory.

5. **Response Streaming**: Use streaming for long-form generation to improve user experience.

6. **Model Loading**: First request after service start or model change is slower (model loading time).

7. **Persistence**: Models remain in memory for `OLLAMA_KEEP_ALIVE` duration (default 5m).

### Debugging Strategy

1. Always check service status first: `systemctl status ollama`
2. Review logs for errors: `journalctl -u ollama -n 50`
3. Verify model availability: `ollama list`
4. Test API connectivity: `curl localhost:11434/api/version`
5. Monitor resources: `free -h` and `df -h`
6. Check network if external access: `curl YOUR_IP:11434/api/version`

---

**Document Version**: 1.0  
**Last Updated**: October 2025  
**Target Agent**: Claude Sonnet 4.5  
**Deployment Platform**: DigitalOcean Ubuntu 22.04 LTS  
**Model**: Mistral 7B

