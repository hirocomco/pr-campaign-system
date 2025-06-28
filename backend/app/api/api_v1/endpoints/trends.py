"""
API endpoints for trend management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.api.deps import get_database
from app.models.trend import Trend
from app.schemas.trend import TrendCreate, TrendResponse, TrendUpdate

router = APIRouter()


@router.get("/", response_model=List[TrendResponse])
async def get_trends(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum trend score"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    sustainable_only: bool = Query(False, description="Show only sustainable trends"),
    db: AsyncSession = Depends(get_database)
) -> List[Trend]:
    """
    Get list of trends with optional filtering.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        category: Filter trends by category
        min_score: Minimum trend score threshold
        platform: Filter by specific platform
        sustainable_only: Only return trends with high sustainability scores
        db: Database session
        
    Returns:
        List of trends matching the criteria
    """
    query = select(Trend).where(Trend.status == "active")
    
    # Apply filters
    if category:
        query = query.where(Trend.category == category)
    
    if min_score is not None:
        query = query.where(Trend.score >= min_score)
    
    if platform:
        query = query.where(Trend.platforms.contains([platform]))
    
    if sustainable_only:
        query = query.where(Trend.sustainability_score >= 0.7)
    
    # Order by score descending
    query = query.order_by(desc(Trend.score)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    trends = result.scalars().all()
    
    return trends


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(
    trend_id: UUID,
    db: AsyncSession = Depends(get_database)
) -> Trend:
    """
    Get a specific trend by ID.
    
    Args:
        trend_id: UUID of the trend to retrieve
        db: Database session
        
    Returns:
        Trend object
        
    Raises:
        HTTPException: If trend not found
    """
    query = select(Trend).where(Trend.id == trend_id)
    result = await db.execute(query)
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trend not found"
        )
    
    return trend


@router.post("/", response_model=TrendResponse, status_code=status.HTTP_201_CREATED)
async def create_trend(
    trend_data: TrendCreate,
    db: AsyncSession = Depends(get_database)
) -> Trend:
    """
    Create a new trend.
    
    Args:
        trend_data: Trend creation data
        db: Database session
        
    Returns:
        Created trend object
    """
    trend = Trend(**trend_data.dict())
    db.add(trend)
    await db.commit()
    await db.refresh(trend)
    
    return trend


@router.put("/{trend_id}", response_model=TrendResponse)
async def update_trend(
    trend_id: UUID,
    trend_update: TrendUpdate,
    db: AsyncSession = Depends(get_database)
) -> Trend:
    """
    Update an existing trend.
    
    Args:
        trend_id: UUID of the trend to update
        trend_update: Trend update data
        db: Database session
        
    Returns:
        Updated trend object
        
    Raises:
        HTTPException: If trend not found
    """
    query = select(Trend).where(Trend.id == trend_id)
    result = await db.execute(query)
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trend not found"
        )
    
    # Update fields
    update_data = trend_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trend, field, value)
    
    await db.commit()
    await db.refresh(trend)
    
    return trend


@router.delete("/{trend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trend(
    trend_id: UUID,
    db: AsyncSession = Depends(get_database)
):
    """
    Delete a trend (soft delete by setting status to 'archived').
    
    Args:
        trend_id: UUID of the trend to delete
        db: Database session
        
    Raises:
        HTTPException: If trend not found
    """
    query = select(Trend).where(Trend.id == trend_id)
    result = await db.execute(query)
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trend not found"
        )
    
    trend.status = "archived"
    await db.commit()


@router.get("/stats/summary")
async def get_trends_summary(
    db: AsyncSession = Depends(get_database)
) -> dict:
    """
    Get summary statistics for trends.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with trend statistics
    """
    # Count trends by status
    active_count_query = select(func.count(Trend.id)).where(Trend.status == "active")
    total_count_query = select(func.count(Trend.id))
    
    active_count = await db.scalar(active_count_query)
    total_count = await db.scalar(total_count_query)
    
    # Get average scores
    avg_score_query = select(func.avg(Trend.score)).where(Trend.status == "active")
    avg_sustainability_query = select(func.avg(Trend.sustainability_score)).where(Trend.status == "active")
    
    avg_score = await db.scalar(avg_score_query) or 0
    avg_sustainability = await db.scalar(avg_sustainability_query) or 0
    
    return {
        "total_trends": total_count,
        "active_trends": active_count,
        "average_score": round(float(avg_score), 2),
        "average_sustainability": round(float(avg_sustainability), 2)
    } 