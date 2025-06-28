"""
Configuration settings for the PR Campaign Ideation System.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pr_campaign_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # AI/ML APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # External Data Sources
    NEWS_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "pr-campaign-system/1.0"
    
    # Security
    VALID_API_KEYS: List[str] = []
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    DIGEST_RECIPIENTS: List[str] = []
    
    # Frontend Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Trend Analysis Configuration
    MIN_TREND_SCORE: float = 0.3
    MAX_TRENDS_PER_DAY: int = 50
    TREND_ANALYSIS_SCHEDULE: str = "0 6 * * *"  # Every day at 6 AM
    
    # Campaign Generation Configuration
    MAX_ANGLES_PER_TREND: int = 5
    MIN_SUSTAINABILITY_SCORE: float = 0.7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 3600
    TREND_CACHE_TTL_SECONDS: int = 86400
    
    # AI Model Configuration
    DEFAULT_AI_PROVIDER: str = "openrouter"  # openai, anthropic, or openrouter
    DEFAULT_AI_MODEL: str = "anthropic/claude-3.5-sonnet"  # OpenRouter model format
    BACKUP_AI_MODEL: str = "openai/gpt-4"  # Fallback model
    OPENAI_MODEL: str = "gpt-4"  # For direct OpenAI usage
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"  # For direct Anthropic usage
    MAX_TOKENS_PER_REQUEST: int = 2000
    AI_TEMPERATURE: float = 0.7
    
    # Data Collection Settings
    MAX_TRENDS_PER_SOURCE: int = 50
    TREND_ANALYSIS_BATCH_SIZE: int = 10
    
    # Campaign Generation Settings
    MAX_CAMPAIGNS_PER_TREND: int = 5
    MIN_CAMPAIGN_SCORE: float = 60.0
    CAMPAIGN_GENERATION_TIMEOUT: int = 120
    
    # Environment Info
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    @field_validator("VALID_API_KEYS", mode="before")
    @classmethod
    def assemble_api_keys(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []
    
    @field_validator("DIGEST_RECIPIENTS", mode="before")
    @classmethod
    def assemble_digest_recipients(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings() 