"""
Daily trend analysis tasks.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog
from sqlalchemy import select, and_

from app.tasks.celery_app import celery_app, run_async_task
from app.core.database import get_db_session
from app.models.trend import Trend
from app.models.campaign import Campaign
from app.services.trend_detection.google_trends import GoogleTrendsService
from app.services.trend_detection.news_api import NewsAPIService
from app.services.trend_detection.reddit_service import RedditService
from app.services.angle_generation.ai_service import AIService

logger = structlog.get_logger()


@celery_app.task(bind=True, name="app.tasks.daily_analysis.analyze_daily_trends")
def analyze_daily_trends(self):
    """
    Main daily trend analysis task.
    Collects trends from all sources and processes them.
    """
    logger.info("Starting daily trend analysis")
    
    try:
        result = run_async_task(_analyze_daily_trends_async())
        logger.info("Daily trend analysis completed", result=result)
        return result
    except Exception as e:
        logger.error("Daily trend analysis failed", error=str(e))
        raise self.retry(countdown=60, max_retries=3)


async def _analyze_daily_trends_async() -> Dict[str, Any]:
    """
    Async implementation of daily trend analysis.
    
    Returns:
        Dictionary with analysis results
    """
    db = await get_db_session()
    
    try:
        # Initialize services
        google_service = GoogleTrendsService()
        news_service = NewsAPIService()
        reddit_service = RedditService()
        ai_service = AIService()
        
        # Collect trends from all sources
        all_trends = []
        
        # Google Trends
        try:
            google_trends = await google_service.get_trending_topics()
            all_trends.extend(google_trends)
            logger.info("Collected Google trends", count=len(google_trends))
        except Exception as e:
            logger.warning("Failed to collect Google trends", error=str(e))
        
        # News API
        try:
            news_trends = await news_service.get_trending_topics()
            all_trends.extend(news_trends)
            logger.info("Collected news trends", count=len(news_trends))
        except Exception as e:
            logger.warning("Failed to collect news trends", error=str(e))
        
        # Reddit
        try:
            reddit_trends = await reddit_service.get_trending_topics()
            all_trends.extend(reddit_trends)
            logger.info("Collected Reddit trends", count=len(reddit_trends))
        except Exception as e:
            logger.warning("Failed to collect Reddit trends", error=str(e))
        
        # Process and deduplicate trends
        processed_trends = await _process_and_deduplicate_trends(all_trends, db)
        
        # Score and filter trends
        scored_trends = await _score_and_filter_trends(processed_trends, ai_service, db)
        
        # Generate campaign angles for top trends
        campaigns_generated = await _generate_campaign_angles(scored_trends[:10], ai_service, db)
        
        await db.commit()
        
        return {
            "total_collected": len(all_trends),
            "processed_trends": len(processed_trends),
            "scored_trends": len(scored_trends),
            "campaigns_generated": campaigns_generated,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close()


async def _process_and_deduplicate_trends(
    raw_trends: List[Dict[str, Any]], 
    db
) -> List[Trend]:
    """
    Process raw trends and remove duplicates.
    
    Args:
        raw_trends: List of raw trend data
        db: Database session
        
    Returns:
        List of processed Trend objects
    """
    processed_trends = []
    
    for trend_data in raw_trends:
        # Check if trend already exists (by title similarity)
        existing_query = select(Trend).where(
            and_(
                Trend.title.ilike(f"%{trend_data['title'][:50]}%"),
                Trend.status == "active",
                Trend.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        result = await db.execute(existing_query)
        existing_trend = result.scalar_one_or_none()
        
        if existing_trend:
            # Update existing trend with new data
            existing_trend.volume += trend_data.get('volume', 0)
            existing_trend.platforms = list(set(existing_trend.platforms + trend_data.get('platforms', [])))
            existing_trend.updated_at = datetime.utcnow()
            processed_trends.append(existing_trend)
        else:
            # Create new trend
            trend = Trend(
                title=trend_data['title'],
                description=trend_data.get('description'),
                category=trend_data.get('category'),
                score=trend_data.get('score', 0.0),
                velocity=trend_data.get('velocity', 0.0),
                volume=trend_data.get('volume', 0),
                platforms=trend_data.get('platforms', []),
                keywords=trend_data.get('keywords', []),
                source_urls=trend_data.get('source_urls', []),
                metadata=trend_data.get('metadata', {}),
                first_seen_at=datetime.utcnow()
            )
            db.add(trend)
            processed_trends.append(trend)
    
    return processed_trends


async def _score_and_filter_trends(
    trends: List[Trend], 
    ai_service: AIService, 
    db
) -> List[Trend]:
    """
    Score trends and filter by sustainability.
    
    Args:
        trends: List of trends to score
        ai_service: AI service for analysis
        db: Database session
        
    Returns:
        List of filtered trends
    """
    scored_trends = []
    
    for trend in trends:
        try:
            # Calculate sustainability score using AI
            sustainability_analysis = await ai_service.analyze_trend_sustainability(trend)
            trend.sustainability_score = sustainability_analysis.get('score', 0.0)
            trend.analysis_data = sustainability_analysis
            
            # Brand safety check
            safety_check = await ai_service.check_brand_safety(trend)
            trend.is_brand_safe = safety_check.get('is_safe', True)
            
            # Only keep trends that meet minimum criteria
            if (trend.sustainability_score >= 0.3 and 
                trend.score >= 0.2 and
                trend.is_brand_safe):
                trend.is_analyzed = True
                trend.analyzed_at = datetime.utcnow()
                scored_trends.append(trend)
            else:
                trend.status = "archived"
                
        except Exception as e:
            logger.warning("Failed to score trend", trend_id=trend.id, error=str(e))
            trend.status = "archived"
    
    # Sort by combined score (trend score + sustainability)
    scored_trends.sort(
        key=lambda t: (t.score * 0.6 + t.sustainability_score * 0.4), 
        reverse=True
    )
    
    return scored_trends


async def _generate_campaign_angles(
    trends: List[Trend], 
    ai_service: AIService, 
    db
) -> int:
    """
    Generate campaign angles for top trends.
    
    Args:
        trends: List of top trends
        ai_service: AI service for generation
        db: Database session
        
    Returns:
        Number of campaigns generated
    """
    campaigns_generated = 0
    
    for trend in trends:
        try:
            # Generate campaign ideas
            campaign_ideas = await ai_service.generate_campaign_ideas(trend)
            
            for idea in campaign_ideas:
                campaign = Campaign(
                    trend_id=trend.id,
                    title=idea['title'],
                    headline=idea['headline'],
                    description=idea['description'],
                    brief=idea['brief'],
                    campaign_type=idea.get('type', 'trend-riding'),
                    industry=idea.get('industry'),
                    target_audience=idea.get('target_audience'),
                    execution_timeline=idea.get('timeline', '1-2 days'),
                    difficulty_level=idea.get('difficulty', 'medium'),
                    potential_score=idea.get('potential_score', 0.5),
                    virality_score=idea.get('virality_score', 0.5),
                    brand_safety_score=idea.get('brand_safety_score', 0.8),
                    execution_complexity=idea.get('complexity', 0.5),
                    suggested_channels=idea.get('channels', []),
                    key_messages=idea.get('key_messages', []),
                    media_hooks=idea.get('media_hooks', []),
                    generation_model=idea.get('model', 'gpt-4'),
                    generation_metadata=idea.get('metadata', {})
                )
                db.add(campaign)
                campaigns_generated += 1
                
        except Exception as e:
            logger.warning("Failed to generate campaigns for trend", trend_id=trend.id, error=str(e))
    
    return campaigns_generated


@celery_app.task(bind=True, name="app.tasks.daily_analysis.cleanup_old_trends")
def cleanup_old_trends(self):
    """
    Clean up old trends and campaigns.
    """
    logger.info("Starting cleanup of old trends")
    
    try:
        result = run_async_task(_cleanup_old_trends_async())
        logger.info("Cleanup completed", result=result)
        return result
    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
        raise


async def _cleanup_old_trends_async() -> Dict[str, int]:
    """
    Archive old trends and campaigns.
    
    Returns:
        Dictionary with cleanup statistics
    """
    db = await get_db_session()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Archive old trends
        old_trends_query = select(Trend).where(
            and_(
                Trend.created_at < cutoff_date,
                Trend.status == "active"
            )
        )
        result = await db.execute(old_trends_query)
        old_trends = result.scalars().all()
        
        trends_archived = 0
        for trend in old_trends:
            trend.status = "archived"
            trends_archived += 1
        
        # Archive old campaigns
        old_campaigns_query = select(Campaign).where(
            and_(
                Campaign.created_at < cutoff_date,
                Campaign.status == "draft"
            )
        )
        result = await db.execute(old_campaigns_query)
        old_campaigns = result.scalars().all()
        
        campaigns_archived = 0
        for campaign in old_campaigns:
            campaign.status = "archived"
            campaigns_archived += 1
        
        await db.commit()
        
        return {
            "trends_archived": trends_archived,
            "campaigns_archived": campaigns_archived
        }
        
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close() 