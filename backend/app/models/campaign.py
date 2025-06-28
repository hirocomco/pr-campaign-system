"""
Campaign model for storing PR campaign ideas and their execution details.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Campaign(Base):
    """
    Model for storing PR campaign ideas generated from trends.
    """
    __tablename__ = "campaigns"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationship to trend
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False, index=True)
    
    # Core campaign information
    title = Column(String(500), nullable=False, index=True)
    headline = Column(String(1000), nullable=False)  # Main campaign headline
    description = Column(Text, nullable=False)
    brief = Column(Text, nullable=False)  # Detailed execution brief
    
    # Campaign categorization
    campaign_type = Column(String(100), nullable=False, index=True)  # "newsjacking", "trend-riding", "data-story"
    industry = Column(String(100), nullable=True, index=True)
    target_audience = Column(String(200), nullable=True)
    
    # Execution details
    execution_timeline = Column(String(50), nullable=False)  # "1-2 days", "1 week", "ongoing"
    difficulty_level = Column(String(20), nullable=False, default="medium")  # easy, medium, hard
    required_resources = Column(ARRAY(String), nullable=True, default=list)
    
    # Scoring and metrics
    potential_score = Column(Float, nullable=False, default=0.0, index=True)
    virality_score = Column(Float, nullable=False, default=0.0)
    brand_safety_score = Column(Float, nullable=False, default=0.0)
    execution_complexity = Column(Float, nullable=False, default=0.0)  # 0-1 scale
    
    # Content suggestions
    content_pillars = Column(ARRAY(String), nullable=True, default=list)
    key_messages = Column(ARRAY(String), nullable=True, default=list)
    call_to_action = Column(String(500), nullable=True)
    
    # Media and distribution
    suggested_channels = Column(ARRAY(String), nullable=True, default=list)  # ["twitter", "linkedin", "press"]
    media_hooks = Column(ARRAY(String), nullable=True, default=list)
    journalist_angles = Column(ARRAY(String), nullable=True, default=list)
    
    # Supporting data
    data_points = Column(JSONB, nullable=True, default=dict)  # Stats, figures, research
    source_links = Column(ARRAY(String), nullable=True, default=list)
    
    # Brand considerations
    brand_archetypes = Column(ARRAY(String), nullable=True, default=list)  # Which brand types this suits
    risk_factors = Column(ARRAY(String), nullable=True, default=list)
    brand_safety_notes = Column(Text, nullable=True)
    
    # AI generation metadata
    generation_model = Column(String(50), nullable=True)  # "gpt-4", "claude-3"
    generation_prompt = Column(Text, nullable=True)
    generation_metadata = Column(JSONB, nullable=True, default=dict)
    
    # Status and lifecycle
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, approved, used, archived
    is_featured = Column(Boolean, nullable=False, default=False, index=True)
    is_evergreen = Column(Boolean, nullable=False, default=False)  # Can be reused/adapted
    
    # Usage tracking
    view_count = Column(Integer, nullable=False, default=0)
    download_count = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=True)  # User rating 1-5
    feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    trend = relationship("Trend", back_populates="campaigns")
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, title='{self.title}', score={self.potential_score})>"
    
    @property
    def age_hours(self) -> Optional[float]:
        """Calculate age of campaign in hours."""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    @property
    def is_recent(self) -> bool:
        """Check if campaign was created in the last 24 hours."""
        return self.age_hours <= 24
    
    @property
    def overall_score(self) -> float:
        """Calculate overall campaign score combining multiple factors."""
        weights = {
            'potential': 0.4,
            'virality': 0.3,
            'brand_safety': 0.2,
            'complexity': 0.1  # Lower complexity = higher score
        }
        
        complexity_score = 1.0 - self.execution_complexity  # Invert complexity
        
        return (
            self.potential_score * weights['potential'] +
            self.virality_score * weights['virality'] +
            self.brand_safety_score * weights['brand_safety'] +
            complexity_score * weights['complexity']
        ) 