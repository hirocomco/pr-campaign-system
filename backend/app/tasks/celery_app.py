"""
Celery application configuration for background tasks.
"""

import asyncio
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "pr_campaign_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.daily_analysis",
        "app.tasks.trend_scoring", 
        "app.tasks.digest_email"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    # Daily trend analysis at 6 AM UTC
    "daily-trend-analysis": {
        "task": "app.tasks.daily_analysis.analyze_daily_trends",
        "schedule": crontab(hour=6, minute=0),  # 6:00 AM UTC daily
    },
    # Trend scoring update every 4 hours
    "update-trend-scores": {
        "task": "app.tasks.trend_scoring.update_trend_scores",
        "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours
    },
    # Daily digest email at 8 AM UTC
    "daily-digest-email": {
        "task": "app.tasks.digest_email.send_daily_digest",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM UTC daily
    },
    # Cleanup old trends weekly
    "cleanup-old-trends": {
        "task": "app.tasks.daily_analysis.cleanup_old_trends", 
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2 AM UTC
    },
}


def run_async_task(async_func):
    """
    Utility function to run async functions in Celery tasks.
    
    Args:
        async_func: Async function to run
        
    Returns:
        Result of the async function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_func)
    finally:
        loop.close() 