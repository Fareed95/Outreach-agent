# Syntrase — Database Documentation

> PostgreSQL on Supabase · SQLAlchemy 2.0 (async) · Alembic migrations
> All tables live in the `public` schema with RLS enabled.

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    campaigns ||--o{ businesses : "has many"
    businesses ||--o{ contacts : "has many"
    contacts ||--o{ email_records : "has many"
    businesses ||--o{ email_records : "linked"
    campaigns ||--o{ email_records : "linked"

    campaigns {
        UUID id PK
        VARCHAR name
        VARCHAR niche
        VARCHAR target_location
        campaign_status status
        INT total_sent
        INT total_opened
        INT total_replied
        INT total_bounced
        JSON config
        TIMESTAMPTZ created_at
        TIMESTAMPTZ started_at
        TIMESTAMPTZ completed_at
    }

    niche_research {
        UUID id PK
        VARCHAR niche UK
        JSON pain_points
        JSON software_gaps
        VARCHAR decision_maker_role
        TEXT raw_research
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    businesses {
        UUID id PK
        UUID campaign_id FK
        VARCHAR niche
        VARCHAR name
        VARCHAR website
        VARCHAR industry
        VARCHAR location
        VARCHAR city
        TEXT description
        JSON pain_points
        VARCHAR source_url
        TIMESTAMPTZ scraped_at
    }

    contacts {
        UUID id PK
        UUID business_id FK
        VARCHAR email
        BOOLEAN email_verified
        VARCHAR full_name
        VARCHAR job_title
        contact_source source
        TIMESTAMPTZ found_at
    }

    email_records {
        UUID id PK
        UUID contact_id FK
        UUID business_id FK
        UUID campaign_id FK
        VARCHAR subject
        TEXT body
        VARCHAR variant
        VARCHAR sender_account
        email_status status
        TIMESTAMPTZ sent_at
        TIMESTAMPTZ opened_at
        TIMESTAMPTZ replied_at
        TIMESTAMPTZ bounced_at
        INT open_count
    }
```

---

## Tables

### 1. `campaigns`

The top-level entity. Each campaign targets a specific niche + location and tracks aggregate email performance.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | ✗ | `uuid_generate_v4()` | Primary key |
| `name` | `VARCHAR` | ✗ | — | Human-readable campaign name |
| `niche` | `VARCHAR` | ✗ | — | Target business niche (e.g. "CA firms") |
| `target_location` | `VARCHAR` | ✓ | `NULL` | Geographic target (e.g. "Mumbai, India") |
| `status` | `campaign_status` | ✗ | `'draft'` | Lifecycle state |
| `total_sent` | `INTEGER` | ✗ | `0` | Emails sent counter |
| `total_opened` | `INTEGER` | ✗ | `0` | Emails opened counter |
| `total_replied` | `INTEGER` | ✗ | `0` | Replies received counter |
| `total_bounced` | `INTEGER` | ✗ | `0` | Bounced emails counter |
| `config` | `JSON` | ✓ | `NULL` | Flexible settings dict |
| `created_at` | `TIMESTAMPTZ` | ✗ | `now()` | Campaign creation time |
| `started_at` | `TIMESTAMPTZ` | ✓ | `NULL` | When campaign was started |
| `completed_at` | `TIMESTAMPTZ` | ✓ | `NULL` | When campaign finished |

**Relationships:**
- `campaigns` → `businesses` (one-to-many, cascade delete)

---

### 2. `niche_research`

Cached research data per niche. Prevents redundant LLM/Serper calls — same niche = reuse research.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | ✗ | `uuid_generate_v4()` | Primary key |
| `niche` | `VARCHAR` | ✗ | — | Niche name (**unique**) |
| `pain_points` | `JSON` | ✗ | — | List of identified pain points |
| `software_gaps` | `JSON` | ✗ | — | Software/tool gaps in the niche |
| `decision_maker_role` | `VARCHAR` | ✓ | `NULL` | Who to target (e.g. "Managing Partner") |
| `raw_research` | `TEXT` | ✓ | `NULL` | Full raw research text from LLM |
| `created_at` | `TIMESTAMPTZ` | ✗ | `now()` | When research was done |
| `updated_at` | `TIMESTAMPTZ` | ✓ | `NULL` | Auto-updated on modification |

**Standalone table** — not linked to campaigns (shared cache across campaigns).

---

### 3. `businesses`

Target businesses discovered by the Research Agent for a specific campaign.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | ✗ | `uuid_generate_v4()` | Primary key |
| `campaign_id` | `UUID` | ✗ | — | FK → `campaigns.id` |
| `niche` | `VARCHAR` | ✗ | — | Business niche category |
| `name` | `VARCHAR` | ✗ | — | Business name |
| `website` | `VARCHAR` | ✓ | `NULL` | Business website URL |
| `industry` | `VARCHAR` | ✓ | `NULL` | Industry classification |
| `location` | `VARCHAR` | ✓ | `NULL` | Full location string |
| `city` | `VARCHAR` | ✓ | `NULL` | City name |
| `description` | `TEXT` | ✓ | `NULL` | Business description |
| `pain_points` | `JSON` | ✓ | `NULL` | Business-specific pain points |
| `source_url` | `VARCHAR` | ✓ | `NULL` | Where the business was found |
| `scraped_at` | `TIMESTAMPTZ` | ✗ | `now()` | When business was scraped |

**Relationships:**
- `businesses` → `campaign` (many-to-one)
- `businesses` → `contacts` (one-to-many, cascade delete)

---

### 4. `contacts`

Email contacts extracted from businesses by the Contact Finder Agent.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | ✗ | `uuid_generate_v4()` | Primary key |
| `business_id` | `UUID` | ✗ | — | FK → `businesses.id` |
| `email` | `VARCHAR` | ✗ | — | Contact email address |
| `email_verified` | `BOOLEAN` | ✗ | `false` | ZeroBounce verification status |
| `full_name` | `VARCHAR` | ✓ | `NULL` | Contact's full name |
| `job_title` | `VARCHAR` | ✓ | `NULL` | Contact's job title |
| `source` | `contact_source` | ✗ | `'guess'` | How the email was discovered |
| `found_at` | `TIMESTAMPTZ` | ✗ | `now()` | When contact was found |

**Relationships:**
- `contacts` → `business` (many-to-one)
- `contacts` → `email_records` (one-to-many, cascade delete)

---

### 5. `email_records`

Individual outreach emails — tracks content, delivery status, and engagement metrics.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | ✗ | `uuid_generate_v4()` | Primary key |
| `contact_id` | `UUID` | ✗ | — | FK → `contacts.id` |
| `business_id` | `UUID` | ✗ | — | FK → `businesses.id` |
| `campaign_id` | `UUID` | ✗ | — | FK → `campaigns.id` |
| `subject` | `VARCHAR` | ✗ | — | Email subject line |
| `body` | `TEXT` | ✗ | — | Email body content |
| `variant` | `VARCHAR` | ✓ | `NULL` | A/B test variant label (e.g. "A", "B") |
| `sender_account` | `VARCHAR` | ✓ | `NULL` | Gmail account used to send |
| `status` | `email_status` | ✗ | `'pending'` | Delivery/engagement state |
| `sent_at` | `TIMESTAMPTZ` | ✓ | `NULL` | When email was sent |
| `opened_at` | `TIMESTAMPTZ` | ✓ | `NULL` | First open timestamp |
| `replied_at` | `TIMESTAMPTZ` | ✓ | `NULL` | Reply received timestamp |
| `bounced_at` | `TIMESTAMPTZ` | ✓ | `NULL` | Bounce detected timestamp |
| `open_count` | `INTEGER` | ✗ | `0` | Total open count (tracking pixel) |

**Relationships:**
- `email_records` → `contact` (many-to-one)

---

## Enum Types

### `campaign_status`

```
draft → running → paused → completed
```

| Value | Description |
|---|---|
| `draft` | Campaign created but not yet started |
| `running` | Actively sending emails |
| `paused` | Temporarily stopped |
| `completed` | All emails sent, campaign finished |

### `contact_source`

| Value | Description |
|---|---|
| `website` | Extracted from business website (mailto, contact page) |
| `guess` | Generated via domain pattern guessing (info@, contact@) |
| `linkedin` | Found via LinkedIn profile |
| `manual` | Manually added by user |

### `email_status`

```
pending → sent → opened → replied
                → bounced
                → unsubscribed
```

| Value | Description |
|---|---|
| `pending` | Written but not yet sent |
| `sent` | Successfully delivered via SMTP |
| `opened` | Tracking pixel fired (email was opened) |
| `replied` | Recipient replied (detected via IMAP) |
| `bounced` | Email bounced (invalid address, full inbox) |
| `unsubscribed` | Recipient clicked unsubscribe link |

---

## Indexes

### Single-Column Indexes

| Table | Index Name | Column(s) | Type |
|---|---|---|---|
| `campaigns` | `ix_campaigns_name` | `name` | B-tree |
| `campaigns` | `ix_campaigns_niche` | `niche` | B-tree |
| `campaigns` | `ix_campaigns_status` | `status` | B-tree |
| `campaigns` | `ix_campaigns_created_at` | `created_at` | B-tree |
| `niche_research` | `ix_niche_research_niche` | `niche` | B-tree, **unique** |
| `businesses` | `ix_businesses_campaign_id` | `campaign_id` | B-tree |
| `businesses` | `ix_businesses_niche` | `niche` | B-tree |
| `businesses` | `ix_businesses_name` | `name` | B-tree |
| `contacts` | `ix_contacts_business_id` | `business_id` | B-tree |
| `contacts` | `ix_contacts_email` | `email` | B-tree |
| `email_records` | `ix_email_records_contact_id` | `contact_id` | B-tree |
| `email_records` | `ix_email_records_business_id` | `business_id` | B-tree |
| `email_records` | `ix_email_records_campaign_id` | `campaign_id` | B-tree |
| `email_records` | `ix_email_records_status` | `status` | B-tree |

### Composite Indexes

| Table | Index Name | Columns | Purpose |
|---|---|---|---|
| `businesses` | `ix_businesses_campaign_niche` | `(campaign_id, niche)` | Filter businesses by campaign + niche |
| `contacts` | `ix_contacts_business_verified` | `(business_id, email_verified)` | Find verified contacts per business |
| `email_records` | `ix_email_records_campaign_status` | `(campaign_id, status)` | **Feedback loop** — campaign analytics by status |
| `email_records` | `ix_email_records_campaign_sent` | `(campaign_id, sent_at)` | Time-based send tracking per campaign |
| `email_records` | `ix_email_records_campaign_variant` | `(campaign_id, variant)` | A/B variant performance comparison |

**Total: 19 custom indexes** (plus auto-created PK indexes).

---

## Row Level Security (RLS)

RLS is enabled on all 5 tables. The backend connects via the Supabase **service role** (`postgres` user), which has full CRUD access. Frontend/dashboard clients use the `authenticated` role with read-only access.

### Policy Summary

| Policy Name | Tables | Role | Operations | Condition |
|---|---|---|---|---|
| `service_role_full_access` | All 5 tables | `postgres` | ALL (SELECT, INSERT, UPDATE, DELETE) | `USING (true) WITH CHECK (true)` |
| `authenticated_read_only` | All 5 tables | `authenticated` | SELECT only | `USING (true)` |

### Access Matrix

| Role | SELECT | INSERT | UPDATE | DELETE |
|---|---|---|---|---|
| `postgres` (service role) | ✅ | ✅ | ✅ | ✅ |
| `authenticated` | ✅ | ✗ | ✗ | ✗ |
| `anon` | ✗ | ✗ | ✗ | ✗ |

### Why This Design?

- **Backend (Python/SQLAlchemy)** connects with the `postgres` role via the service role key — full access, bypasses RLS by default.
- **Supabase JS client** (future dashboard) would use `authenticated` role — can read data for analytics but cannot modify it.
- **Anonymous access** is fully revoked — no public API exposure.

---

## Foreign Key Relationships

```
campaigns.id
  ├── businesses.campaign_id
  └── email_records.campaign_id

businesses.id
  ├── contacts.business_id
  └── email_records.business_id

contacts.id
  └── email_records.contact_id
```

### Cascade Rules

| Parent | Child | On Delete |
|---|---|---|
| `campaigns` | `businesses` | CASCADE (delete-orphan) |
| `businesses` | `contacts` | CASCADE (delete-orphan) |
| `contacts` | `email_records` | CASCADE (delete-orphan) |

Deleting a campaign removes all its businesses → contacts → email records.

---

## Connection Setup

### Two Connection Strings

Syntrase uses two separate Supabase connection strings:

| Variable | Purpose | Port | Driver | Used By |
|---|---|---|---|---|
| `DATABASE_URL` | App runtime queries | 6543 (pooler) | `postgresql+asyncpg://` | SQLAlchemy async engine |
| `DATABASE_URL_MIGRATIONS` | Schema migrations (DDL) | 6543 (pooler) | `postgresql://` → auto-converted to `postgresql+asyncpg://` | Alembic |

### Connection Pool Settings

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,       # 10 persistent connections
    max_overflow=20,    # Up to 30 total under load
    pool_pre_ping=True, # Validate connections before use
)
```

### Important: Password Encoding

If your Supabase password contains special characters (like `@`), URL-encode them:

```
@ → %40
# → %23
: → %3A
```

Example:
```
# Wrong — @ breaks URL parsing
postgresql://user:Pass@123@host:5432/db

# Correct — @ encoded as %40
postgresql://user:Pass%40123@host:5432/db
```

---

## Alembic Migrations

### Directory Structure

```
migrations/
├── env.py              # Async migration environment (reads .env)
├── script.py.mako      # Migration template
├── README
└── versions/
    └── 20260622_1945_ac3845289c10_initial_schema.py
```

### Common Commands

```bash
# Apply all pending migrations
make migrate

# Create a new migration (auto-detects model changes)
make migrate-new name="add_tracking_pixel_id"

# Rollback the last migration
make migrate-down

# Show migration history
make migrate-history
```

### How env.py Works

1. Loads `.env` via `python-dotenv`
2. Reads `DATABASE_URL_MIGRATIONS` directly from `os.environ` (avoids loading the full `Settings` class which requires all API keys)
3. Converts `postgresql://` → `postgresql+asyncpg://` for the async engine
4. Escapes `%` characters for ConfigParser compatibility
5. Imports `Base` and all models from `db.models` for autogenerate detection

---

## Key Files

| File | Purpose |
|---|---|
| [db/base.py](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/db/base.py) | SQLAlchemy `DeclarativeBase` — all models inherit from this |
| [db/models.py](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/db/models.py) | 5 ORM models + 3 enum types |
| [db/database.py](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/db/database.py) | Async engine, session maker, health check |
| [migrations/env.py](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/migrations/env.py) | Alembic async environment |
| [alembic.ini](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/alembic.ini) | Alembic configuration |
| [.env](file:///home/fareed-sayed/Documents/Crodlin/crodlin-outreach-agent/.env.example) | Connection strings (see `.env.example`) |

---

## Common Queries

### Get campaign analytics
```sql
SELECT
    campaign_id,
    status,
    COUNT(*) as count
FROM email_records
WHERE campaign_id = '<uuid>'
GROUP BY campaign_id, status;
-- Uses: ix_email_records_campaign_status
```

### Find verified contacts for a business
```sql
SELECT * FROM contacts
WHERE business_id = '<uuid>' AND email_verified = true;
-- Uses: ix_contacts_business_verified
```

### A/B variant performance
```sql
SELECT
    variant,
    COUNT(*) FILTER (WHERE status = 'sent') as sent,
    COUNT(*) FILTER (WHERE status = 'opened') as opened,
    COUNT(*) FILTER (WHERE status = 'replied') as replied
FROM email_records
WHERE campaign_id = '<uuid>'
GROUP BY variant;
-- Uses: ix_email_records_campaign_variant
```

### Campaign send timeline
```sql
SELECT
    DATE(sent_at) as send_date,
    COUNT(*) as emails_sent
FROM email_records
WHERE campaign_id = '<uuid>' AND sent_at IS NOT NULL
GROUP BY DATE(sent_at)
ORDER BY send_date;
-- Uses: ix_email_records_campaign_sent
```

### Niche research cache lookup
```sql
SELECT * FROM niche_research WHERE niche = 'CA firms';
-- Uses: ix_niche_research_niche (unique)
```

---

*Schema version: `ac3845289c10` (initial_schema) · Applied: 2026-06-22*
