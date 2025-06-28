"""Advanced trend scoring and analysis tasks."""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .celery_app import celery_app
from ..core.database import get_db_session
from ..models.trend import Trend
from ..services.data_enrichment.enrichment_service import DataEnrichmentService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def advanced_trend_scoring(self, trend_ids: List[str] = None):
    """
    Perform advanced scoring analysis on trends.
    
    Args:
        trend_ids: Optional list of specific trend IDs to score
    """
    try:
        return asyncio.run(_run_advanced_scoring(trend_ids))
    except Exception as exc:
        logger.error(f"Advanced trend scoring failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

async def _run_advanced_scoring(trend_ids: List[str] = None) -> Dict[str, Any]:
    """
    Run advanced trend scoring analysis.
    
    Args:
        trend_ids: Optional list of specific trend IDs to score
        
    Returns:
        Analysis results
    """
    try:
        async with get_db_session() as session:
            # Get trends to analyze
            if trend_ids:
                query = select(Trend).where(Trend.id.in_(trend_ids))
            else:
                # Score trends from last 24 hours that haven't been scored recently
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                query = select(Trend).where(
                    Trend.created_at >= cutoff_time,
                    Trend.sustainability_score.is_(None) | 
                    (Trend.updated_at < datetime.utcnow() - timedelta(hours=6))
                )
            
            result = await session.execute(query)
            trends = result.scalars().all()
            
            if not trends:
                logger.info("No trends found for advanced scoring")
                return {"processed": 0, "status": "no_trends"}
            
            # Initialize enrichment service
            enrichment_service = DataEnrichmentService(session)
            
            # Process trends in batches
            batch_size = 10
            processed_count = 0
            
            for i in range(0, len(trends), batch_size):
                batch = trends[i:i + batch_size]
                
                # Calculate advanced scores for batch
                scored_trends = await _calculate_advanced_scores(batch, enrichment_service)
                
                # Update trends in database
                for trend in scored_trends:
                    await session.merge(trend)
                
                processed_count += len(scored_trends)
                
                # Commit batch
                await session.commit()
                
                logger.info(f"Processed batch {i//batch_size + 1}: {len(scored_trends)} trends")
            
            return {
                "processed": processed_count,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in advanced trend scoring: {e}")
        raise

async def _calculate_advanced_scores(
    trends: List[Trend], enrichment_service: DataEnrichmentService
) -> List[Trend]:
    """
    Calculate advanced scores for a batch of trends.
    
    Args:
        trends: List of trends to score
        enrichment_service: Data enrichment service instance
        
    Returns:
        List of trends with updated scores
    """
    scored_trends = []
    
    for trend in trends:
        try:
            # Enrich trend with additional data
            enriched_trend = await enrichment_service.enrich_trend(trend)
            
            # Calculate PR potential score
            pr_score = await _calculate_pr_potential(enriched_trend)
            enriched_trend.pr_potential_score = pr_score
            
            # Calculate virality potential
            viral_score = await _calculate_virality_potential(enriched_trend)
            enriched_trend.viral_potential_score = viral_score
            
            # Calculate brand safety score
            safety_score = await _calculate_brand_safety_score(enriched_trend)
            enriched_trend.brand_safety_score = safety_score
            
            # Update overall score based on all factors
            enriched_trend.score = await _calculate_overall_score(enriched_trend)
            
            # Update timestamp
            enriched_trend.updated_at = datetime.utcnow()
            
            scored_trends.append(enriched_trend)
            
        except Exception as e:
            logger.error(f"Error scoring trend {trend.id}: {e}")
            # Keep original trend if scoring fails
            scored_trends.append(trend)
    
    return scored_trends

async def _calculate_pr_potential(trend: Trend) -> float:
    """
    Calculate PR potential score for a trend.
    
    Args:
        trend: Trend object with enriched data
        
    Returns:
        PR potential score (0-100)
    """
    try:
        score = 0.0
        metadata = trend.trend_metadata or {}
        
        # News coverage factor (30% weight)
        news_articles = metadata.get("related_news", [])
        news_score = min(30, len(news_articles) * 3)
        score += news_score
        
        # Search volume trends (25% weight)
        search_data = metadata.get("search_volume", {})
        volume_change = search_data.get("volume_change_7d", 0)
        if volume_change > 50:
            score += 25
        elif volume_change > 20:
            score += 20
        elif volume_change > 0:
            score += 15
        
        # Sentiment analysis (20% weight)
        sentiment_data = metadata.get("sentiment_analysis", {})
        sentiment_score = sentiment_data.get("sentiment_score", 0)
        positive_percentage = sentiment_data.get("sentiment_distribution", {}).get("positive", 50)
        score += (positive_percentage / 100) * 20
        
        # Geographic reach (15% weight)
        geo_data = metadata.get("geographic_distribution", {})
        countries_count = len(geo_data.get("top_countries", []))
        score += min(15, countries_count * 3)
        
        # Competition analysis (10% weight)
        competition_data = metadata.get("competition_analysis", {})
        opportunity_score = competition_data.get("opportunity_score", 50)
        score += (opportunity_score / 100) * 10
        
        return min(100.0, max(0.0, score))
        
    except Exception as e:
        logger.error(f"Error calculating PR potential: {e}")
        return 50.0

async def _calculate_virality_potential(trend: Trend) -> float:
    """
    Calculate virality potential score for a trend.
    
    Args:
        trend: Trend object with enriched data
        
    Returns:
        Virality potential score (0-100)
    """
    try:
        score = 0.0
        metadata = trend.trend_metadata or {}
        
        # Engagement velocity (40% weight)
        search_data = metadata.get("search_volume", {})
        volume_change_24h = search_data.get("volume_change_24h", 0)
        if volume_change_24h > 100:
            score += 40
        elif volume_change_24h > 50:
            score += 30
        elif volume_change_24h > 20:
            score += 20
        elif volume_change_24h > 0:
            score += 10
        
        # Demographic spread (25% weight)
        demo_data = metadata.get("demographics", {})
        age_groups = demo_data.get("age_groups", {})
        if len(age_groups) >= 4:  # Multiple age groups engaged
            score += 25
        elif len(age_groups) >= 3:
            score += 20
        elif len(age_groups) >= 2:
            score += 15
        
        # Emotional resonance (20% weight)
        sentiment_data = metadata.get("sentiment_analysis", {})
        emotional_indicators = sentiment_data.get("emotional_indicators", [])
        if "excitement" in emotional_indicators:
            score += 8
        if "curiosity" in emotional_indicators:
            score += 6
        if "surprise" in emotional_indicators:
            score += 6
        
        # Content shareability (15% weight)
        if any(keyword in trend.title.lower() for keyword in 
               ["viral", "trending", "breaking", "shocking", "amazing"]):
            score += 15
        elif any(keyword in trend.title.lower() for keyword in 
                 ["new", "latest", "exclusive", "first"]):
            score += 10
        
        return min(100.0, max(0.0, score))
        
    except Exception as e:
        logger.error(f"Error calculating virality potential: {e}")
        return 50.0

async def _calculate_brand_safety_score(trend: Trend) -> float:
    """
    Calculate brand safety score for a trend.
    
    Args:
        trend: Trend object with enriched data
        
    Returns:
        Brand safety score (0-100, higher is safer)
    """
    try:
        score = 100.0  # Start with perfect safety
        metadata = trend.trend_metadata or {}
        
        # Check for risk factors
        sentiment_data = metadata.get("sentiment_analysis", {})
        risk_factors = sentiment_data.get("risk_factors", [])
        
        # Deduct points for each risk factor
        risk_deductions = {
            "political sensitivity": 20,
            "potential controversy": 15,
            "adult content": 30,
            "violence": 25,
            "illegal activity": 40,
            "hate speech": 35,
            "misinformation": 25,
        }
        
        for risk_factor in risk_factors:
            deduction = risk_deductions.get(risk_factor.lower(), 10)
            score -= deduction
        
        # Check sentiment distribution for negative sentiment
        sentiment_dist = sentiment_data.get("sentiment_distribution", {})
        negative_percentage = sentiment_dist.get("negative", 0)
        if negative_percentage > 30:
            score -= 15
        elif negative_percentage > 20:
            score -= 10
        elif negative_percentage > 10:
            score -= 5
        
        # Check for controversial keywords in trend title
        controversial_keywords = [
            "scandal", "controversy", "lawsuit", "arrest", "banned",
            "illegal", "fraud", "scam", "fake", "conspiracy"
        ]
        
        for keyword in controversial_keywords:
            if keyword in trend.title.lower():
                score -= 10
        
        return max(0.0, min(100.0, score))
        
    except Exception as e:
        logger.error(f"Error calculating brand safety score: {e}")
        return 75.0  # Default to moderately safe

async def _calculate_overall_score(trend: Trend) -> float:
    """
    Calculate overall trend score based on all factors.
    
    Args:
        trend: Trend object with all scores calculated
        
    Returns:
        Overall score (0-100)
    """
    try:
        # Weight different score components
        weights = {
            "base_score": 0.25,  # Original trend score
            "sustainability": 0.25,  # Long-term potential
            "pr_potential": 0.20,  # PR campaign potential
            "viral_potential": 0.15,  # Virality potential
            "brand_safety": 0.15,  # Brand safety factor
        }
        
        scores = {
            "base_score": trend.score or 50.0,
            "sustainability": trend.sustainability_score or 50.0,
            "pr_potential": trend.pr_potential_score or 50.0,
            "viral_potential": trend.viral_potential_score or 50.0,
            "brand_safety": trend.brand_safety_score or 75.0,
        }
        
        # Calculate weighted average
        overall_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        # Apply brand safety penalty if score is too low
        if scores["brand_safety"] < 50:
            overall_score *= 0.8  # 20% penalty for low safety
        
        return min(100.0, max(0.0, overall_score))
        
    except Exception as e:
        logger.error(f"Error calculating overall score: {e}")
        return 50.0

@celery_app.task
def trend_decay_analysis():
    """Analyze trend decay patterns and update relevance scores."""
    try:
        return asyncio.run(_run_decay_analysis())
    except Exception as exc:
        logger.error(f"Trend decay analysis failed: {exc}")
        raise

async def _run_decay_analysis() -> Dict[str, Any]:
    """Run trend decay analysis to identify declining trends."""
    try:
        async with get_db_session() as session:
            # Get trends older than 3 days
            cutoff_time = datetime.utcnow() - timedelta(days=3)
            query = select(Trend).where(Trend.created_at < cutoff_time)
            
            result = await session.execute(query)
            trends = result.scalars().all()
            
            decayed_count = 0
            
            for trend in trends:
                # Calculate decay factor based on age
                age_days = (datetime.utcnow() - trend.created_at).days
                decay_factor = max(0.1, 1.0 - (age_days * 0.1))  # 10% decay per day
                
                # Apply decay to scores
                trend.score *= decay_factor
                trend.sustainability_score = (trend.sustainability_score or 50.0) * decay_factor
                trend.pr_potential_score = (trend.pr_potential_score or 50.0) * decay_factor
                
                decayed_count += 1
            
            await session.commit()
            
            return {
                "processed": decayed_count,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in trend decay analysis: {e}")
        raise 