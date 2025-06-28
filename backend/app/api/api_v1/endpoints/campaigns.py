"""
API endpoints for campaign management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_database
from app.models.campaign import Campaign
from app.models.trend import Trend

router = APIRouter()


@router.get("/")
async def get_campaigns(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    trend_id: Optional[UUID] = Query(None, description="Filter by trend ID"),
    campaign_type: Optional[str] = Query(None, description="Filter by campaign type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum potential score"),
    featured_only: bool = Query(False, description="Show only featured campaigns"),
    db: AsyncSession = Depends(get_database)
) -> List[dict]:
    """
    Get list of campaigns with optional filtering.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        trend_id: Filter campaigns by specific trend
        campaign_type: Filter by campaign type
        industry: Filter by industry
        min_score: Minimum potential score threshold
        featured_only: Only return featured campaigns
        db: Database session
        
    Returns:
        List of campaigns matching the criteria
    """
    query = select(Campaign).options(selectinload(Campaign.trend)).where(Campaign.status == "draft")
    
    # Apply filters
    if trend_id:
        query = query.where(Campaign.trend_id == trend_id)
    
    if campaign_type:
        query = query.where(Campaign.campaign_type == campaign_type)
    
    if industry:
        query = query.where(Campaign.industry == industry)
    
    if min_score is not None:
        query = query.where(Campaign.potential_score >= min_score)
    
    if featured_only:
        query = query.where(Campaign.is_featured == True)
    
    # Order by potential score descending
    query = query.order_by(desc(Campaign.potential_score)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    # Convert to dict for response
    return [
        {
            "id": campaign.id,
            "title": campaign.title,
            "headline": campaign.headline,
            "description": campaign.description,
            "brief": campaign.brief,
            "campaign_type": campaign.campaign_type,
            "industry": campaign.industry,
            "target_audience": campaign.target_audience,
            "execution_timeline": campaign.execution_timeline,
            "difficulty_level": campaign.difficulty_level,
            "potential_score": campaign.potential_score,
            "virality_score": campaign.virality_score,
            "brand_safety_score": campaign.brand_safety_score,
            "overall_score": campaign.overall_score,
            "suggested_channels": campaign.suggested_channels,
            "media_hooks": campaign.media_hooks,
            "key_messages": campaign.key_messages,
            "is_featured": campaign.is_featured,
            "created_at": campaign.created_at,
            "trend": {
                "id": campaign.trend.id,
                "title": campaign.trend.title,
                "category": campaign.trend.category,
                "score": campaign.trend.score,
                "sustainability_score": campaign.trend.sustainability_score
            } if campaign.trend else None
        }
        for campaign in campaigns
    ]


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_database)
) -> dict:
    """
    Get a specific campaign by ID.
    
    Args:
        campaign_id: UUID of the campaign to retrieve
        db: Database session
        
    Returns:
        Campaign object with trend information
        
    Raises:
        HTTPException: If campaign not found
    """
    query = select(Campaign).options(selectinload(Campaign.trend)).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return {
        "id": campaign.id,
        "trend_id": campaign.trend_id,
        "title": campaign.title,
        "headline": campaign.headline,
        "description": campaign.description,
        "brief": campaign.brief,
        "campaign_type": campaign.campaign_type,
        "industry": campaign.industry,
        "target_audience": campaign.target_audience,
        "execution_timeline": campaign.execution_timeline,
        "difficulty_level": campaign.difficulty_level,
        "required_resources": campaign.required_resources,
        "potential_score": campaign.potential_score,
        "virality_score": campaign.virality_score,
        "brand_safety_score": campaign.brand_safety_score,
        "execution_complexity": campaign.execution_complexity,
        "overall_score": campaign.overall_score,
        "content_pillars": campaign.content_pillars,
        "key_messages": campaign.key_messages,
        "call_to_action": campaign.call_to_action,
        "suggested_channels": campaign.suggested_channels,
        "media_hooks": campaign.media_hooks,
        "journalist_angles": campaign.journalist_angles,
        "data_points": campaign.data_points,
        "source_links": campaign.source_links,
        "brand_archetypes": campaign.brand_archetypes,
        "risk_factors": campaign.risk_factors,
        "brand_safety_notes": campaign.brand_safety_notes,
        "generation_model": campaign.generation_model,
        "status": campaign.status,
        "is_featured": campaign.is_featured,
        "is_evergreen": campaign.is_evergreen,
        "view_count": campaign.view_count,
        "download_count": campaign.download_count,
        "rating": campaign.rating,
        "created_at": campaign.created_at,
        "updated_at": campaign.updated_at,
        "trend": {
            "id": campaign.trend.id,
            "title": campaign.trend.title,
            "description": campaign.trend.description,
            "category": campaign.trend.category,
            "score": campaign.trend.score,
            "sustainability_score": campaign.trend.sustainability_score,
            "platforms": campaign.trend.platforms,
            "keywords": campaign.trend.keywords
        } if campaign.trend else None
    }


@router.post("/{campaign_id}/view")
async def increment_view_count(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_database)
) -> dict:
    """
    Increment the view count for a campaign.
    
    Args:
        campaign_id: UUID of the campaign
        db: Database session
        
    Returns:
        Updated view count
        
    Raises:
        HTTPException: If campaign not found
    """
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    campaign.view_count += 1
    await db.commit()
    
    return {"view_count": campaign.view_count}


@router.post("/{campaign_id}/download")
async def increment_download_count(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_database)
) -> dict:
    """
    Increment the download count for a campaign.
    
    Args:
        campaign_id: UUID of the campaign
        db: Database session
        
    Returns:
        Updated download count
        
    Raises:
        HTTPException: If campaign not found
    """
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    campaign.download_count += 1
    await db.commit()
    
    return {"download_count": campaign.download_count}


@router.get("/types/summary")
async def get_campaign_types_summary(
    db: AsyncSession = Depends(get_database)
) -> dict:
    """
    Get summary of campaign types and their counts.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with campaign type statistics
    """
    # Get count by campaign type
    type_query = select(
        Campaign.campaign_type,
        func.count(Campaign.id).label('count'),
        func.avg(Campaign.potential_score).label('avg_score')
    ).where(Campaign.status == "draft").group_by(Campaign.campaign_type)
    
    result = await db.execute(type_query)
    types_data = result.all()
    
    return {
        "campaign_types": [
            {
                "type": row.campaign_type,
                "count": row.count,
                "average_score": round(float(row.avg_score or 0), 2)
            }
            for row in types_data
        ]
    } 