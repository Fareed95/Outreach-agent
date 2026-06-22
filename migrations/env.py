"""
migrations/env.py
-----------------
Alembic async migration environment for Syntrase.

Reads DATABASE_URL_MIGRATIONS from environment / .env file (the DIRECT
Supabase connection — not pooler) for DDL operations. Imports all models
so autogenerate can detect schema changes.
"""

import asyncio
import os
import socket
from logging.config import fileConfig
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ── Load .env before anything else ───────────────────────────────────────────
load_dotenv()

# ── Alembic Config object ────────────────────────────────────────────────────
config = context.config

# ── Python logging from alembic.ini ──────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import Base + all models (required for autogenerate) ─────────────────────
from db.base import Base  # noqa: E402
import db.models  # noqa: E402, F401  — triggers model registration

target_metadata = Base.metadata

# ── Build async URL from env ─────────────────────────────────────────────────
_migrations_url = os.getenv("DATABASE_URL_MIGRATIONS", "")
if _migrations_url.startswith("postgresql://"):
    _async_url = _migrations_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
else:
    _async_url = _migrations_url


def _resolve_ipv4(host: str, port: int) -> str:
    """Resolve hostname to IPv4 address, needed when environment lacks IPv6."""
    try:
        results = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if results:
            return results[0][4][0]
    except socket.gaierror:
        pass
    return host


def _make_engine_url() -> str:
    """Replace hostname with IPv4 address if needed to avoid IPv6 issues."""
    parsed = urlparse(_async_url)
    hostname = parsed.hostname
    port = parsed.port or 5432

    # Try resolving to IPv4 first
    ipv4 = _resolve_ipv4(hostname, port)
    if ipv4 != hostname:
        # Rebuild URL with IPv4 address
        # netloc is user:pass@host:port — replace host part
        new_netloc = parsed.netloc.replace(hostname, ipv4)
        return parsed._replace(netloc=new_netloc).geturl()
    return _async_url


# ── Offline mode (SQL script generation) ─────────────────────────────────────


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL (no Engine needed).
    Calls to context.execute() emit DDL to the script output.
    """
    context.configure(
        url=_async_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (live DB connection) ─────────────────────────────────────────


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations against the live database."""
    engine_url = _make_engine_url()

    connectable = create_async_engine(
        engine_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
