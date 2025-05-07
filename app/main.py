import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect

from app.api import api_router
from app.api.dependencies.rate_limit import limiter
from app.core.config import settings
from app.db.session import get_db, engine


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Subscription-based currency converter API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Include the API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    Root endpoint, returns API info.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "Subscription-based currency converter API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# Initialize database with default plans
@app.on_event("startup")
async def init_db():
    """
    Initialize the database with default plans.
    """
    from sqlalchemy import select, text
    from app.db.session import async_session
    from app.models.user import Plan
    
    async with async_session() as db:
        try:
            # Check if tables exist first by running a simple query
            try:
                await db.execute(text("SELECT 1 FROM plan LIMIT 1"))
                # If we got here, the table exists
            except Exception:
                # Table doesn't exist yet, migrations need to run
                print("Database tables not ready yet - will be created by migrations")
                return
            
            # Check if plans already exist
            result = await db.execute(select(Plan))
            plans = result.scalars().all()
            
            if not plans:
                print("Creating default plans")
                # Create default plans
                default_plans = [
                    Plan(name="Free", rate_limit=10, initial_credits=100),
                    Plan(name="Pro", rate_limit=60, initial_credits=1000),
                    Plan(name="Diamond", rate_limit=120, initial_credits=5000),
                ]
                
                for plan in default_plans:
                    db.add(plan)
                
                await db.commit()
                print("Default plans created successfully")
        except Exception as e:
            print(f"Error during database initialization: {e}")
            # Don't raise the exception, just log it
            # This allows the app to start even if DB is not ready 