"""initial_schema

Revision ID: ac3845289c10
Revises: 
Create Date: 2026-06-22 19:45:41.434834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ac3845289c10'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# All Syntrase tables — RLS policies use the `postgres` role (service role)
# since the backend connects as the database owner, not via Supabase auth.
# Anon/authenticated roles get explicit SELECT-only access.
SYNTRASE_TABLES = [
    'campaigns',
    'niche_research',
    'businesses',
    'contacts',
    'email_records',
]


def upgrade() -> None:
    """Create initial Syntrase schema — campaigns, niche_research,
    businesses, contacts, email_records — with RLS policies and indexes."""

    # ── Enum types ────────────────────────────────────────────────────────
    campaign_status = sa.Enum(
        'draft', 'running', 'paused', 'completed',
        name='campaign_status',
    )
    contact_source = sa.Enum(
        'website', 'guess', 'linkedin', 'manual',
        name='contact_source',
    )
    email_status = sa.Enum(
        'pending', 'sent', 'opened', 'replied', 'bounced', 'unsubscribed',
        name='email_status',
    )

    # ── campaigns ─────────────────────────────────────────────────────────
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('niche', sa.String(), nullable=False),
        sa.Column('target_location', sa.String(), nullable=True),
        sa.Column('status', campaign_status, nullable=False, server_default='draft'),
        sa.Column('total_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_opened', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_replied', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_bounced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_campaigns_name', 'campaigns', ['name'])
    op.create_index('ix_campaigns_niche', 'campaigns', ['niche'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    op.create_index('ix_campaigns_created_at', 'campaigns', ['created_at'])

    # ── niche_research ────────────────────────────────────────────────────
    op.create_table(
        'niche_research',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('niche', sa.String(), nullable=False, unique=True),
        sa.Column('pain_points', sa.JSON(), nullable=False),
        sa.Column('software_gaps', sa.JSON(), nullable=False),
        sa.Column('decision_maker_role', sa.String(), nullable=True),
        sa.Column('raw_research', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_niche_research_niche', 'niche_research', ['niche'], unique=True)

    # ── businesses ────────────────────────────────────────────────────────
    op.create_table(
        'businesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('niche', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pain_points', sa.JSON(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_businesses_campaign_id', 'businesses', ['campaign_id'])
    op.create_index('ix_businesses_niche', 'businesses', ['niche'])
    op.create_index('ix_businesses_name', 'businesses', ['name'])
    # Composite: find businesses in a campaign by niche
    op.create_index('ix_businesses_campaign_niche', 'businesses', ['campaign_id', 'niche'])

    # ── contacts ──────────────────────────────────────────────────────────
    op.create_table(
        'contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('source', contact_source, nullable=False, server_default='guess'),
        sa.Column('found_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_contacts_business_id', 'contacts', ['business_id'])
    op.create_index('ix_contacts_email', 'contacts', ['email'])
    # Composite: check for verified contacts per business
    op.create_index('ix_contacts_business_verified', 'contacts', ['business_id', 'email_verified'])

    # ── email_records ─────────────────────────────────────────────────────
    op.create_table(
        'email_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contacts.id'), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('variant', sa.String(), nullable=True),
        sa.Column('sender_account', sa.String(), nullable=True),
        sa.Column('status', email_status, nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bounced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_email_records_contact_id', 'email_records', ['contact_id'])
    op.create_index('ix_email_records_business_id', 'email_records', ['business_id'])
    op.create_index('ix_email_records_campaign_id', 'email_records', ['campaign_id'])
    op.create_index('ix_email_records_status', 'email_records', ['status'])
    # Composite: feedback-loop queries (campaign analytics by status)
    op.create_index('ix_email_records_campaign_status', 'email_records', ['campaign_id', 'status'])
    # Composite: time-based send tracking per campaign
    op.create_index('ix_email_records_campaign_sent', 'email_records', ['campaign_id', 'sent_at'])
    # Composite: variant performance comparison
    op.create_index('ix_email_records_campaign_variant', 'email_records', ['campaign_id', 'variant'])

    # ── RLS Policies ──────────────────────────────────────────────────────
    # Syntrase uses the `postgres` role (Supabase service_role key) from the
    # backend — so the owner role has full access by default. RLS is enabled
    # to lock down anon/authenticated Supabase clients from directly
    # reading/writing these tables. The backend bypasses RLS via the service
    # role connection.
    #
    # Policy strategy:
    #   - Enable RLS on all tables
    #   - GRANT SELECT to `authenticated` role (read-only dashboard access)
    #   - No INSERT/UPDATE/DELETE for authenticated — only the service backend
    #   - anon gets zero access
    conn = op.get_bind()

    for table in SYNTRASE_TABLES:
        # Enable RLS
        conn.execute(sa.text(
            f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY'
        ))

        # Force RLS even for table owner (the postgres role) — optional but
        # recommended for defense-in-depth. Comment out if your backend needs
        # to bypass RLS entirely via the postgres role.
        # conn.execute(sa.text(
        #     f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY'
        # ))

        # Policy: service_role (postgres) has full access — this is implicit
        # since the owner bypasses RLS, but we add an explicit policy for
        # clarity when FORCE is enabled.
        conn.execute(sa.text(
            f'CREATE POLICY "service_role_full_access" ON {table} '
            f'FOR ALL '
            f'TO postgres '
            f'USING (true) '
            f'WITH CHECK (true)'
        ))

        # Policy: authenticated users get read-only access (for dashboard)
        conn.execute(sa.text(
            f'CREATE POLICY "authenticated_read_only" ON {table} '
            f'FOR SELECT '
            f'TO authenticated '
            f'USING (true)'
        ))

        # Revoke all default privileges from anon
        conn.execute(sa.text(
            f'REVOKE ALL ON {table} FROM anon'
        ))

        # Grant SELECT to authenticated
        conn.execute(sa.text(
            f'GRANT SELECT ON {table} TO authenticated'
        ))


def downgrade() -> None:
    """Drop all Syntrase tables, RLS policies, and enum types."""
    conn = op.get_bind()

    # Drop RLS policies before dropping tables
    for table in reversed(SYNTRASE_TABLES):
        conn.execute(sa.text(
            f'DROP POLICY IF EXISTS "service_role_full_access" ON {table}'
        ))
        conn.execute(sa.text(
            f'DROP POLICY IF EXISTS "authenticated_read_only" ON {table}'
        ))

    op.drop_table('email_records')
    op.drop_table('contacts')
    op.drop_table('businesses')
    op.drop_table('niche_research')
    op.drop_table('campaigns')

    # Drop enum types
    sa.Enum(name='email_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='contact_source').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='campaign_status').drop(op.get_bind(), checkfirst=True)
