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
    
    # RAG Configuration
    RAG_TOP_K: int = 5  # Number of facts to retrieve from knowledge graph
    RAG_TEMPERATURE: float = 0.7  # Balanced creativity/factuality
    RAG_MAX_TOKENS: int = 2000  # Max response length
    RAG_STREAM: bool = True  # Enable streaming by default
    RAG_MAX_CONTEXT_LENGTH: int = 4000  # Max context tokens
    
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
    
    # Graphiti Configuration (Production-Ready v2.0.0)
    GRAPHITI_ENABLED: bool = True
    GRAPHITI_SAFE_QUEUE_ENABLED: bool = True  # Token-aware rate limiting
    GRAPHITI_RATE_LIMIT_TOKENS_PER_MIN: int = 4_000_000  # Anthropic limit
    GRAPHITI_SAFETY_BUFFER_PCT: float = 0.80  # 80% of limit (3.2M tokens/min)
    GRAPHITI_ESTIMATED_TOKENS_PER_CHUNK: int = 3_000  # Conservative estimate
    
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

