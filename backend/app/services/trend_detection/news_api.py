"""
News API service for collecting trending news topics.
"""

from typing import List, Dict, Any
import structlog
from newsapi import NewsApiClient
from app.core.config import settings

logger = structlog.get_logger()


class NewsAPIService:
    """Service for collecting trends from news sources."""
    
    def __init__(self):
        """Initialize News API service."""
        self.client = NewsApiClient(api_key=settings.NEWS_API_KEY) if settings.NEWS_API_KEY else None
    
    async def get_trending_topics(self, country: str = 'us') -> List[Dict[str, Any]]:
        """
        Get trending topics from news sources.
        
        Args:
            country: Country code for news
            
        Returns:
            List of trend dictionaries
        """
        if not self.client:
            logger.warning("News API key not configured")
            return []
        
        try:
            # Get top headlines
            headlines = self.client.get_top_headlines(country=country, page_size=20)
            
            trends = []
            for idx, article in enumerate(headlines.get('articles', [])):
                trend_data = {
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'category': 'news',
                    'score': max(0.2, 0.9 - (idx * 0.04)),
                    'velocity': max(0.1, 0.8 - (idx * 0.03)),
                    'volume': 500 - (idx * 25),
                    'platforms': ['news'],
                    'keywords': self._extract_keywords(article['title']),
                    'source_urls': [article.get('url', '')],
                    'metadata': {
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article.get('publishedAt', ''),
                        'author': article.get('author', ''),
                        'country': country
                    }
                }
                trends.append(trend_data)
            
            logger.info("Collected news trends", count=len(trends), country=country)
            return trends
            
        except Exception as e:
            logger.error("Failed to collect news trends", error=str(e))
            return []
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from article title."""
        # Simple keyword extraction - split and filter
        words = title.lower().split()
        keywords = [word.strip('.,!?":;') for word in words if len(word) > 3]
        return keywords[:5] 