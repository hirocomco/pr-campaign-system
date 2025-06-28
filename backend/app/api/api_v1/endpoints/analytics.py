"""
API endpoints for analytics and system metrics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.api.deps import get_database
from app.models.trend import Trend
from app.models.campaign import Campaign

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days to include in metrics"),
    db: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get dashboard metrics for the specified time period.
    
    Args:
        days: Number of days to include in metrics
        db: Database session
        
    Returns:
        Dictionary with dashboard metrics
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Trend metrics
    total_trends_query = select(func.count(Trend.id)).where(Trend.created_at >= cutoff_date)
    active_trends_query = select(func.count(Trend.id)).where(
        and_(Trend.created_at >= cutoff_date, Trend.status == "active")
    )
    avg_trend_score_query = select(func.avg(Trend.score)).where(
        and_(Trend.created_at >= cutoff_date, Trend.status == "active")
    )
    
    total_trends = await db.scalar(total_trends_query) or 0
    active_trends = await db.scalar(active_trends_query) or 0
    avg_trend_score = await db.scalar(avg_trend_score_query) or 0
    
    # Campaign metrics
    total_campaigns_query = select(func.count(Campaign.id)).where(Campaign.created_at >= cutoff_date)
    featured_campaigns_query = select(func.count(Campaign.id)).where(
        and_(Campaign.created_at >= cutoff_date, Campaign.is_featured == True)
    )
    avg_campaign_score_query = select(func.avg(Campaign.potential_score)).where(
        Campaign.created_at >= cutoff_date
    )
    
    total_campaigns = await db.scalar(total_campaigns_query) or 0
    featured_campaigns = await db.scalar(featured_campaigns_query) or 0
    avg_campaign_score = await db.scalar(avg_campaign_score_query) or 0
    
    # Top performing trends
    top_trends_query = select(Trend).where(
        and_(Trend.created_at >= cutoff_date, Trend.status == "active")
    ).order_by(desc(Trend.score)).limit(5)
    
    result = await db.execute(top_trends_query)
    top_trends = result.scalars().all()
    
    # Recent campaigns
    recent_campaigns_query = select(Campaign).where(
        Campaign.created_at >= cutoff_date
    ).order_by(desc(Campaign.created_at)).limit(5)
    
    result = await db.execute(recent_campaigns_query)
    recent_campaigns = result.scalars().all()
    
    return {
        "period_days": days,
        "trends": {
            "total": total_trends,
            "active": active_trends,
            "average_score": round(float(avg_trend_score), 2),
            "top_trends": [
                {
                    "id": trend.id,
                    "title": trend.title,
                    "score": trend.score,
                    "category": trend.category,
                    "platforms": trend.platforms
                }
                for trend in top_trends
            ]
        },
        "campaigns": {
            "total": total_campaigns,
            "featured": featured_campaigns,
            "average_score": round(float(avg_campaign_score), 2),
            "recent_campaigns": [
                {
                    "id": campaign.id,
                    "title": campaign.title,
                    "campaign_type": campaign.campaign_type,
                    "potential_score": campaign.potential_score,
                    "created_at": campaign.created_at
                }
                for campaign in recent_campaigns
            ]
        }
    }


@router.get("/trends/performance")
async def get_trends_performance(
    days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    db: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get trend performance analytics.
    
    Args:
        days: Number of days to analyze
        db: Database session
        
    Returns:
        Dictionary with trend performance data
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Trends by category
    category_query = select(
        Trend.category,
        func.count(Trend.id).label('count'),
        func.avg(Trend.score).label('avg_score'),
        func.avg(Trend.sustainability_score).label('avg_sustainability')
    ).where(
        and_(Trend.created_at >= cutoff_date, Trend.category.isnot(None))
    ).group_by(Trend.category).order_by(desc('count'))
    
    result = await db.execute(category_query)
    categories_data = result.all()
    
    # Trends by platform
    platform_query = select(Trend).where(Trend.created_at >= cutoff_date)
    result = await db.execute(platform_query)
    trends = result.scalars().all()
    
    platform_counts = {}
    for trend in trends:
        for platform in trend.platforms:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Score distribution
    score_ranges = {
        "0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0
    }
    
    for trend in trends:
        if trend.score < 0.2:
            score_ranges["0.0-0.2"] += 1
        elif trend.score < 0.4:
            score_ranges["0.2-0.4"] += 1
        elif trend.score < 0.6:
            score_ranges["0.4-0.6"] += 1
        elif trend.score < 0.8:
            score_ranges["0.6-0.8"] += 1
        else:
            score_ranges["0.8-1.0"] += 1
    
    return {
        "period_days": days,
        "categories": [
            {
                "category": row.category,
                "count": row.count,
                "average_score": round(float(row.avg_score or 0), 2),
                "average_sustainability": round(float(row.avg_sustainability or 0), 2)
            }
            for row in categories_data
        ],
        "platforms": [
            {"platform": platform, "count": count}
            for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "score_distribution": score_ranges
    }


@router.get("/campaigns/performance")
async def get_campaigns_performance(
    days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    db: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get campaign performance analytics.
    
    Args:
        days: Number of days to analyze
        db: Database session
        
    Returns:
        Dictionary with campaign performance data
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Campaigns by type
    type_query = select(
        Campaign.campaign_type,
        func.count(Campaign.id).label('count'),
        func.avg(Campaign.potential_score).label('avg_potential'),
        func.avg(Campaign.virality_score).label('avg_virality'),
        func.avg(Campaign.brand_safety_score).label('avg_safety')
    ).where(
        Campaign.created_at >= cutoff_date
    ).group_by(Campaign.campaign_type).order_by(desc('count'))
    
    result = await db.execute(type_query)
    types_data = result.all()
    
    # Campaigns by industry
    industry_query = select(
        Campaign.industry,
        func.count(Campaign.id).label('count'),
        func.avg(Campaign.potential_score).label('avg_score')
    ).where(
        and_(Campaign.created_at >= cutoff_date, Campaign.industry.isnot(None))
    ).group_by(Campaign.industry).order_by(desc('count'))
    
    result = await db.execute(industry_query)
    industries_data = result.all()
    
    # Engagement metrics
    engagement_query = select(
        func.sum(Campaign.view_count).label('total_views'),
        func.sum(Campaign.download_count).label('total_downloads'),
        func.avg(Campaign.rating).label('avg_rating'),
        func.count(Campaign.id).label('total_campaigns')
    ).where(Campaign.created_at >= cutoff_date)
    
    result = await db.execute(engagement_query)
    engagement_data = result.first()
    
    return {
        "period_days": days,
        "campaign_types": [
            {
                "type": row.campaign_type,
                "count": row.count,
                "average_potential": round(float(row.avg_potential or 0), 2),
                "average_virality": round(float(row.avg_virality or 0), 2),
                "average_safety": round(float(row.avg_safety or 0), 2)
            }
            for row in types_data
        ],
        "industries": [
            {
                "industry": row.industry,
                "count": row.count,
                "average_score": round(float(row.avg_score or 0), 2)
            }
            for row in industries_data
        ],
        "engagement": {
            "total_views": engagement_data.total_views or 0,
            "total_downloads": engagement_data.total_downloads or 0,
            "average_rating": round(float(engagement_data.avg_rating or 0), 2),
            "total_campaigns": engagement_data.total_campaigns or 0
        }
    }


@router.get("/system/health")
async def get_system_health(
    db: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get system health metrics.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with system health information
    """
    # Check database connectivity and recent activity
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    # Recent trends and campaigns
    recent_trends_query = select(func.count(Trend.id)).where(Trend.created_at >= last_24h)
    recent_campaigns_query = select(func.count(Campaign.id)).where(Campaign.created_at >= last_24h)
    
    recent_trends = await db.scalar(recent_trends_query) or 0
    recent_campaigns = await db.scalar(recent_campaigns_query) or 0
    
    # Unanalyzed trends
    unanalyzed_query = select(func.count(Trend.id)).where(
        and_(Trend.is_analyzed == False, Trend.status == "active")
    )
    unanalyzed_trends = await db.scalar(unanalyzed_query) or 0
    
    return {
        "timestamp": now.isoformat(),
        "database": {
            "status": "healthy",
            "recent_activity": {
                "trends_last_24h": recent_trends,
                "campaigns_last_24h": recent_campaigns
            }
        },
        "processing": {
            "unanalyzed_trends": unanalyzed_trends
        },
        "status": "healthy" if unanalyzed_trends < 100 else "warning"
    } 