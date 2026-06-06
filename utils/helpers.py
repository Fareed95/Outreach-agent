"""
utils/helpers.py
-----------------
General helper functions for the outreach agent.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_uuid() -> str:
    """Generate a unique identifier string.

    Returns:
        A UUID4 string.
    """
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get the current UTC datetime.

    Returns:
        Current datetime in UTC timezone.
    """
    return datetime.now(timezone.utc)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime as an ISO 8601 string.

    Args:
        dt: Datetime to format. Defaults to current UTC time.

    Returns:
        ISO 8601 formatted string.
    """
    if dt is None:
        dt = utc_now()
    return dt.isoformat()


def parse_timestamp(ts: str) -> datetime:
    """Parse an ISO 8601 timestamp string.

    Args:
        ts: ISO 8601 formatted timestamp string.

    Returns:
        Parsed datetime object.
    """
    return datetime.fromisoformat(ts)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis.

    Args:
        text: Text to truncate.
        max_length: Maximum character length.

    Returns:
        Truncated text string.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."