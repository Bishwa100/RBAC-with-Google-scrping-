"""
TopicLens Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional

class TopicLensSettings(BaseSettings):
    """TopicLens configuration settings"""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Ollama LLM Configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_max_tokens: int = 512
    
    # Database
    topiclens_db_url: str = "sqlite:///./topiclens.db"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Available sources
    available_sources: list = [
        "youtube", "github", "reddit", "twitter", "blogs",
        "linkedin", "facebook", "instagram", "quora", "events"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "TOPICLENS_"
        extra = "ignore"  # Allow extra env vars without validation errors

topiclens_settings = TopicLensSettings()
