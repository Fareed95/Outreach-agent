"""
db/database.py
--------------
Async database engine and session management for Syntrase.

Uses SQLAlchemy 2.0 async engine with asyncpg driver, configured
for Supabase connection pooling. Provides FastAPI-compatible
dependency injection via get_async_session().
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from config.settings import settings


# ── Async Engine ──────────────────────────────────────────────────────────────

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# ── Session Factory ───────────────────────────────────────────────────────────

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Dependencies ──────────────────────────────────────────────────────────────


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    Usage as FastAPI dependency:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_async_session)):
            ...

    Usage standalone:
        async with async_session_maker() as session:
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# ── Health Check ──────────────────────────────────────────────────────────────


async def check_connection() -> bool:
    """Run a simple SELECT 1 health check against the database.

    Returns:
        True if the connection is healthy, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
