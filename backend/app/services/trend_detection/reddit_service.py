"""
Reddit service for collecting trending topics.
"""

from typing import List, Dict, Any
import structlog
import praw
import asyncio
from app.core.config import settings
from app.services.content_categorization.ai_categorizer import AIContentCategorizer, ContentSafetyLevel

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
            
        # Initialize AI categorizer
        self.ai_categorizer = AIContentCategorizer() if settings.AI_CATEGORIZATION_ENABLED else None
    
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
            filtered_count = 0
            
            # Get configurable subreddits from settings
            subreddits = settings.REDDIT_SUBREDDITS
            posts_per_subreddit = settings.REDDIT_POSTS_PER_SUBREDDIT
            algorithm = settings.REDDIT_TRENDING_ALGORITHM
            
            logger.info("Fetching Reddit trends", 
                       subreddits=subreddits, 
                       algorithm=algorithm, 
                       posts_per_sub=posts_per_subreddit,
                       ai_categorization_enabled=settings.AI_CATEGORIZATION_ENABLED)
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Use configurable trending algorithm
                    if algorithm == "hot":
                        posts = subreddit.hot(limit=posts_per_subreddit)
                    elif algorithm == "top":
                        posts = subreddit.top(time_filter="day", limit=posts_per_subreddit)
                    elif algorithm == "rising":
                        posts = subreddit.rising(limit=posts_per_subreddit)
                    elif algorithm == "new":
                        posts = subreddit.new(limit=posts_per_subreddit)
                    else:
                        posts = subreddit.hot(limit=posts_per_subreddit)
                    
                    for idx, post in enumerate(posts):
                        # Extract Reddit metadata
                        reddit_metadata = self._extract_reddit_metadata(post)
                        
                        # Apply AI categorization
                        content_category = None
                        if settings.AI_CATEGORIZATION_ENABLED and self.ai_categorizer:
                            try:
                                content_category = await self.ai_categorizer.categorize_content(
                                    title=post.title,
                                    description=post.selftext[:500] if post.selftext else '',
                                    subreddit=subreddit_name,
                                    reddit_metadata=reddit_metadata
                                )
                                
                                # Check if content should be filtered based on AI categorization
                                if not self._should_include_content(content_category):
                                    filtered_count += 1
                                    logger.debug("Content filtered by AI", 
                                               title=post.title[:50],
                                               safety_level=content_category.safety_level.value,
                                               confidence=content_category.confidence)
                                    continue
                                    
                            except Exception as e:
                                logger.warning("AI categorization failed", error=str(e), title=post.title[:50])
                                # Fallback to keyword filtering if enabled
                                if settings.FALLBACK_TO_KEYWORD_FILTER and settings.CONTENT_FILTER_ENABLED:
                                    if self._is_content_filtered(post):
                                        filtered_count += 1
                                        logger.debug("Content filtered by fallback", title=post.title[:50])
                                        continue
                        
                        # Fallback filtering for when AI categorization is disabled
                        elif settings.CONTENT_FILTER_ENABLED:
                            if self._is_content_filtered(post):
                                filtered_count += 1
                                logger.debug("Content filtered by keywords", title=post.title[:50])
                                continue
                        
                        # Calculate enhanced trending score
                        trending_score = self._calculate_trending_score(post, algorithm)
                        
                        # Build trend data with categorization results
                        trend_data = {
                            'title': post.title,
                            'description': post.selftext[:200] if post.selftext else '',
                            'category': subreddit_name,
                            'score': trending_score,
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
                                'reddit_score': post.score,
                                'algorithm': algorithm,
                                'awards_received': getattr(post, 'total_awards_received', 0),
                                'is_original_content': getattr(post, 'is_original_content', False),
                                'position_in_subreddit': idx + 1,
                                'reddit_metadata': reddit_metadata,
                                'ai_categorization': {
                                    'safety_level': content_category.safety_level.value if content_category else None,
                                    'confidence': content_category.confidence if content_category else None,
                                    'primary_category': content_category.primary_category if content_category else None,
                                    'reasoning': content_category.reasoning if content_category else None,
                                    'is_brand_safe': content_category.is_brand_safe if content_category else None
                                } if content_category else None
                            }
                        }
                        trends.append(trend_data)
                        
                except Exception as e:
                    logger.warning("Failed to fetch from subreddit", subreddit=subreddit_name, error=str(e))
            
            # Sort trends by score (highest first)
            trends.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info("Collected Reddit trends", 
                       count=len(trends), 
                       filtered_count=filtered_count,
                       ai_categorization_enabled=settings.AI_CATEGORIZATION_ENABLED)
            return trends
            
        except Exception as e:
            logger.error("Failed to collect Reddit trends", error=str(e))
            return []
    
    def _calculate_trending_score(self, post, algorithm: str) -> float:
        """
        Calculate enhanced trending score based on multiple factors.
        
        Args:
            post: Reddit post object
            algorithm: Algorithm used to fetch posts
            
        Returns:
            Normalized trending score (0.1-1.0)
        """
        try:
            # Base score from Reddit points (normalized)
            base_score = max(0.1, min(1.0, post.score / 10000))
            
            # Engagement ratio (comments per upvote)
            engagement_ratio = 0.0
            if post.score > 0:
                engagement_ratio = min(1.0, post.num_comments / post.score)
            
            # Time decay factor (newer posts get higher scores)
            import time
            current_time = time.time()
            post_age_hours = (current_time - post.created_utc) / 3600
            time_decay = max(0.1, 1.0 / (1.0 + post_age_hours / 24))  # Decay over 24 hours
            
            # Awards factor (premium engagement)
            awards_factor = min(1.0, getattr(post, 'total_awards_received', 0) / 10)
            
            # Algorithm-specific weights
            if algorithm == "hot":
                # Hot algorithm: Balance recency, score, and engagement
                trending_score = (
                    base_score * 0.4 +
                    post.upvote_ratio * 0.2 +
                    engagement_ratio * 0.2 +
                    time_decay * 0.15 +
                    awards_factor * 0.05
                )
            elif algorithm == "top":
                # Top algorithm: Emphasize score and awards
                trending_score = (
                    base_score * 0.6 +
                    post.upvote_ratio * 0.2 +
                    engagement_ratio * 0.1 +
                    awards_factor * 0.1
                )
            elif algorithm == "rising":
                # Rising algorithm: Emphasize recent rapid growth
                trending_score = (
                    base_score * 0.3 +
                    post.upvote_ratio * 0.2 +
                    engagement_ratio * 0.2 +
                    time_decay * 0.25 +
                    awards_factor * 0.05
                )
            else:  # new or default
                # New algorithm: Emphasize recency and initial engagement
                trending_score = (
                    base_score * 0.2 +
                    post.upvote_ratio * 0.3 +
                    engagement_ratio * 0.2 +
                    time_decay * 0.3
                )
            
            return max(0.1, min(1.0, trending_score))
            
        except Exception as e:
            logger.warning("Failed to calculate trending score", error=str(e))
            return max(0.1, min(1.0, post.score / 10000))  # Fallback to simple score
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from post title."""
        # Simple keyword extraction
        words = title.lower().split()
        keywords = [word.strip('.,!?":;[]()') for word in words if len(word) > 3]
        return keywords[:5]
    
    def _extract_reddit_metadata(self, post) -> Dict[str, Any]:
        """Extract comprehensive metadata from Reddit post."""
        metadata = {}
        
        # Basic post info
        metadata['over_18'] = getattr(post, 'over_18', False)
        metadata['locked'] = getattr(post, 'locked', False)
        metadata['stickied'] = getattr(post, 'stickied', False)
        metadata['gilded'] = getattr(post, 'gilded', 0)
        metadata['awards_received'] = getattr(post, 'total_awards_received', 0)
        
        # Flairs
        metadata['link_flair_text'] = getattr(post, 'link_flair_text', None)
        metadata['author_flair_text'] = getattr(post, 'author_flair_text', None)
        
        # Additional content indicators
        metadata['is_video'] = getattr(post, 'is_video', False)
        metadata['is_original_content'] = getattr(post, 'is_original_content', False)
        metadata['is_reddit_media_domain'] = getattr(post, 'is_reddit_media_domain', False)
        metadata['domain'] = getattr(post, 'domain', '')
        
        # Engagement metrics
        metadata['score'] = post.score
        metadata['upvote_ratio'] = post.upvote_ratio
        metadata['num_comments'] = post.num_comments
        
        return metadata
    
    def _should_include_content(self, content_category) -> bool:
        """Determine if content should be included based on AI categorization."""
        if not content_category:
            return True  # Include if categorization failed
            
        # Block unsafe content levels
        unsafe_levels = {
            ContentSafetyLevel.BLOCKED,
            ContentSafetyLevel.VIOLENT, 
            ContentSafetyLevel.NSFW,
            ContentSafetyLevel.POLITICAL
        }
        
        if content_category.safety_level in unsafe_levels:
            return False
            
        # For controversial content, check confidence
        if content_category.safety_level == ContentSafetyLevel.CONTROVERSIAL:
            return content_category.confidence < 0.8  # Only include if AI is uncertain
            
        # For caution content, check settings
        if content_category.safety_level == ContentSafetyLevel.CAUTION:
            return settings.ALLOW_CAUTION_CONTENT and content_category.confidence >= settings.AI_CATEGORIZATION_MIN_CONFIDENCE
            
        # Include safe content
        return content_category.safety_level == ContentSafetyLevel.SAFE
    
    def _is_content_filtered(self, post) -> bool:
        """
        Check if content should be filtered based on keywords.
        
        Args:
            post: Reddit post object
            
        Returns:
            True if content should be filtered, False otherwise
        """
        try:
            # Combine title and description for filtering
            content_text = (post.title + " " + (post.selftext or "")).lower()
            
            # Check war-related keywords
            for keyword in settings.CONTENT_FILTER_WAR_KEYWORDS:
                if keyword.lower() in content_text:
                    logger.debug("Content filtered: war keyword found", 
                               keyword=keyword, 
                               title=post.title[:50])
                    return True
            
            # Check politics-related keywords
            for keyword in settings.CONTENT_FILTER_POLITICS_KEYWORDS:
                if keyword.lower() in content_text:
                    logger.debug("Content filtered: politics keyword found", 
                               keyword=keyword, 
                               title=post.title[:50])
                    return True
            
            # Check violence-related keywords
            for keyword in settings.CONTENT_FILTER_VIOLENCE_KEYWORDS:
                if keyword.lower() in content_text:
                    logger.debug("Content filtered: violence keyword found", 
                               keyword=keyword, 
                               title=post.title[:50])
                    return True
            
            # Check subreddit-specific filtering
            subreddit_name = str(post.subreddit).lower()
            if subreddit_name in ['politics', 'worldpolitics', 'conservative', 'liberal', 
                                 'the_donald', 'sandersforpresident', 'politicalhumor',
                                 'combatfootage', 'ukraine', 'russia', 'war']:
                logger.debug("Content filtered: restricted subreddit", 
                           subreddit=subreddit_name, 
                           title=post.title[:50])
                return True
            
            return False
            
        except Exception as e:
            logger.warning("Error in content filtering", error=str(e))
            # When in doubt, don't filter - let content through
            return False 