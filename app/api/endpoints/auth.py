from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User, Plan
from app.schemas.user import UserCreate, UserLogin, Token, UserInfo
from app.services.user import create_user, authenticate_user, get_user_by_email
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the user
    user = await create_user(db, user_in)
    
    # Create access token
    access_token = create_access_token(user.email)
    
    # Get plan details for response
    result = await db.execute(select(Plan).where(Plan.id == user.plan_id))
    plan = result.scalar_one()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "api_key": user.api_key,
        "credits": user.credits,
        "rate_limit": plan.rate_limit
    }


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    """
    # Authenticate the user
    user = await authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(user.email)
    
    # Get plan details for response
    result = await db.execute(select(Plan).where(Plan.id == user.plan_id))
    plan = result.scalar_one()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "api_key": user.api_key,
        "credits": user.credits,
        "rate_limit": plan.rate_limit
    }


@router.get("/me", response_model=UserInfo)
async def get_me(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    """
    Get current user information.
    """
    # Explicitly load user with plan relationship
    result = await db.execute(
        select(User)
        .options(selectinload(User.plan))
        .where(User.id == current_user_id.id)
    )
    user = result.scalar_one()
    return user 