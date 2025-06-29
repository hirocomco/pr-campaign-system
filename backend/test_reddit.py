#!/usr/bin/env python3
"""
Test script for Reddit service functionality.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append('/app')

from app.services.trend_detection.reddit_service import RedditService
from app.core.config import settings


async def test_reddit_service():
    """Test the Reddit service."""
    print("🔍 Testing Reddit Service...")
    print(f"Reddit Client ID: {settings.REDDIT_CLIENT_ID[:10]}...")
    print(f"Reddit User Agent: {settings.REDDIT_USER_AGENT}")
    print("-" * 50)
    
    # Initialize Reddit service
    reddit_service = RedditService()
    
    if not reddit_service.reddit:
        print("❌ Reddit service not initialized - missing credentials")
        return
    
    print("✅ Reddit service initialized successfully")
    
    # Test fetching trending topics
    try:
        print("\n📊 Fetching trending topics from Reddit...")
        trends = await reddit_service.get_trending_topics(limit=10)
        
        if trends:
            print(f"✅ Found {len(trends)} trending topics!")
            print("\n🔥 Top 5 Reddit Trends:")
            print("=" * 60)
            
            for i, trend in enumerate(trends[:5], 1):
                print(f"\n{i}. {trend['title'][:80]}...")
                print(f"   📍 Subreddit: r/{trend['category']}")
                print(f"   📊 Score: {trend['score']:.2f} | Volume: {trend['volume']} comments")
                print(f"   🔗 URL: {trend['source_urls'][0]}")
                print(f"   🏷️  Keywords: {', '.join(trend['keywords'][:3])}")
        else:
            print("❌ No trends found")
            
    except Exception as e:
        print(f"❌ Error fetching trends: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_reddit_service()) 