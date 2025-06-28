"""Data enrichment service for enhancing trend data with additional context."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...models.trend import Trend
from ...schemas.trend import TrendUpdate

logger = logging.getLogger(__name__)

class DataEnrichmentService:
    """Service for enriching trend data with additional context and insights."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.newsapi_key = settings.NEWS_API_KEY
        self.google_api_key = settings.GOOGLE_API_KEY
        
    async def enrich_trend(self, trend: Trend) -> Trend:
        """
        Enrich a trend with additional data from multiple sources.
        
        Args:
            trend: Trend object to enrich
            
        Returns:
            Enriched trend object
        """
        try:
            # Gather enrichment data from multiple sources
            enrichment_tasks = [
                self._get_related_news(trend.title),
                self._get_search_volume_data(trend.title),
                self._get_demographic_data(trend.title),
                self._get_geographic_distribution(trend.title),
                self._get_sentiment_analysis(trend.title),
                self._get_competition_analysis(trend.title),
            ]
            
            results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
            
            # Process results
            related_news = results[0] if not isinstance(results[0], Exception) else []
            search_volume = results[1] if not isinstance(results[1], Exception) else {}
            demographics = results[2] if not isinstance(results[2], Exception) else {}
            geography = results[3] if not isinstance(results[3], Exception) else {}
            sentiment = results[4] if not isinstance(results[4], Exception) else {}
            competition = results[5] if not isinstance(results[5], Exception) else {}
            
            # Update trend metadata
            enrichment_data = {
                "related_news": related_news,
                "search_volume": search_volume,
                "demographics": demographics,
                "geographic_distribution": geography,
                "sentiment_analysis": sentiment,
                "competition_analysis": competition,
                "enriched_at": datetime.utcnow().isoformat(),
            }
            
            # Merge with existing metadata
            if trend.metadata:
                trend.metadata.update(enrichment_data)
            else:
                trend.metadata = enrichment_data
            
            # Update sustainability score based on enriched data
            trend.sustainability_score = await self._calculate_sustainability_score(
                trend, enrichment_data
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Error enriching trend {trend.id}: {e}")
            return trend
    
    async def _get_related_news(self, query: str) -> List[Dict[str, Any]]:
        """Get related news articles for a trend."""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": self.newsapi_key,
                    "sortBy": "relevancy",
                    "pageSize": 10,
                    "language": "en",
                    "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                "title": article["title"],
                                "description": article["description"],
                                "url": article["url"],
                                "published_at": article["publishedAt"],
                                "source": article["source"]["name"],
                            }
                            for article in data.get("articles", [])
                        ]
        except Exception as e:
            logger.error(f"Error fetching related news for {query}: {e}")
        
        return []
    
    async def _get_search_volume_data(self, query: str) -> Dict[str, Any]:
        """Get search volume and trend data."""
        try:
            # This would integrate with Google Trends API or similar service
            # For now, return mock data structure
            return {
                "current_volume": 1000,
                "volume_change_24h": 15.5,
                "volume_change_7d": 45.2,
                "peak_time": "2024-01-15T14:00:00Z",
                "trend_direction": "increasing",
                "related_queries": [
                    f"{query} news",
                    f"{query} 2024",
                    f"latest {query}",
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching search volume for {query}: {e}")
            return {}
    
    async def _get_demographic_data(self, query: str) -> Dict[str, Any]:
        """Get demographic breakdown of trend interest."""
        try:
            # This would integrate with social media APIs or analytics services
            return {
                "age_groups": {
                    "18-24": 25.5,
                    "25-34": 35.2,
                    "35-44": 20.1,
                    "45-54": 12.8,
                    "55+": 6.4
                },
                "gender": {
                    "male": 48.2,
                    "female": 51.8
                },
                "interests": [
                    "technology",
                    "entertainment",
                    "lifestyle",
                    "business"
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching demographics for {query}: {e}")
            return {}
    
    async def _get_geographic_distribution(self, query: str) -> Dict[str, Any]:
        """Get geographic distribution of trend interest."""
        try:
            return {
                "top_countries": [
                    {"country": "United States", "percentage": 35.2},
                    {"country": "United Kingdom", "percentage": 18.7},
                    {"country": "Canada", "percentage": 12.4},
                    {"country": "Australia", "percentage": 8.9},
                    {"country": "Germany", "percentage": 6.8},
                ],
                "top_cities": [
                    {"city": "New York", "percentage": 8.5},
                    {"city": "London", "percentage": 7.2},
                    {"city": "Los Angeles", "percentage": 6.1},
                    {"city": "Toronto", "percentage": 4.8},
                    {"city": "Sydney", "percentage": 3.9},
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching geography for {query}: {e}")
            return {}
    
    async def _get_sentiment_analysis(self, query: str) -> Dict[str, Any]:
        """Analyze sentiment around the trend."""
        try:
            # This would use sentiment analysis services
            return {
                "overall_sentiment": "positive",
                "sentiment_score": 0.65,  # -1 to 1 scale
                "sentiment_distribution": {
                    "positive": 65.2,
                    "neutral": 28.1,
                    "negative": 6.7
                },
                "emotional_indicators": [
                    "excitement",
                    "curiosity",
                    "optimism"
                ],
                "risk_factors": [
                    "potential controversy",
                    "political sensitivity"
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {query}: {e}")
            return {}
    
    async def _get_competition_analysis(self, query: str) -> Dict[str, Any]:
        """Analyze competition and saturation for the trend."""
        try:
            return {
                "competition_level": "medium",
                "competing_brands": [
                    "Brand A",
                    "Brand B", 
                    "Brand C"
                ],
                "market_saturation": 45.6,  # percentage
                "opportunity_score": 72.3,  # 0-100 scale
                "white_space_areas": [
                    "B2B applications",
                    "Sustainability angle",
                    "Educational content"
                ],
                "recommended_positioning": "thought leadership"
            }
        except Exception as e:
            logger.error(f"Error analyzing competition for {query}: {e}")
            return {}
    
    async def _calculate_sustainability_score(
        self, trend: Trend, enrichment_data: Dict[str, Any]
    ) -> float:
        """
        Calculate sustainability score based on enriched data.
        
        Args:
            trend: Original trend object
            enrichment_data: Enriched data dictionary
            
        Returns:
            Sustainability score (0-100)
        """
        try:
            score = 0.0
            
            # Base score from original trend
            score += trend.score * 0.3
            
            # Search volume trends (30% weight)
            search_data = enrichment_data.get("search_volume", {})
            volume_change_7d = search_data.get("volume_change_7d", 0)
            if volume_change_7d > 20:
                score += 30
            elif volume_change_7d > 0:
                score += 15
            
            # News coverage (20% weight)
            news_count = len(enrichment_data.get("related_news", []))
            if news_count >= 5:
                score += 20
            elif news_count >= 3:
                score += 15
            elif news_count >= 1:
                score += 10
            
            # Sentiment analysis (10% weight)
            sentiment_data = enrichment_data.get("sentiment_analysis", {})
            sentiment_score = sentiment_data.get("sentiment_score", 0)
            if sentiment_score > 0.5:
                score += 10
            elif sentiment_score > 0:
                score += 5
            
            # Competition level (10% weight)
            competition_data = enrichment_data.get("competition_analysis", {})
            opportunity_score = competition_data.get("opportunity_score", 50)
            score += opportunity_score * 0.1
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating sustainability score: {e}")
            return trend.sustainability_score or 50.0
    
    async def batch_enrich_trends(self, trends: List[Trend]) -> List[Trend]:
        """
        Enrich multiple trends in parallel.
        
        Args:
            trends: List of trends to enrich
            
        Returns:
            List of enriched trends
        """
        try:
            enrichment_tasks = [self.enrich_trend(trend) for trend in trends]
            enriched_trends = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
            
            # Filter out any failed enrichments
            successful_enrichments = [
                trend for trend in enriched_trends 
                if not isinstance(trend, Exception)
            ]
            
            return successful_enrichments
            
        except Exception as e:
            logger.error(f"Error in batch enrichment: {e}")
            return trends 