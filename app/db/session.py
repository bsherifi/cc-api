import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/currency_converter")

# Create engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get DB session
async def get_db():
    """Dependency for getting async DB session."""
    db = async_session()
    try:
        yield db
    finally:
        await db.close() 