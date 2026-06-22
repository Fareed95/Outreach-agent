"""
db/base.py
----------
SQLAlchemy 2.0 declarative base for Syntrase.

All models inherit from this Base class. Import Base wherever you need
to register models with the metadata (e.g., in Alembic env.py).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all Syntrase SQLAlchemy models."""

    pass
