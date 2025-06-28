"""Pydantic schemas for campaign data validation and serialization."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class CampaignType(str, Enum):
    """Campaign types for classification."""
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    SEASONAL = "seasonal"
    NEWS_JACKING = "news_jacking"
    THOUGHT_LEADERSHIP = "thought_leadership"

class CampaignStatus(str, Enum):
    """Campaign execution status."""
    DRAFT = "draft"
    READY = "ready"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class DifficultyLevel(str, Enum):
    """Campaign execution difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class CampaignAngleBase(BaseModel):
    """Base schema for campaign angles."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=1000)
    target_audience: str = Field(..., min_length=5, max_length=200)
    key_message: str = Field(..., min_length=10, max_length=500)
    supporting_data: Optional[str] = Field(None, max_length=2000)
    
class CampaignAngleCreate(CampaignAngleBase):
    """Schema for creating campaign angles."""
    pass

class CampaignAngleUpdate(BaseModel):
    """Schema for updating campaign angles."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=1000)
    target_audience: Optional[str] = Field(None, min_length=5, max_length=200)
    key_message: Optional[str] = Field(None, min_length=10, max_length=500)
    supporting_data: Optional[str] = Field(None, max_length=2000)

class CampaignAngle(CampaignAngleBase):
    """Schema for campaign angle responses."""
    id: str
    campaign_id: str
    quality_score: float = Field(..., ge=0, le=100)
    estimated_reach: int = Field(..., ge=0)
    effort_required: DifficultyLevel
    timeline_days: int = Field(..., ge=1, le=365)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExecutionRequirements(BaseModel):
    """Campaign execution requirements."""
    budget_range: str = Field(..., min_length=5, max_length=100)
    team_size: int = Field(..., ge=1, le=20)
    skills_required: List[str] = Field(..., min_items=1, max_items=10)
    tools_needed: List[str] = Field(default_factory=list, max_items=10)
    timeline_weeks: int = Field(..., ge=1, le=52)

class BrandConsiderations(BaseModel):
    """Brand safety and alignment considerations."""
    brand_safety_score: float = Field(..., ge=0, le=100)
    risk_factors: List[str] = Field(default_factory=list, max_items=10)
    alignment_score: float = Field(..., ge=0, le=100)
    content_guidelines: List[str] = Field(default_factory=list, max_items=20)

class CampaignBase(BaseModel):
    """Base campaign schema."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    campaign_type: CampaignType
    target_industries: List[str] = Field(..., min_items=1, max_items=10)
    estimated_reach: int = Field(..., ge=0)
    execution_difficulty: DifficultyLevel
    execution_requirements: ExecutionRequirements
    brand_considerations: BrandConsiderations
    content_suggestions: List[str] = Field(default_factory=list, max_items=20)
    
    @validator('target_industries')
    def validate_industries(cls, v):
        if not v:
            raise ValueError('At least one target industry must be specified')
        return v

class CampaignCreate(CampaignBase):
    """Schema for creating campaigns."""
    trend_id: str = Field(..., min_length=1)

class CampaignUpdate(BaseModel):
    """Schema for updating campaigns."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    campaign_type: Optional[CampaignType] = None
    target_industries: Optional[List[str]] = Field(None, min_items=1, max_items=10)
    estimated_reach: Optional[int] = Field(None, ge=0)
    execution_difficulty: Optional[DifficultyLevel] = None
    content_suggestions: Optional[List[str]] = Field(None, max_items=20)
    status: Optional[CampaignStatus] = None

class Campaign(CampaignBase):
    """Schema for campaign responses."""
    id: str
    trend_id: str
    status: CampaignStatus
    viral_potential_score: float = Field(..., ge=0, le=100)
    timeliness_score: float = Field(..., ge=0, le=100)
    originality_score: float = Field(..., ge=0, le=100)
    feasibility_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    angles: List[CampaignAngle] = Field(default_factory=list)
    views_count: int = Field(default=0, ge=0)
    downloads_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CampaignSummary(BaseModel):
    """Lightweight campaign summary for lists."""
    id: str
    title: str
    campaign_type: CampaignType
    status: CampaignStatus
    overall_score: float
    estimated_reach: int
    execution_difficulty: DifficultyLevel
    angles_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    """Response schema for campaign lists with pagination."""
    campaigns: List[CampaignSummary]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool

class CampaignStats(BaseModel):
    """Campaign statistics."""
    total_campaigns: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_difficulty: Dict[str, int]
    average_score: float
    top_performing: List[CampaignSummary] 