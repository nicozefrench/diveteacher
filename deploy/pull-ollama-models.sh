#!/bin/bash
# Pull Ollama models script

set -e

MODELS=("llama3:8b" "mistral:7b" "mixtral:8x7b")

echo "🤖 Pulling Ollama models..."

for model in "${MODELS[@]}"; do
    echo "📥 Pulling $model..."
    docker exec rag-ollama ollama pull $model
done

echo "✅ All models pulled successfully!"
echo ""
echo "Available models:"
docker exec rag-ollama ollama list

