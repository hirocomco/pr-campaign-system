"""
Trend model for storing and tracking trending topics.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Trend(Base):
    """
    Model for storing trending topics with their metadata and analysis.
    """
    __tablename__ = "trends"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core trend information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Scoring and analysis
    score = Column(Float, nullable=False, default=0.0, index=True)
    velocity = Column(Float, nullable=False, default=0.0)  # Rate of growth
    volume = Column(Integer, nullable=False, default=0)  # Total mentions/searches
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    sustainability_score = Column(Float, nullable=False, default=0.0, index=True)
    
    # Source information
    platforms = Column(ARRAY(String), nullable=False, default=list)  # ["twitter", "google", "reddit"]
    source_urls = Column(ARRAY(String), nullable=True, default=list)
    keywords = Column(ARRAY(String), nullable=True, default=list)
    
    # Metadata and analysis results
    trend_metadata = Column(JSONB, nullable=True, default=dict)  # Flexible storage for additional data
    analysis_data = Column(JSONB, nullable=True, default=dict)  # AI analysis results
    
    # Geographic data
    regions = Column(ARRAY(String), nullable=True, default=list)  # ["US", "UK", "CA"]
    
    # Status and lifecycle
    status = Column(String(50), nullable=False, default="active", index=True)  # active, archived, expired
    is_analyzed = Column(Boolean, nullable=False, default=False, index=True)
    is_brand_safe = Column(Boolean, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    analyzed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # When trend is expected to fade
    
    # Tracking data
    first_seen_at = Column(DateTime, nullable=True)
    peak_score = Column(Float, nullable=True)
    peak_score_at = Column(DateTime, nullable=True)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="trend")
    
    def __repr__(self) -> str:
        return f"<Trend(id={self.id}, title='{self.title}', score={self.score})>"
    
    @property
    def age_hours(self) -> Optional[float]:
        """Calculate age of trend in hours."""
        if not self.first_seen_at:
            return None
        return (datetime.utcnow() - self.first_seen_at).total_seconds() / 3600
    
    @property
    def is_rising(self) -> bool:
        """Check if trend is currently rising in popularity."""
        return self.velocity > 0
    
    @property
    def is_sustainable(self) -> bool:
        """Check if trend has sufficient sustainability for campaign development."""
        return self.sustainability_score >= 0.7 