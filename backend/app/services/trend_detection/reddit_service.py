"""
Reddit service for collecting trending topics.
"""

from typing import List, Dict, Any
import structlog
import praw
from app.core.config import settings

logger = structlog.get_logger()


class RedditService:
    """Service for collecting trends from Reddit."""
    
    def __init__(self):
        """Initialize Reddit service."""
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
        else:
            self.reddit = None
    
    async def get_trending_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get trending topics from Reddit.
        
        Args:
            limit: Number of posts to fetch
            
        Returns:
            List of trend dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API credentials not configured")
            return []
        
        try:
            trends = []
            
            # Get hot posts from popular subreddits
            subreddits = ['all', 'news', 'worldnews', 'technology', 'entertainment']
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    hot_posts = subreddit.hot(limit=5)
                    
                    for idx, post in enumerate(hot_posts):
                        trend_data = {
                            'title': post.title,
                            'description': post.selftext[:200] if post.selftext else '',
                            'category': subreddit_name,
                            'score': max(0.1, min(1.0, post.score / 10000)),  # Normalize score
                            'velocity': max(0.1, min(1.0, post.upvote_ratio)),
                            'volume': post.num_comments,
                            'platforms': ['reddit'],
                            'keywords': self._extract_keywords(post.title),
                            'source_urls': [f"https://reddit.com{post.permalink}"],
                            'metadata': {
                                'subreddit': subreddit_name,
                                'author': str(post.author) if post.author else 'deleted',
                                'created_utc': post.created_utc,
                                'num_comments': post.num_comments,
                                'upvote_ratio': post.upvote_ratio,
                                'reddit_score': post.score
                            }
                        }
                        trends.append(trend_data)
                        
                except Exception as e:
                    logger.warning("Failed to fetch from subreddit", subreddit=subreddit_name, error=str(e))
            
            logger.info("Collected Reddit trends", count=len(trends))
            return trends
            
        except Exception as e:
            logger.error("Failed to collect Reddit trends", error=str(e))
            return []
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from post title."""
        # Simple keyword extraction
        words = title.lower().split()
        keywords = [word.strip('.,!?":;[]()') for word in words if len(word) > 3]
        return keywords[:5] 