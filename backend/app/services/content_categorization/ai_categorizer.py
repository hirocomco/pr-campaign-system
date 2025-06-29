"""
AI-powered content categorization service for brand safety.
"""

from typing import Dict, List, Any, Optional
import structlog
from pydantic import BaseModel
from enum import Enum

from app.services.angle_generation.ai_service import AIService
from app.core.config import settings

logger = structlog.get_logger()


class ContentSafetyLevel(Enum):
    """Content safety levels for brand safety."""
    SAFE = "safe"
    CAUTION = "caution"
    POLITICAL = "political"
    VIOLENT = "violent"
    CONTROVERSIAL = "controversial"
    NSFW = "nsfw"
    BLOCKED = "blocked"


class ContentCategory(BaseModel):
    """Content categorization result."""
    safety_level: ContentSafetyLevel
    confidence: float  # 0.0 to 1.0
    primary_category: str
    secondary_categories: List[str]
    reasoning: str
    metadata_signals: Dict[str, Any]
    is_brand_safe: bool


class AIContentCategorizer:
    """AI-powered content categorizer for brand safety."""
    
    def __init__(self):
        """Initialize the AI categorizer."""
        self.ai_service = AIService()
        
    async def categorize_content(
        self, 
        title: str, 
        description: str = "", 
        subreddit: str = "",
        reddit_metadata: Optional[Dict[str, Any]] = None
    ) -> ContentCategory:
        """
        Categorize content using AI analysis and Reddit metadata.
        
        Args:
            title: Post title
            description: Post content/description
            subreddit: Subreddit name
            reddit_metadata: Additional Reddit metadata (flairs, flags, etc.)
            
        Returns:
            ContentCategory with safety assessment
        """
        try:
            # Extract metadata signals
            metadata_signals = self._extract_metadata_signals(reddit_metadata or {})
            
            # Check for immediate blocking signals
            immediate_block = self._check_immediate_blocks(title, description, subreddit, metadata_signals)
            if immediate_block:
                return ContentCategory(
                    safety_level=ContentSafetyLevel.BLOCKED,
                    confidence=1.0,
                    primary_category="auto_blocked",
                    secondary_categories=[],
                    reasoning=f"Automatically blocked: {immediate_block}",
                    metadata_signals=metadata_signals,
                    is_brand_safe=False
                )
            
            # Use AI for nuanced categorization
            ai_result = await self._ai_categorize(title, description, subreddit, metadata_signals)
            
            # Combine AI analysis with metadata signals
            final_category = self._combine_signals(ai_result, metadata_signals)
            
            logger.info("Content categorized", 
                       title=title[:50], 
                       safety_level=final_category.safety_level.value,
                       confidence=final_category.confidence)
            
            return final_category
            
        except Exception as e:
            logger.error("Content categorization failed", error=str(e), title=title[:50])
            # Default to CAUTION when categorization fails
            return ContentCategory(
                safety_level=ContentSafetyLevel.CAUTION,
                confidence=0.5,
                primary_category="analysis_failed",
                secondary_categories=[],
                reasoning=f"Categorization failed, defaulting to caution: {str(e)}",
                metadata_signals=reddit_metadata or {},
                is_brand_safe=False
            )
    
    def _extract_metadata_signals(self, reddit_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant signals from Reddit metadata."""
        signals = {}
        
        # NSFW flag
        if reddit_metadata.get('over_18', False):
            signals['nsfw'] = True
            
        # Post flairs
        if reddit_metadata.get('link_flair_text'):
            signals['post_flair'] = reddit_metadata['link_flair_text'].lower()
            
        # Author flairs  
        if reddit_metadata.get('author_flair_text'):
            signals['author_flair'] = reddit_metadata['author_flair_text'].lower()
            
        # Content flags
        if reddit_metadata.get('locked', False):
            signals['locked'] = True
            
        if reddit_metadata.get('stickied', False):
            signals['stickied'] = True
            
        # High engagement/awards can indicate quality content
        if reddit_metadata.get('gilded', 0) > 0:
            signals['gilded'] = reddit_metadata['gilded']
            
        if reddit_metadata.get('awards_received', 0) > 0:
            signals['awarded'] = reddit_metadata['awards_received']
            
        return signals
    
    def _check_immediate_blocks(
        self, 
        title: str, 
        description: str, 
        subreddit: str, 
        metadata_signals: Dict[str, Any]
    ) -> Optional[str]:
        """Check for content that should be immediately blocked."""
        
        # NSFW content
        if metadata_signals.get('nsfw', False):
            return "NSFW content"
            
        # Known problematic subreddits (from config)
        blocked_subreddits = set(s.lower() for s in settings.BLOCKED_SUBREDDITS)
        
        if subreddit.lower() in blocked_subreddits:
            return f"Blocked subreddit: {subreddit}"
            
        # Problematic flairs (from config)
        if metadata_signals.get('post_flair'):
            flair = metadata_signals['post_flair']
            blocked_flairs = [f.lower() for f in settings.BLOCKED_FLAIRS]
            if any(blocked in flair for blocked in blocked_flairs):
                return f"Blocked flair: {flair}"
                
        return None
    
    async def _ai_categorize(
        self, 
        title: str, 
        description: str, 
        subreddit: str, 
        metadata_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to categorize content with nuanced understanding."""
        
        # Build prompt from configurable template
        prompt = settings.AI_CATEGORIZATION_USER_PROMPT_TEMPLATE.format(
            title=title,
            description=description[:300],
            subreddit=subreddit,
            metadata_signals=metadata_signals
        )

        try:
            messages = [
                {"role": "system", "content": settings.AI_CATEGORIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.ai_service.generate_with_fallback(
                messages=messages,
                max_tokens=300,
                temperature=0.1  # Low temperature for consistent categorization
            )
            
            # Parse JSON response
            import json
            result = json.loads(response.strip())
            return result
            
        except Exception as e:
            logger.warning("AI categorization failed", error=str(e))
            # Fallback categorization
            return {
                "safety_level": "CAUTION",
                "confidence": 0.3,
                "primary_category": "unknown",
                "secondary_categories": [],
                "reasoning": f"AI analysis failed: {str(e)}",
                "pr_suitability": "Unknown - manual review needed"
            }
    
    def _combine_signals(
        self, 
        ai_result: Dict[str, Any], 
        metadata_signals: Dict[str, Any]
    ) -> ContentCategory:
        """Combine AI analysis with metadata signals for final categorization."""
        
        try:
            # Parse AI result
            safety_level = ContentSafetyLevel(ai_result.get('safety_level', 'caution').lower())
            confidence = float(ai_result.get('confidence', 0.5))
            
            # Adjust confidence based on metadata signals
            if metadata_signals.get('gilded', 0) > 0 or metadata_signals.get('awarded', 0) > 0:
                # Awarded content is often higher quality
                if safety_level == ContentSafetyLevel.SAFE:
                    confidence = min(1.0, confidence + 0.1)
                    
            if metadata_signals.get('locked', False):
                # Locked content is often controversial
                if safety_level == ContentSafetyLevel.SAFE:
                    safety_level = ContentSafetyLevel.CAUTION
                    confidence = max(confidence - 0.2, 0.3)
            
            # Determine brand safety
            brand_safe = safety_level in [ContentSafetyLevel.SAFE, ContentSafetyLevel.CAUTION] and confidence >= 0.7
            
            return ContentCategory(
                safety_level=safety_level,
                confidence=confidence,
                primary_category=ai_result.get('primary_category', 'unknown'),
                secondary_categories=ai_result.get('secondary_categories', []),
                reasoning=ai_result.get('reasoning', 'AI analysis completed'),
                metadata_signals=metadata_signals,
                is_brand_safe=brand_safe
            )
            
        except Exception as e:
            logger.error("Signal combination failed", error=str(e))
            return ContentCategory(
                safety_level=ContentSafetyLevel.CAUTION,
                confidence=0.3,
                primary_category="error",
                secondary_categories=[],
                reasoning=f"Analysis error: {str(e)}",
                metadata_signals=metadata_signals,
                is_brand_safe=False
            ) 