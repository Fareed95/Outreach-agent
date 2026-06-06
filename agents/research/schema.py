"""
agents/research/schema.py
--------------------------
Business model — output of Research Agent.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Business(BaseModel):
    """A target business discovered by the Research Agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    country: str = "India"
    description: Optional[str] = None
    pain_points: list[str] = []
    niche: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)