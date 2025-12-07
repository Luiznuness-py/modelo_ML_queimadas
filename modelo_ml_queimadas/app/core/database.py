"""
Database configuration and session management.
"""
from typing import AsyncGenerator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings
from app.models.base_model import Base


# Build database URL from separate parameters
_database_url = settings.get_database_url(
    async_driver=True, 
    use_test_db=(settings.ENVIRONMENT.upper() == "TEST")
)

print("\nDatabase URL:", _database_url)

# Create async ENGINE
async_engine = create_async_engine(
    _database_url,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
)

# Create async SESSION factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ====
# ASYNC DATABASE SESSION
# ====
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    For database sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ====
# SYNC DATABASE ENGINE
# ====
TO-DO: Refactor _database_url to use this function when creating sync engine in memory
def get_sync_engine() -> Engine:
    """
    Create synchronous engine.
    """
    return create_engine(
        _database_url,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
    )


# ====
# BASE MODEL
# ====

Base = DBBase