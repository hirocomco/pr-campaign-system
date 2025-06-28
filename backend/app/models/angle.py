"""
Angle model for storing specific campaign angles and story ideas.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Angle(Base):
    """
    Model for storing specific campaign angles and story ideas related to trends.
    """
    __tablename__ = "angles"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationships
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True, index=True)
    
    # Core angle information
    title = Column(String(500), nullable=False, index=True)
    hook = Column(String(1000), nullable=False)  # The compelling hook/headline
    story_angle = Column(Text, nullable=False)  # The narrative angle
    data_hook = Column(String(500), nullable=True)  # "73% increase in tourism bookings"
    
    # Content structure
    headline_options = Column(ARRAY(String), nullable=True, default=list)
    key_statistics = Column(ARRAY(String), nullable=True, default=list)
    supporting_quotes = Column(ARRAY(String), nullable=True, default=list)
    
    # Targeting and positioning
    angle_type = Column(String(100), nullable=False, index=True)  # "data-driven", "emotional", "newsjacking"
    target_publications = Column(ARRAY(String), nullable=True, default=list)
    journalist_contacts = Column(ARRAY(String), nullable=True, default=list)
    
    # Brand application
    brand_categories = Column(ARRAY(String), nullable=True, default=list)  # Which industries this works for
    brand_examples = Column(ARRAY(String), nullable=True, default=list)  # Example brands that could use this
    adaptation_notes = Column(Text, nullable=True)  # How to adapt for different brands
    
    # Execution details
    research_requirements = Column(ARRAY(String), nullable=True, default=list)
    content_requirements = Column(ARRAY(String), nullable=True, default=list)
    timeline_estimate = Column(String(50), nullable=True)  # "2-3 days", "1 week"
    
    # Scoring
    uniqueness_score = Column(Float, nullable=False, default=0.0)  # How unique/original the angle is
    newsworthiness_score = Column(Float, nullable=False, default=0.0)  # Media appeal
    brand_fit_score = Column(Float, nullable=False, default=0.0)  # How well it fits brands
    execution_ease = Column(Float, nullable=False, default=0.0)  # How easy to execute
    
    # Media potential
    media_formats = Column(ARRAY(String), nullable=True, default=list)  # ["press-release", "infographic", "video"]
    distribution_channels = Column(ARRAY(String), nullable=True, default=list)
    expected_reach = Column(String(50), nullable=True)  # "local", "national", "international"
    
    # Supporting materials
    reference_links = Column(ARRAY(String), nullable=True, default=list)
    source_data = Column(JSONB, nullable=True, default=dict)
    visual_concepts = Column(ARRAY(String), nullable=True, default=list)
    
    # AI generation details
    generation_prompt = Column(Text, nullable=True)
    generation_model = Column(String(50), nullable=True)
    generation_metadata = Column(JSONB, nullable=True, default=dict)
    
    # Quality and validation
    fact_checked = Column(Boolean, nullable=False, default=False)
    brand_safety_approved = Column(Boolean, nullable=False, default=False)
    originality_score = Column(Float, nullable=True)  # Plagiarism/similarity check
    
    # Usage and feedback
    usage_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=True)  # If tracked, conversion to actual campaigns
    user_rating = Column(Float, nullable=True)  # 1-5 star rating
    feedback_notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, approved, used, archived
    is_featured = Column(Boolean, nullable=False, default=False, index=True)
    is_template = Column(Boolean, nullable=False, default=False)  # Can be reused as template
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    validated_at = Column(DateTime, nullable=True)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    trend = relationship("Trend")
    campaign = relationship("Campaign")
    
    def __repr__(self) -> str:
        return f"<Angle(id={self.id}, title='{self.title}', type='{self.angle_type}')>"
    
    @property
    def overall_score(self) -> float:
        """Calculate overall angle score."""
        weights = {
            'uniqueness': 0.25,
            'newsworthiness': 0.30,
            'brand_fit': 0.25,
            'execution_ease': 0.20
        }
        
        return (
            self.uniqueness_score * weights['uniqueness'] +
            self.newsworthiness_score * weights['newsworthiness'] +
            self.brand_fit_score * weights['brand_fit'] +
            self.execution_ease * weights['execution_ease']
        )
    
    @property
    def is_ready_for_use(self) -> bool:
        """Check if angle is validated and ready for use."""
        return (
            self.fact_checked and
            self.brand_safety_approved and
            self.status == "approved"
        )
    
    @property
    def complexity_level(self) -> str:
        """Get complexity level based on execution ease."""
        if self.execution_ease >= 0.8:
            return "easy"
        elif self.execution_ease >= 0.5:
            return "medium"
        else:
            return "hard" 