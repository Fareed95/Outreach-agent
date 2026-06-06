"""
agents/email_writer/schema.py
------------------------------
EmailRecord model — output of Email Writer + Sender.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class EmailStatus(str, Enum):
    """Status values for an email record throughout its lifecycle."""

    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


class EmailRecord(BaseModel):
    """A complete email record with tracking information."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    business_id: str
    campaign_id: str
    subject: str
    body: str
    variant: str = "A"
    status: EmailStatus = EmailStatus.PENDING
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    open_count: int = 0
    tracking_pixel_id: Optional[str] = None