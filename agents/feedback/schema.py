"""
agents/feedback/schema.py
--------------------------
Campaign model — tracks full campaign lifecycle.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class CampaignStatus(str, Enum):
    """Status values for a campaign's lifecycle."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class Campaign(BaseModel):
    """A complete campaign record with performance metrics."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    niche: str
    target_location: str
    status: CampaignStatus = CampaignStatus.DRAFT
    total_sent: int = 0
    total_opened: int = 0
    total_replied: int = 0
    total_bounced: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    config: dict = {}
    insights: list[str] = []           # AI-generated insights from feedback agent