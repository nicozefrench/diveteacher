# Environment Variables Configuration for Qwen 2.5 7B Q8_0

## Required Environment Variables

Add these variables to your `.env` file in the project root:

```bash
# =============================================================================
# LLM Configuration (Qwen 2.5 7B Q8_0)
# =============================================================================
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0  # 8-bit quantization for optimal RAG quality

# =============================================================================
# RAG Configuration
# =============================================================================
RAG_TOP_K=5              # Number of facts to retrieve from knowledge graph
RAG_TEMPERATURE=0.7      # Balanced creativity/factuality
RAG_MAX_TOKENS=2000      # Max response length
RAG_STREAM=true          # Enable streaming responses

# =============================================================================
# Qwen-Specific Tuning (for RAG downstream tasks)
# =============================================================================
QWEN_TEMPERATURE=0.7     # Optimal for RAG synthesis
QWEN_TOP_P=0.9
QWEN_TOP_K=40
QWEN_NUM_CTX=4096        # Context window (Qwen supports up to 32k)
```

## Instructions

1. Copy these variables to your `.env` file
2. Keep existing variables (NEO4J, ANTHROPIC_API_KEY, etc.)
3. Replace `OLLAMA_MODEL` if it was previously set to `mistral` or `llama3`
4. Add the new RAG and QWEN configuration variables

## Notes

- **Q8_0 Quantization:** Optimal for RAG quality (98/100)
- **Expected Performance (Mac M1 Max CPU):** 30-40 tokens/sec
- **Memory Usage:** ~10GB RAM / 32GB total
- **Model Source:** [HuggingFace - bartowski/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF)

