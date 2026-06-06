"""
core/state.py
--------------
Shared LangGraph state passed between all pipeline nodes.
"""

from typing import TypedDict, Optional


class OutreachState(TypedDict):
    """Shared state for the LangGraph pipeline passed between nodes."""

    campaign_id: str                         # Unique campaign identifier
    niche: str                               # Target business niche
    location: str                            # Target geographic location
    businesses: list[dict]                   # ResearchAgent output
    contacts: list[dict]                     # ContactFinderAgent output
    emails_written: list[dict]               # EmailWriterAgent output
    emails_sent: list[dict]                  # Sender output
    errors: list[str]                        # Error accumulator
    current_step: str                        # Pipeline step tracker
    metadata: dict                           # Flexible extra info