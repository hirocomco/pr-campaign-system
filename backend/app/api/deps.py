"""
Dependencies for API endpoints.
"""

from typing import Generator, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


def get_current_user():
    """
    Get current user dependency (placeholder for authentication).
    
    Returns:
        dict: Current user information
    """
    # TODO: Implement proper authentication
    return {"id": "user-123", "email": "user@example.com"}


def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Get current active user dependency.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        dict: Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    # TODO: Implement user status checking
    return current_user


async def verify_api_key():
    """
    Verify API key for external access.
    
    Returns:
        bool: True if API key is valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    # TODO: Implement API key verification
    return True 