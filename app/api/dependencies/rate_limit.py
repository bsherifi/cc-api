from fastapi import Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.user import User
from app.services.user import get_user_by_api_key


# Create a limiter instance
limiter = Limiter(key_func=get_remote_address)


async def get_user_rate_limit(request: Request) -> int:
    """
    Return the rate limit for a user based on their plan.
    Used by the slowapi decorator to determine the rate limit.
    
    IMPORTANT: This function must only take the request parameter
    when used with @limiter.limit().
    """
    # Get API key from header
    api_key = request.headers.get("x-api-key")
    if not api_key:
        # Default to lowest rate limit if no API key
        return 10
    
    # Get DB session from request state
    # SlowAPI needs this function to only take request as a parameter,
    # so we need to manually get the DB session
    from app.db.session import async_session
    
    async with async_session() as db:
        # Get user from API key
        user = await get_user_by_api_key(db, api_key)
        if not user or not user.plan:
            # Default to lowest rate limit if user or plan not found
            return 10
            
        # Store the user in the request state for later use
        request.state.user = user
        
        # Return the rate limit from the user's plan
        return user.plan.rate_limit 