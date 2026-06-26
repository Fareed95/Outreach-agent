"""
agents/research/schema.py
--------------------------
Pydantic models for Research Agent I/O.
Maps to DB tables: niche_research, businesses.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


class NicheResearch(BaseModel):
    """Matches niche_research DB table."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: str
    pain_points: list[str] = []
    software_gaps: list[str] = []
    decision_maker_role: Optional[str] = None
    raw_research: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class Business(BaseModel):
    """Matches businesses DB table."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    niche: str
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    pain_points: list[str] = []
    source_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class NicheSuggestion(BaseModel):
    """AI-suggested niche with reasoning."""
    niche: str
    reasoning: str
    potential_pain_points: list[str] = []
    estimated_market_size: str = ""


class ResearchAgentInput(BaseModel):
    """Input to Research Agent."""
    campaign_id: str
    niche: str
    location: str
    target_count: int = 10  # businesses to find per niche


class ResearchAgentOutput(BaseModel):
    """Output from Research Agent."""
    niche_research: NicheResearch
    businesses: list[Business]
    search_queries_used: list[str] = []
    total_found: int = 0