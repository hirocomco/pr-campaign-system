"""
Google Trends service for collecting trending topics.
"""

from typing import List, Dict, Any
import structlog
from pytrends.request import TrendReq

logger = structlog.get_logger()


class GoogleTrendsService:
    """Service for collecting trends from Google Trends."""
    
    def __init__(self):
        """Initialize Google Trends service."""
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    async def get_trending_topics(self, geo: str = 'US') -> List[Dict[str, Any]]:
        """
        Get trending topics from Google Trends.
        
        Args:
            geo: Geographic location for trends
            
        Returns:
            List of trend dictionaries
        """
        try:
            # Get trending searches
            trending_searches = self.pytrends.trending_searches(pn=geo)
            
            trends = []
            for idx, topic in enumerate(trending_searches[0][:20]):  # Top 20
                trend_data = {
                    'title': str(topic),
                    'description': f"Trending topic: {topic}",
                    'category': 'general',
                    'score': max(0.1, 1.0 - (idx * 0.05)),  # Decreasing score
                    'velocity': max(0.1, 1.0 - (idx * 0.03)),
                    'volume': 1000 - (idx * 50),
                    'platforms': ['google'],
                    'keywords': [str(topic).lower()],
                    'source_urls': [f"https://trends.google.com/trends/explore?q={topic}"],
                    'metadata': {
                        'geo': geo,
                        'source': 'google_trends',
                        'rank': idx + 1
                    }
                }
                trends.append(trend_data)
            
            logger.info("Collected Google trends", count=len(trends), geo=geo)
            return trends
            
        except Exception as e:
            logger.error("Failed to collect Google trends", error=str(e))
            return [] 