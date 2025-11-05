"""
Configuration settings using Pydantic Settings

All environment variables are loaded from .env file or system environment.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, claude, openai
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q8_0"  # Qwen 2.5 7B Q8_0 for optimal RAG quality
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    OPENROUTER_API_KEY: Optional[str] = None  # For Mistral via OpenRouter (Graphiti)
    GEMINI_API_KEY: Optional[str] = None  # For Gemini 2.5 Flash-Lite (Graphiti LLM operations)

    # RAG Configuration
    RAG_TOP_K: int = 5  # Number of facts to retrieve from knowledge graph
    RAG_TEMPERATURE: float = 0.7  # Balanced creativity/factuality
    RAG_MAX_TOKENS: int = 2000  # Max response length
    RAG_STREAM: bool = True  # Enable streaming by default
    RAG_MAX_CONTEXT_LENGTH: int = 4000  # Max context tokens

    # RAG Reranking Configuration (Cross-Encoder - Cole Medin Pattern)
    RAG_RERANKING_ENABLED: bool = True  # Enable cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
    RAG_RERANKING_RETRIEVAL_MULTIPLIER: int = 4  # Retrieve top_k × 4 facts, rerank to top_k
    # Expected: +10-15% retrieval precision with reranking
    # Performance: ~100ms for 20 facts on CPU
    # Cost: FREE (local inference, ~200MB RAM for model)

    # Qwen-Specific Configuration
    QWEN_TEMPERATURE: float = 0.7  # Optimal for RAG synthesis
    QWEN_TOP_P: float = 0.9  # Nucleus sampling
    QWEN_TOP_K: int = 40  # Top-k sampling
    QWEN_NUM_CTX: int = 4096  # Context window (supports up to 32k)

    # Neo4j Configuration
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "change_me_in_production"
    NEO4J_DATABASE: str = "neo4j"

    # Graphiti Configuration (Gemini 2.5 Flash-Lite - ARIA Pattern)
    GRAPHITI_ENABLED: bool = True
    GRAPHITI_LLM_MODEL: str = "gemini-2.5-flash-lite"  # Google Gemini 2.5 Flash-Lite (~$1-2/year!)
    GRAPHITI_LLM_TEMPERATURE: float = 0.0  # Deterministic for entity extraction
    GRAPHITI_ESTIMATED_TOKENS_PER_CHUNK: int = 3_000  # Conservative estimate
    GRAPHITI_SEMAPHORE_LIMIT: int = 10  # Concurrent LLM calls (4K RPM = safe)

    # File Storage
    UPLOAD_DIR: str = "/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,ppt,pptx,doc,docx"

    # Monitoring (Sentry)
    SENTRY_DSN_BACKEND: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    # Processing
    DOCLING_TIMEOUT: int = 900  # 15 minutes (allows for model download on first run)
    PROCESSING_WORKERS: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

