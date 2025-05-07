from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.api_key import get_api_user
from app.services.user import deduct_credits


async def check_credits(
    credits_required: int,
    user: User = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Check if a user has enough credits for an operation.
    Raises an HTTPException if the user doesn't have enough credits.
    """
    if user.credits < credits_required:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Not enough credits. Required: {credits_required}, Available: {user.credits}"
        )
    
    return user


def require_credits(credits_to_deduct: int):
    """
    Returns a dependency function that deducts credits from a user's account.
    """
    async def _deduct_user_credits(
        user: User = Depends(get_api_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # First check if the user has enough credits
        if user.credits < credits_to_deduct:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Not enough credits. Required: {credits_to_deduct}, Available: {user.credits}"
            )
        
        # Deduct the credits
        success = await deduct_credits(db, user, credits_to_deduct)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deduct credits"
            )
        
        return user
    
    return _deduct_user_credits 