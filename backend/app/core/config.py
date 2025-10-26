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
    OLLAMA_MODEL: str = "llama3:8b"
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    # Neo4j Configuration
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "change_me_in_production"
    NEO4J_DATABASE: str = "neo4j"
    
    # Graphiti Configuration
    GRAPHITI_ENABLED: bool = True
    
    # File Storage
    UPLOAD_DIR: str = "/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,ppt,pptx,doc,docx"
    
    # Monitoring (Sentry)
    SENTRY_DSN_BACKEND: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    # Processing
    DOCKLING_TIMEOUT: int = 300  # 5 minutes
    PROCESSING_WORKERS: int = 2
    
    # RAG Configuration
    RAG_TOP_K: int = 5  # Number of context chunks to retrieve
    RAG_MAX_CONTEXT_LENGTH: int = 4000  # Max context tokens
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

