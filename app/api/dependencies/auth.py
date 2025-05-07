from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.models.user import User
from app.services.user import get_user_by_email

# OAuth2 scheme for JWT token
security = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current user ID from the JWT token.
    Returns only the user ID to avoid async relationship loading issues.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get the payload from the token
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the subject (user email) from the payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Get the user from the database
        user = await get_user_by_email(db, email)
        if user is None:
            raise credentials_exception
        
        return user
        
    except JWTError:
        raise credentials_exception 