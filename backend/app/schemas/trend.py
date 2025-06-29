"""
Pydantic schemas for Trend model.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TrendBase(BaseModel):
    """Base trend schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Trend title")
    description: Optional[str] = Field(None, description="Trend description")
    category: Optional[str] = Field(None, max_length=100, description="Trend category")
    platforms: List[str] = Field(default_factory=list, description="Source platforms")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Related keywords")
    regions: Optional[List[str]] = Field(default_factory=list, description="Geographic regions")


class TrendCreate(TrendBase):
    """Schema for creating a new trend."""
    score: float = Field(0.0, ge=0.0, le=1.0, description="Trend score")
    velocity: float = Field(0.0, description="Trend velocity/growth rate")
    volume: int = Field(0, ge=0, description="Total mentions/searches")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score")
    sustainability_score: float = Field(0.0, ge=0.0, le=1.0, description="Sustainability score")
    source_urls: Optional[List[str]] = Field(default_factory=list, description="Source URLs")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platform names."""
        valid_platforms = ['twitter', 'reddit', 'google', 'news', 'tiktok', 'instagram', 'youtube']
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return [p.lower() for p in v]


class TrendUpdate(BaseModel):
    """Schema for updating an existing trend."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    score: Optional[float] = Field(None, ge=0.0, le=1.0)
    velocity: Optional[float] = None
    volume: Optional[int] = Field(None, ge=0)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    sustainability_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    platforms: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    source_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    analysis_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|expired)$")
    is_analyzed: Optional[bool] = None
    is_brand_safe: Optional[bool] = None


class TrendResponse(TrendBase):
    """Schema for trend responses."""
    id: UUID
    score: float
    velocity: float
    volume: int
    sentiment_score: Optional[float]
    sustainability_score: float
    source_urls: List[str]
    metadata: Dict[str, Any] = Field(alias="trend_metadata")
    analysis_data: Dict[str, Any]
    status: str
    is_analyzed: bool
    is_brand_safe: Optional[bool]
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime]
    expires_at: Optional[datetime]
    first_seen_at: Optional[datetime]
    peak_score: Optional[float]
    peak_score_at: Optional[datetime]
    
    # Computed properties
    age_hours: Optional[float] = None
    is_rising: bool = False
    is_sustainable: bool = False
    
    class Config:
        from_attributes = True
        
    @validator('age_hours', pre=True, always=True)
    def calculate_age_hours(cls, v, values):
        """Calculate age in hours."""
        if 'first_seen_at' in values and values['first_seen_at']:
            return (datetime.utcnow() - values['first_seen_at']).total_seconds() / 3600
        return None
    
    @validator('is_rising', pre=True, always=True)
    def calculate_is_rising(cls, v, values):
        """Check if trend is rising."""
        return values.get('velocity', 0) > 0
    
    @validator('is_sustainable', pre=True, always=True)
    def calculate_is_sustainable(cls, v, values):
        """Check if trend is sustainable."""
        return values.get('sustainability_score', 0) >= 0.7


class TrendSummary(BaseModel):
    """Schema for trend summary statistics."""
    total_trends: int
    active_trends: int
    average_score: float
    average_sustainability: float
    top_categories: List[Dict[str, Any]] = Field(default_factory=list)
    trending_platforms: List[Dict[str, Any]] = Field(default_factory=list) 