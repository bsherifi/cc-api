from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import verify_password, get_password_hash, generate_api_key
from app.models.user import User, Plan
from app.schemas.user import UserCreate


async def get_plan_by_id(db: AsyncSession, plan_id: int) -> Plan:
    """Get a plan by its ID."""
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """Get a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_api_key(db: AsyncSession, api_key: str) -> User:
    """Get a user by their API key with plan relationship loaded."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.plan))
        .where(User.api_key == api_key)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    # Get the plan
    plan = await get_plan_by_id(db, user_in.plan_id)
    if not plan:
        raise ValueError(f"Plan with ID {user_in.plan_id} not found")
    
    # Create user
    api_key = generate_api_key()
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        api_key=api_key,
        credits=plan.initial_credits,
        plan_id=plan.id
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def deduct_credits(db: AsyncSession, user: User, credits: int) -> bool:
    """Deduct credits from a user's account. Returns True if successful."""
    if user.credits < credits:
        return False
    
    user.credits -= credits
    await db.commit()
    await db.refresh(user)
    
    return True 