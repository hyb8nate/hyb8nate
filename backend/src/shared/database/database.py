"""Database setup and session management using SQLAlchemy AsyncIO."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.shared.settings import settings

# Create the Base class for models
Base = declarative_base()

# Create async engine using computed database URL
engine = create_async_engine(
    "sqlite+aiosqlite:///./data/hyb8nate.db",
    echo=settings.DEBUG,
    future=True,
    # PostgreSQL specific pool settings (ignored for SQLite)
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize the database (create tables)"""
    # Ensure data directory exists only for SQLite
    os.makedirs("./data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
