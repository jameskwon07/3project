"""
Database configuration and setup
Uses SQLite3 for development, PostgreSQL for production
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

# Database URL from environment variable
# Format examples:
# - SQLite: sqlite+aiosqlite:///./master.db
# - PostgreSQL: postgresql+asyncpg://user:password@localhost/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./master.db"  # Default to SQLite for development
)

# Determine if using SQLite or PostgreSQL
IS_SQLITE = DATABASE_URL.startswith("sqlite+aiosqlite")

# Create async engine with appropriate settings
# SQLite does not support connection pooling, so we only use pool settings for PostgreSQL
if IS_SQLITE:
    # SQLite: No connection pooling, simpler settings
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to False, we'll use custom query logging
        future=True,
    )
else:
    # PostgreSQL: Use connection pooling
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to False, we'll use custom query logging
        future=True,
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Maximum overflow connections
        pool_pre_ping=True,  # Verify connections before using
    )

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    Used in FastAPI route dependencies
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

