"""
db/models.py
------------
SQLAlchemy 2.0 ORM models for Syntrase.

Defines the core schema: Campaign, NicheResearch, Business, Contact,
and EmailRecord. All tables use PostgreSQL-native UUID primary keys
and are designed for Supabase (PostgreSQL) exclusively.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


# ── Enum types ────────────────────────────────────────────────────────────────


class CampaignStatus(str, enum.Enum):
    """Status lifecycle for an outreach campaign."""

    draft = "draft"
    running = "running"
    paused = "paused"
    completed = "completed"


class ContactSource(str, enum.Enum):
    """How a contact email was discovered."""

    website = "website"
    guess = "guess"
    linkedin = "linkedin"
    manual = "manual"


class EmailStatus(str, enum.Enum):
    """Delivery / engagement status of a sent email."""

    pending = "pending"
    sent = "sent"
    opened = "opened"
    replied = "replied"
    bounced = "bounced"
    unsubscribed = "unsubscribed"


# ── Models ────────────────────────────────────────────────────────────────────


class Campaign(Base):
    """An outreach campaign targeting a specific niche and location."""

    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, index=True)
    niche: Mapped[str] = mapped_column(String, index=True)
    target_location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status", create_constraint=True),
        default=CampaignStatus.draft,
    )

    # Aggregate counters
    total_sent: Mapped[int] = mapped_column(default=0)
    total_opened: Mapped[int] = mapped_column(default=0)
    total_replied: Mapped[int] = mapped_column(default=0)
    total_bounced: Mapped[int] = mapped_column(default=0)

    # Flexible settings dict
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=None, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    businesses: Mapped[list["Business"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id!r}, name={self.name!r}, niche={self.niche!r})>"


class NicheResearch(Base):
    """Cached research data for a specific niche (pain points, gaps, etc.)."""

    __tablename__ = "niche_research"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    niche: Mapped[str] = mapped_column(String, unique=True, index=True)
    pain_points: Mapped[list] = mapped_column(JSON)
    software_gaps: Mapped[list] = mapped_column(JSON)
    decision_maker_role: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_research: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=None, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        nullable=True, onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<NicheResearch(id={self.id!r}, niche={self.niche!r})>"


class Business(Base):
    """A target business discovered during outreach research."""

    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), index=True
    )
    niche: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Timestamps
    scraped_at: Mapped[datetime] = mapped_column(
        default=None, server_default=func.now()
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="businesses")
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Business(id={self.id!r}, name={self.name!r}, niche={self.niche!r})>"


class Contact(Base):
    """An email contact associated with a target business."""

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), index=True
    )
    email: Mapped[str] = mapped_column(String, index=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    job_title: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[ContactSource] = mapped_column(
        Enum(ContactSource, name="contact_source", create_constraint=True),
        default=ContactSource.guess,
    )

    # Timestamps
    found_at: Mapped[datetime] = mapped_column(
        default=None, server_default=func.now()
    )

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="contacts")
    email_records: Mapped[list["EmailRecord"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Contact(id={self.id!r}, email={self.email!r})>"


class EmailRecord(Base):
    """A single outreach email — tracks content, delivery, and engagement."""

    __tablename__ = "email_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), index=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), index=True
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), index=True
    )

    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    variant: Mapped[str | None] = mapped_column(String, nullable=True)
    sender_account: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus, name="email_status", create_constraint=True),
        default=EmailStatus.pending,
        index=True,
    )

    # Engagement timestamps
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(nullable=True)
    bounced_at: Mapped[datetime | None] = mapped_column(nullable=True)

    open_count: Mapped[int] = mapped_column(default=0)

    # Relationships
    contact: Mapped["Contact"] = relationship(back_populates="email_records")

    # Composite index for fast feedback-loop queries
    __table_args__ = (
        Index("ix_email_records_campaign_status", "campaign_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<EmailRecord(id={self.id!r}, status={self.status!r})>"
