#!/bin/bash
# Vercel Deployment Script

set -e

echo "🚀 Deploying frontend to Vercel..."

cd frontend

# Install Vercel CLI if not installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy to production
echo "🌐 Deploying..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "Don't forget to set environment variables in Vercel dashboard:"
echo "- VITE_API_URL=https://api.your-domain.com"
echo "- VITE_SENTRY_DSN=your_sentry_dsn"

