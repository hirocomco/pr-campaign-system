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
    REDDIT_SUBREDDITS: List[str] = ["all", "news", "worldnews", "technology", "entertainment", "business", "science"]
    REDDIT_POSTS_PER_SUBREDDIT: int = 5
    REDDIT_TRENDING_ALGORITHM: str = "hot"  # hot, top, rising, new
    
    # Content Categorization Configuration
    AI_CATEGORIZATION_ENABLED: bool = True
    FALLBACK_TO_KEYWORD_FILTER: bool = True  # Fallback if AI categorization fails
    
    # AI Categorization Settings
    AI_CATEGORIZATION_MIN_CONFIDENCE: float = 0.7  # Minimum confidence for AI decisions
    AI_CATEGORIZATION_TIMEOUT: int = 30  # Seconds to wait for AI response
    ALLOW_CAUTION_CONTENT: bool = True  # Allow content marked as CAUTION level
    
    # AI Categorization Prompts
    AI_CATEGORIZATION_SYSTEM_PROMPT: str = "You are an expert content safety analyst for brand marketing. Analyze content and respond with valid JSON only."
    
    AI_CATEGORIZATION_USER_PROMPT_TEMPLATE: str = """
Analyze this Reddit content for brand safety and categorization:

CONTENT TO ANALYZE:
Title: {title}
Description: {description}
Subreddit: r/{subreddit}
Metadata: {metadata_signals}

CATEGORIZATION TASK:
Categorize this content for brand safety with these levels:
- SAFE: Brand-safe, suitable for PR campaigns (technology, science, entertainment, lifestyle)
- CAUTION: Potentially sensitive but not necessarily unsafe (health topics, minor controversies)  
- POLITICAL: Political content that brands should avoid
- VIOLENT: Violence, crime, war content
- CONTROVERSIAL: Highly divisive topics
- NSFW: Adult/inappropriate content

ANALYSIS CRITERIA:
1. Context and nuance matter - look beyond keywords
2. Consider if a major brand would associate with this content
3. Assess potential for backlash or controversy
4. Science, technology, entertainment are typically safe
5. News can be safe unless political/violent
6. Personal stories and advice are often safe

REQUIRED RESPONSE FORMAT (JSON):
{{
    "safety_level": "SAFE|CAUTION|POLITICAL|VIOLENT|CONTROVERSIAL|NSFW",
    "confidence": 0.85,
    "primary_category": "technology|science|entertainment|news|lifestyle|politics|violence|controversy",
    "secondary_categories": ["specific", "subcategories"],
    "reasoning": "Brief explanation of the categorization decision",
    "pr_suitability": "Brief assessment of PR campaign suitability"
}}

Respond only with valid JSON.
"""
    
    # Blocked Subreddits and Content (configurable lists)
    BLOCKED_SUBREDDITS: List[str] = [
        "politics", "worldpolitics", "conservative", "liberal", 
        "the_donald", "sandersforpresident", "politicalhumor",
        "combatfootage", "ukraine", "russia", "war", "syriancivilwar",
        "watchpeopledie", "gore", "nsfw", "nsfw_gifs"
    ]
    
    BLOCKED_FLAIRS: List[str] = [
        "nsfw", "politics", "violence", "gore", "war", "breaking news"
    ]
    
    # Legacy Content Filtering (fallback only)
    CONTENT_FILTER_ENABLED: bool = False  # Deprecated in favor of AI categorization
    CONTENT_FILTER_WAR_KEYWORDS: List[str] = [
        "war", "battle", "conflict", "invasion", "bombing", "attack", "military", "combat",
        "weapon", "soldier", "army", "navy", "airforce", "missile", "bomb", "drone", "strike",
        "siege", "battlefield", "casualties", "killed", "dead", "wounded", "fatalities"
    ]
    CONTENT_FILTER_POLITICS_KEYWORDS: List[str] = [
        "election", "vote", "candidate", "republican", "democrat", "congress",
        "senate", "president", "minister", "parliament", "political", "politician",
        "debate", "policy", "legislation", "government", "administration", "conservative",
        "liberal", "progressive", "ballot", "primary", "poll", "voter"
    ]
    CONTENT_FILTER_VIOLENCE_KEYWORDS: List[str] = [
        "murder", "kill", "death", "shot", "shooting", "stabbed", "assault", "violence",
        "fight", "brawl", "riot", "protest", "clash", "terror", "terrorist", "explosion",
        "victim", "crime", "criminal", "gang", "drugs", "arrest", "police", "shooting",
        "hate", "racism", "discrimination", "abuse", "harassment", "threat"
    ]
    
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
    
    @field_validator("REDDIT_SUBREDDITS", mode="before")
    @classmethod
    def assemble_reddit_subreddits(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["all", "news", "worldnews", "technology", "entertainment"]
    
    @field_validator("CONTENT_FILTER_WAR_KEYWORDS", mode="before")
    @classmethod
    def assemble_war_keywords(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [kw.lower() for kw in v]
        return []
    
    @field_validator("CONTENT_FILTER_POLITICS_KEYWORDS", mode="before")
    @classmethod
    def assemble_politics_keywords(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [kw.lower() for kw in v]
        return []
    
    @field_validator("CONTENT_FILTER_VIOLENCE_KEYWORDS", mode="before")
    @classmethod
    def assemble_violence_keywords(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [kw.lower() for kw in v]
        return []
    
    @field_validator("BLOCKED_SUBREDDITS", mode="before")
    @classmethod
    def assemble_blocked_subreddits(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [s.lower() for s in v]
        return []
    
    @field_validator("BLOCKED_FLAIRS", mode="before")
    @classmethod
    def assemble_blocked_flairs(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [s.lower() for s in v]
        return []
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings() 