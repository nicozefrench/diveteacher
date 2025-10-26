#!/bin/bash
# DigitalOcean Droplet Setup Script

set -e

echo "🚀 Setting up RAG Knowledge Graph on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/rag-app
sudo chown -R $USER:$USER /opt/rag-app

# Create persistent volumes
echo "💾 Creating persistent volumes..."
sudo mkdir -p /opt/neo4j-data /opt/neo4j-logs /opt/ollama-models /opt/rag-uploads
sudo chown -R $USER:$USER /opt/neo4j-data /opt/neo4j-logs /opt/ollama-models /opt/rag-uploads

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Install Certbot for SSL
echo "🔐 Installing Certbot..."
sudo apt-get install -y certbot python3-certbot-nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ DigitalOcean setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to /opt/rag-app"
echo "2. Copy env.template to .env and configure"
echo "3. Run: docker-compose -f docker/docker-compose.prod.yml up -d"
echo "4. Pull Ollama model: docker exec rag-ollama ollama pull llama3:8b"
echo "5. Configure SSL: sudo certbot --nginx -d api.your-domain.com"

