"""
agents/contact_finder/schema.py
--------------------------------
Contact model — output of Contact Finder Agent.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Contact(BaseModel):
    """An email contact found for a target business."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: str
    email_verified: bool = False
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: Optional[str] = None      # "website", "hunter.io", "manual"
    found_at: datetime = Field(default_factory=datetime.now)