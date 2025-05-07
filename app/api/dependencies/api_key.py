from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.services.user import get_user_by_api_key


async def get_api_user(
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current user from the API key.
    """
    user = await get_user_by_api_key(db, x_api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return user 