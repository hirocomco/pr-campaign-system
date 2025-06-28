"""
Main API router for version 1.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import trends, campaigns, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 