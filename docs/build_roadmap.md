# Syntrase — Build Roadmap & Phase Checklist

> Phase 1 → Working system (use internally for Syntrase)
> Phase 2 → Product (others can use it — cloud + frontend)
> Phase 3 → Scale (monetization, community, enterprise)

---

## Tools Master List

| Tool | Purpose | Cost | Phase |
|---|---|---|---|
| **UV** | Package manager | Free | All |
| **Python 3.11** | Runtime | Free | All |
| **LangGraph** | Agent orchestration | Free | All |
| **OpenRouter** | LLM API (Gemini Flash) | ~$5-10/mo | All |
| **Ollama** | Local LLM (optional) | Free | All |
| **Serper.dev** | Google Search API | $10/mo | All |
| **Crawl4AI** | Website scraping | Free | All |
| **aiosmtplib** | SMTP email sending | Free | Phase 1 |
| **ZeroBounce** | Email verification | Free tier | All |
| **PostgreSQL** | Database | Free | All |
| **SQLAlchemy** | ORM (async) | Free | All |
| **Alembic** | DB migrations | Free | All |
| **Pydantic** | Data validation + config | Free | All |
| **Loguru** | Logging | Free | All |
| **Tenacity** | Retry logic | Free | All |
| **FastAPI** | Backend API | Free | Phase 2 |
| **Next.js** | Frontend | Free | Phase 2 |
| **Tailwind CSS** | Styling | Free | Phase 2 |
| **Docker + Compose** | Containerization | Free | Phase 1 |
| **Cron** | Scheduling | Free | Phase 1 |
| **Amazon SES** | Scale email sending | ₹1200/mo | Phase 2 |
| **Instantly.ai** | Managed sending (optional) | ₹3100/mo | Phase 2 |
| **Listmonk** | Campaign manager (optional) | Free | Phase 2 |
| **Railway / Render** | Cloud hosting | ~₹800/mo | Phase 2 |
| **Supabase** | Managed PostgreSQL (optional) | Free tier | Phase 2 |
| **pytest** | Testing | Free | All |
| **Ruff** | Linting | Free | All |
| **GitHub Actions** | CI/CD | Free | Phase 2 |

---

---

# PHASE 1 — Core Working System

**Goal:** Build a fully working CLI-based outreach agent.
Use it internally for Syntrase. Validate everything works.

**Timeline:** 6-8 weeks
**Daily effort:** 2-3 hours
**End state:** Run `uv run main.py --mode outreach --niche "CA firms" --location "Mumbai"` and get emails sent.

---

## Week 1 — Project Setup & Database

### Project Scaffold
- [ ] Run Cline scaffold prompt — generate all files
- [ ] `uv init` — initialize UV project
- [ ] `uv sync` — install all dependencies
- [ ] Verify folder structure is correct
- [ ] `.env` file create karo from `.env.example`
- [ ] Fill in API keys (OpenRouter, Serper)

**Tools:** UV, Python 3.11, Cline (free model)

---

### Config & Settings
- [ ] `config/settings.py` verify karo — Pydantic BaseSettings
- [ ] All env vars load ho rahe hain test karo
- [ ] `settings.DATABASE_URL` test karo

**Tools:** Pydantic, python-dotenv

---

### Database Setup
- [ ] `docker compose up postgres` — PostgreSQL start karo
- [ ] `db/database.py` — async engine setup
- [ ] `db/models.py` — SQLAlchemy table models:
  - [ ] Campaign model
  - [ ] Business model
  - [ ] Contact model
  - [ ] EmailRecord model
  - [ ] NicheResearchCache model
  - [ ] FeedbackReport model
- [ ] `alembic init migrations` — Alembic initialize karo
- [ ] `alembic revision --autogenerate -m "initial_tables"` — migration banao
- [ ] `alembic upgrade head` — tables create karo
- [ ] Verify tables in PostgreSQL (`\dt` command)

**Tools:** PostgreSQL, SQLAlchemy, Alembic, Docker

---

### Logger + Retry Setup
- [ ] `utils/logger.py` — Loguru setup verify karo
- [ ] `utils/retry.py` — Tenacity decorator verify karo
- [ ] `utils/helpers.py` — UUID generator, date utils add karo
- [ ] Test logger output in console + file

**Tools:** Loguru, Tenacity

---

## Week 2 — Niche Research Agent

**Goal:** Input `"CA firms"` → Output `pain_points.json`

### Niche Research Agent
- [ ] `agents/research/schema.py` — NicheResearch Pydantic model
- [ ] `agents/research/prompts.py` — Research prompts likhna:
  - [ ] Niche pain point extraction prompt
  - [ ] Software gap analysis prompt
  - [ ] Decision maker identification prompt
- [ ] `agents/research/agent.py` — NicheResearchAgent class:
  - [ ] OpenRouter client initialize karo
  - [ ] `research_niche(niche: str)` method
  - [ ] Serper.dev se Google search karo — `"{niche} problems challenges 2025"`
  - [ ] Multiple queries run karo (3-5 different angles)
  - [ ] LLM se pain points extract karo
  - [ ] Result DB mein cache karo (NicheResearchCache table)
  - [ ] Cache hit check karo — same niche dobara research na kare
- [ ] Test karo:
  - [ ] `"CA firms"` → valid pain points JSON
  - [ ] `"Clinics Mumbai"` → different pain points
  - [ ] Cache test — second run should hit DB, not API

**Tools:** LangGraph, OpenRouter (Gemini Flash), Serper.dev, SQLAlchemy

---

### Serper Integration
- [ ] `utils/serper.py` — Serper API wrapper class:
  - [ ] `search(query: str, num: int)` method
  - [ ] `maps_search(query: str, location: str)` method
  - [ ] Rate limiting (avoid hitting API limits)
  - [ ] Error handling + retry
- [ ] Test with sample queries

**Tools:** httpx, Serper.dev API, Tenacity

---

## Week 3 — Business Finder Agent

**Goal:** Input `"CA firms, Mumbai"` → Output list of businesses with websites

### Business Finder Agent
- [ ] `agents/research/business_finder.py`:
  - [ ] `find_businesses(niche: str, location: str, count: int)` method
  - [ ] Serper Google Search — `"CA firms Mumbai"` + variations
  - [ ] Serper Maps Search — local businesses
  - [ ] JustDial scraping via Crawl4AI — `"justdial.com/Mumbai/CA-firms"`
  - [ ] Deduplication — same business naam se filter
  - [ ] Business data extract: name, website, description, location
  - [ ] Save to DB — businesses table
- [ ] Test karo:
  - [ ] 50 businesses find karo "CA firms Mumbai"
  - [ ] Verify websites are valid URLs
  - [ ] Duplicates check karo

**Tools:** Crawl4AI, Serper.dev, SQLAlchemy, httpx

---

### Crawl4AI Setup
- [ ] `uv add crawl4ai` — install
- [ ] `crawl4ai-setup` — playwright install
- [ ] `utils/crawler.py` — Crawl4AI wrapper:
  - [ ] `crawl_url(url: str)` — single URL crawl
  - [ ] `extract_emails(content: str)` — regex email extraction
  - [ ] `extract_contact_page(url: str)` — /contact page finder
  - [ ] Timeout handling
  - [ ] JS-heavy site support

**Tools:** Crawl4AI, Playwright, regex

---

## Week 4 — Email Finder Agent

**Goal:** Input business website → Output verified email

### Email Finder Agent
- [ ] `agents/contact_finder/agent.py` — ContactFinderAgent:
  - [ ] `find_email(business: Business)` method
  - [ ] Waterfall approach:
    - [ ] Step 1: Crawl4AI website scrape → extract emails
    - [ ] Step 2: Try `/contact`, `/about`, `/team` pages
    - [ ] Step 3: Regex on full page HTML
    - [ ] Step 4: Generate guesses (info@, contact@, hello@)
    - [ ] Step 5: ZeroBounce verify all candidates
    - [ ] Step 6: Return highest confidence email
  - [ ] Save verified contacts to DB
- [ ] `agents/contact_finder/schema.py` — Contact model
- [ ] `agents/contact_finder/prompts.py` — Email extraction prompts

**Tools:** Crawl4AI, ZeroBounce API, regex, SQLAlchemy

---

### ZeroBounce Integration
- [ ] `utils/zerobounce.py` — ZeroBounce API wrapper:
  - [ ] `verify_email(email: str)` — single verify
  - [ ] `bulk_verify(emails: list[str])` — batch verify
  - [ ] Parse response — valid / invalid / catch-all / unknown
  - [ ] Free tier tracking (100/month)
- [ ] Test with known valid + invalid emails

**Tools:** httpx, ZeroBounce API

---

## Week 5 — Email Writer Agent

**Goal:** Business info + pain points → Personalized email

### Email Writer Agent
- [ ] `agents/email_writer/prompts.py` — All email prompts:
  - [ ] Service pitch prompt (B2B)
  - [ ] Job application prompt (B2C)
  - [ ] Freelance pitch prompt (B2C)
  - [ ] Follow-up email prompts (3 follow-ups)
  - [ ] Subject line generation prompt
- [ ] `agents/email_writer/agent.py` — EmailWriterAgent:
  - [ ] `write_email(business, contact, niche_research, user_config)` method
  - [ ] Email type routing (service / job / freelance)
  - [ ] Pain point injection from niche_research
  - [ ] Business-specific personalization
  - [ ] A/B subject line generation (2 variants)
  - [ ] Follow-up sequence generation (3 emails)
  - [ ] Save EmailRecord to DB (status: pending)
- [ ] `agents/email_writer/schema.py` — EmailRecord, EmailType models
- [ ] Quality check:
  - [ ] Email length reasonable (150-300 words)
  - [ ] Business name appears correctly
  - [ ] Pain point relevant to niche
  - [ ] CTA clear

**Tools:** OpenRouter (Gemini Flash), LangGraph, SQLAlchemy

---

## Week 6 — Sender Module + Tracking

**Goal:** Send emails, track opens and replies

### Sender Module
- [ ] `modules/sender.py` — SenderModule:
  - [ ] `load_email_accounts()` — parse EMAIL_ACCOUNTS from env
  - [ ] `rotate_account()` — pick next available account
  - [ ] `check_daily_limit(account)` — skip if limit reached
  - [ ] `send_email(record: EmailRecord, account)` — aiosmtplib send
  - [ ] `inject_tracking_pixel(body, pixel_id)` — add open tracker
  - [ ] `wrap_links(body, record_id)` — click tracking
  - [ ] `randomize_delay()` — human-like send intervals
  - [ ] Update EmailRecord status in DB after send
  - [ ] Error handling — bounce, auth failure, rate limit
- [ ] Warmup scheduler:
  - [ ] `modules/warmup.py` — inter-account email exchange
  - [ ] Cron: run warmup daily 7 AM

**Tools:** aiosmtplib, SQLAlchemy, asyncio

---

### Tracking Module
- [ ] `modules/tracker.py`:
  - [ ] Open tracking:
    - [ ] Generate unique pixel_id per email
    - [ ] 1x1 pixel URL: `{TRACKING_BASE_URL}/px/{pixel_id}`
    - [ ] FastAPI endpoint to serve pixel + log open event
  - [ ] Reply tracking:
    - [ ] `check_replies()` — IMAP polling every 30 min
    - [ ] Match reply to original EmailRecord
    - [ ] Update status: replied in DB
  - [ ] Bounce handling:
    - [ ] Parse SMTP error codes
    - [ ] Update status: bounced in DB
    - [ ] Mark contact as invalid
- [ ] `modules/tracker_server.py` — FastAPI mini server for pixel endpoint

**Tools:** FastAPI, imaplib, aiosmtplib, SQLAlchemy

---

## Week 7 — LangGraph Pipeline + Campaign Manager

**Goal:** Wire all agents into one pipeline

### Master Pipeline
- [ ] `core/state.py` — OutreachState TypedDict finalize karo
- [ ] `core/pipeline.py` — LangGraph graph:
  - [ ] `research_node` — niche research
  - [ ] `business_finder_node` — find businesses
  - [ ] `email_finder_node` — find contacts (parallel per business)
  - [ ] `email_writer_node` — write emails (parallel per contact)
  - [ ] `sender_node` — send emails with rate limiting
  - [ ] Conditional edges:
    - [ ] Error threshold → stop pipeline
    - [ ] No contacts found → skip niche
  - [ ] State persistence via DB checkpointing
- [ ] `core/campaign_manager.py`:
  - [ ] `create_campaign(config)` — new campaign in DB
  - [ ] `cluster_by_niche(emails)` — group by niche
  - [ ] `get_campaign_stats(campaign_id)` — analytics query
  - [ ] `pause_campaign(id)` / `resume_campaign(id)`

**Tools:** LangGraph, SQLAlchemy, asyncio

---

### Main Entry Point
- [ ] `main.py` — finalize argparse:
  - [ ] `--mode outreach` — full pipeline
  - [ ] `--mode feedback` — feedback agent only
  - [ ] `--mode warmup` — warmup script only
  - [ ] `--niche` — target niche
  - [ ] `--location` — target location
  - [ ] `--type` — service / job / freelance
  - [ ] `--about` — your description
  - [ ] `--count` — how many businesses to target

**Tools:** argparse, asyncio

---

## Week 8 — Feedback Agent + Testing + Docker Polish

### Feedback Agent
- [ ] `agents/feedback/prompts.py` — Analysis prompts:
  - [ ] Niche performance analysis prompt
  - [ ] Template improvement prompt
  - [ ] Next round recommendation prompt
- [ ] `agents/feedback/agent.py` — FeedbackAgent:
  - [ ] `analyze_campaign(campaign_id)` — pull stats from DB
  - [ ] Per-niche breakdown:
    - [ ] Open rate ranking
    - [ ] Reply rate ranking
    - [ ] Best subject lines
    - [ ] Best email variants
  - [ ] LLM insights generation
  - [ ] Next round config recommendation
  - [ ] Save FeedbackReport to DB
- [ ] `pipelines/feedback_pipeline.py` — LangGraph feedback graph

**Tools:** LangGraph, OpenRouter, SQLAlchemy

---

### Testing
- [ ] `tests/test_research_agent.py`:
  - [ ] Niche research returns valid pain points
  - [ ] Cache hit works correctly
- [ ] `tests/test_email_writer.py`:
  - [ ] Email generated for valid business input
  - [ ] Subject lines generated (2 variants)
  - [ ] Email length within range
- [ ] `tests/test_sender.py`:
  - [ ] Account rotation works
  - [ ] Daily limit respected
  - [ ] Tracking pixel injected correctly
- [ ] `tests/test_contact_finder.py`:
  - [ ] Email extracted from test website
  - [ ] ZeroBounce verify called correctly

**Tools:** pytest, pytest-asyncio

---

### Docker + Cron Polish
- [ ] `docker/docker-compose.yml` — finalize:
  - [ ] Agent service
  - [ ] PostgreSQL service
  - [ ] Tracker FastAPI service (for pixel endpoint)
  - [ ] Volume mounts — data, logs, postgres_data
  - [ ] Health checks
- [ ] `docker/cron/crontab` — verify schedules:
  - [ ] 9 AM IST — outreach run
  - [ ] 7 AM IST — warmup run
  - [ ] 6 PM IST — reply check
  - [ ] Sunday midnight — weekly feedback
- [ ] End-to-end test:
  - [ ] `docker compose up`
  - [ ] `uv run main.py --mode outreach --niche "CA firms" --location "Mumbai" --type service --about "We build custom software"`
  - [ ] Verify emails in DB
  - [ ] Verify tracking pixel works
  - [ ] Verify feedback agent runs

**Tools:** Docker, Docker Compose, Cron

---

### Phase 1 Done Checklist
- [ ] Niche research working → pain_points in DB
- [ ] 50 businesses found per niche
- [ ] Email finding → 30-40% hit rate
- [ ] Personalized emails generated
- [ ] Emails sent via Gmail SMTP
- [ ] Open tracking working (pixel)
- [ ] Reply tracking working (IMAP)
- [ ] Feedback agent producing insights
- [ ] Everything runs via Docker
- [ ] Cron scheduled correctly
- [ ] Used internally for Syntrase — first campaign sent

**Phase 1 cost:** ~$15-20/month (Serper + OpenRouter)

---
---

# PHASE 2 — Product (Others Can Use It)

**Goal:** Build frontend dashboard + cloud option + pluggable sender/model.
**Timeline:** 8-10 weeks
**Daily effort:** 3-4 hours
**End state:** Anyone can sign up, use cloud version OR self-host with Docker.

---

## Week 9-10 — FastAPI Backend

### REST API
- [ ] `api/main.py` — FastAPI app setup
- [ ] `api/routes/` — API routes:
  - [ ] `campaigns.py` — CRUD campaigns
  - [ ] `analytics.py` — stats endpoints
  - [ ] `settings.py` — user settings CRUD
  - [ ] `pipeline.py` — trigger agent runs
  - [ ] `tracking.py` — pixel + webhook endpoints
- [ ] `api/auth/` — Authentication:
  - [ ] JWT based auth
  - [ ] User registration + login
  - [ ] API key generation (for self-hosted)
- [ ] `api/schemas/` — Request/Response Pydantic models
- [ ] CORS setup for Next.js frontend
- [ ] API documentation — Swagger auto-generated

**Tools:** FastAPI, Uvicorn, JWT (python-jose), SQLAlchemy

---

## Week 11-12 — Next.js Frontend

### Dashboard UI
- [ ] `frontend/` — Next.js project setup:
  - [ ] `npx create-next-app@latest`
  - [ ] Tailwind CSS setup
  - [ ] shadcn/ui components
- [ ] Pages:
  - [ ] `/login` — auth page
  - [ ] `/dashboard` — overview stats
  - [ ] `/campaigns` — campaign list
  - [ ] `/campaigns/new` — campaign creation wizard:
    - [ ] Step 1: Target (niche, location)
    - [ ] Step 2: Conditions (size, has website)
    - [ ] Step 3: Outreach type (service/job/freelance)
    - [ ] Step 4: About yourself
    - [ ] Step 5: Sender config
    - [ ] Step 6: Model config
    - [ ] Step 7: Preview + confirm
  - [ ] `/campaigns/[id]` — campaign detail + analytics
  - [ ] `/settings` — API keys, sender, model
  - [ ] `/inbox` — unified reply inbox
- [ ] Components:
  - [ ] Campaign status card
  - [ ] Analytics charts (recharts)
  - [ ] Niche comparison chart
  - [ ] Email preview modal
  - [ ] Sender config form
  - [ ] Model selector dropdown

**Tools:** Next.js, Tailwind CSS, shadcn/ui, recharts, axios

---

## Week 13 — Pluggable Sender Integration

### Multiple Sender Support
- [ ] `modules/senders/` — sender abstraction:
  - [ ] `base.py` — BaseSender abstract class
  - [ ] `gmail_smtp.py` — Gmail SMTP implementation
  - [ ] `amazon_ses.py` — Amazon SES via boto3
  - [ ] `instantly.py` — Instantly.ai API
  - [ ] `custom_smtp.py` — Any SMTP server
- [ ] `modules/sender_factory.py` — pick sender from config:
  ```python
  SENDER_MODE = "gmail" | "ses" | "instantly" | "smtp"
  ```
- [ ] Frontend settings page — sender config form per type
- [ ] Test all sender types end-to-end

**Tools:** aiosmtplib, boto3 (AWS SDK), httpx (Instantly API)

---

### Amazon SES Setup Guide (for docs)
- [ ] AWS account setup guide in README
- [ ] SES identity verification steps
- [ ] IAM user + credentials
- [ ] Sending limits + sandbox exit

**Tools:** AWS SES, boto3

---

## Week 14 — Pluggable LLM + Model Selector

### Multiple LLM Support
- [ ] `utils/llm_factory.py` — LLM provider factory:
  - [ ] `openrouter` — default (Gemini Flash etc.)
  - [ ] `ollama` — local models
  - [ ] `openai` — GPT-4o etc.
  - [ ] `anthropic` — Claude
- [ ] Frontend model selector:
  - [ ] Provider dropdown
  - [ ] Model name input
  - [ ] API key field
  - [ ] Test connection button
- [ ] Ollama integration:
  - [ ] Docker Compose — optional Ollama service
  - [ ] Model pull on startup
  - [ ] GPU detection

**Tools:** OpenRouter, Ollama, openai SDK, anthropic SDK

---

## Week 15 — Cloud Hosting + Supabase Option

### Cloud Deployment
- [ ] `railway.toml` — Railway deployment config
- [ ] `render.yaml` — Render deployment config
- [ ] Environment variables setup on cloud
- [ ] PostgreSQL on Railway / Render
- [ ] Domain setup
- [ ] HTTPS setup
- [ ] Health check endpoints

**Tools:** Railway / Render, PostgreSQL

---

### Supabase Integration
- [ ] Supabase project setup guide in docs
- [ ] Connection string format for Supabase
- [ ] Row Level Security (RLS) guide
- [ ] Supabase dashboard usage tips
- [ ] Test migrations on Supabase

**Tools:** Supabase, Alembic

---

## Week 16 — Follow-up Sequences + Polish

### Follow-up Sequences
- [ ] `agents/email_writer/followup.py`:
  - [ ] Follow-up 1 (Day 3) — gentle reminder
  - [ ] Follow-up 2 (Day 7) — value add
  - [ ] Follow-up 3 (Day 14) — breakup email
  - [ ] Auto-stop on reply detection
- [ ] Cron update — daily follow-up check
- [ ] DB — track sequence position per contact
- [ ] Frontend — sequence config in campaign wizard

**Tools:** LangGraph, SQLAlchemy, Cron

---

### GitHub Actions CI/CD
- [ ] `.github/workflows/test.yml` — run tests on PR
- [ ] `.github/workflows/deploy.yml` — deploy on main merge
- [ ] Docker Hub auto-build on release
- [ ] Version tagging

**Tools:** GitHub Actions, Docker Hub

---

### Documentation
- [ ] `docs/` folder:
  - [ ] `getting-started.md` — 5 minute setup
  - [ ] `self-hosting.md` — Docker guide
  - [ ] `cloud-hosting.md` — Railway/Render guide
  - [ ] `configuration.md` — all env vars explained
  - [ ] `senders.md` — Gmail / SES / Instantly setup
  - [ ] `models.md` — OpenRouter / Ollama setup
  - [ ] `api-reference.md` — REST API docs
  - [ ] `faq.md` — common issues

---

### Phase 2 Done Checklist
- [ ] Frontend dashboard fully working
- [ ] Campaign creation wizard end-to-end
- [ ] Analytics dashboard showing real data
- [ ] Gmail + SES + Instantly senders working
- [ ] OpenRouter + Ollama models working
- [ ] Cloud deployment live (Railway/Render)
- [ ] Supabase option documented + tested
- [ ] Follow-up sequences working
- [ ] CI/CD pipeline running
- [ ] Docs complete
- [ ] GitHub repo public with good README
- [ ] First 5 external users onboarded

**Phase 2 additional cost:** ~₹800/month (cloud hosting)

---
---

# PHASE 3 — Scale, Community & Monetization

**Goal:** Make it a real product. Community. Revenue.
**Timeline:** Ongoing (3-6 months after Phase 2)
**End state:** Hundreds of users, recurring revenue, active community.

---

## Community Building
- [ ] GitHub repo — proper README with badges, demo GIF
- [ ] Discord server — user community
- [ ] Product Hunt launch
- [ ] Hacker News Show HN post
- [ ] Dev.to / Medium articles — "How I built an open-source Instantly.ai"
- [ ] Twitter/X presence
- [ ] YouTube demo video

---

## WhatsApp Outreach Module (India-specific)
- [ ] `agents/whatsapp/` — WhatsApp outreach agent:
  - [ ] Twilio WhatsApp API integration
  - [ ] Wati.io integration (India-focused)
  - [ ] Personalized WhatsApp message generation
  - [ ] Campaign type: email + WhatsApp combined
- [ ] Frontend — WhatsApp campaign option

**Tools:** Twilio, Wati.io, httpx

---

## LinkedIn Outreach Module
- [ ] `agents/linkedin/` — LinkedIn agent:
  - [ ] Profile research
  - [ ] Connection request message
  - [ ] Follow-up sequence
  - [ ] PhantomBuster integration (optional)
- [ ] Multi-channel campaign: email + LinkedIn

**Tools:** PhantomBuster API, httpx

---

## Advanced Analytics
- [ ] Week-over-week trend charts
- [ ] Niche performance heatmap
- [ ] Best time to send analysis
- [ ] Reply sentiment analysis (positive / negative / neutral)
- [ ] Revenue attribution (mark which leads converted)
- [ ] ROI calculator

**Tools:** recharts, LLM (sentiment), SQLAlchemy

---

## API Access
- [ ] Public REST API with API key auth
- [ ] Rate limiting per API key
- [ ] API docs (Swagger / Redoc)
- [ ] Webhook support — send events to user endpoints
- [ ] Python SDK — `pip install outreachagent`

**Tools:** FastAPI, slowapi (rate limiting)

---

## Monetization Setup
- [ ] Cloud hosted version pricing:
  - [ ] Free: 100 emails/month
  - [ ] Starter ₹999/month: 2000 emails/month
  - [ ] Pro ₹2999/month: 10000 emails/month
  - [ ] Agency ₹4999/month: unlimited
- [ ] Stripe / Razorpay integration
- [ ] Usage metering in DB
- [ ] Billing dashboard in frontend
- [ ] Invoice generation

**Tools:** Stripe, Razorpay, FastAPI

---

## Enterprise Features
- [ ] Multi-user workspaces
- [ ] Role-based access control (RBAC)
- [ ] Team inbox (shared reply management)
- [ ] Custom domain for tracking
- [ ] White-label option
- [ ] SSO (Google, GitHub login)
- [ ] Audit logs
- [ ] Custom LLM fine-tuning on your email style

**Tools:** FastAPI, NextAuth.js, PostgreSQL RLS

---

## Phase 3 Done Checklist
- [ ] 100+ GitHub stars
- [ ] 50+ active users
- [ ] First paying customer on cloud
- [ ] Discord 50+ members
- [ ] WhatsApp module working
- [ ] LinkedIn module working
- [ ] API public and documented
- [ ] Razorpay / Stripe integrated
- [ ] Revenue: ₹10,000+/month recurring

---
---

## Overall Timeline Summary

| Phase | Duration | Goal | Revenue |
|---|---|---|---|
| Phase 1 | 6-8 weeks | Working CLI system | Use for Syntrase internally |
| Phase 2 | 8-10 weeks | Full product + cloud | First external users |
| Phase 3 | 3-6 months | Scale + monetize | ₹10,000+/month |

---

## Cost Summary Per Phase

### Phase 1 (Monthly)
| Tool | Cost |
|---|---|
| OpenRouter (Gemini Flash) | ~$5-10 |
| Serper.dev | $10 |
| ZeroBounce (free tier) | ₹0 |
| Gmail SMTP | ₹0 |
| PostgreSQL (local Docker) | ₹0 |
| **Total** | **~$15-20 (₹1,250-1,700)** |

### Phase 2 (Monthly, additional)
| Tool | Cost |
|---|---|
| Cloud hosting (Railway/Render) | ~₹800 |
| Amazon SES (5k emails/day) | ~₹1,200 |
| Domain | ~₹100 |
| **Total additional** | **~₹2,100** |

### Phase 3 (Monthly, additional)
| Tool | Cost |
|---|---|
| Twilio (WhatsApp) | Usage based |
| Stripe fees | 2-3% per transaction |
| **Total additional** | **Covered by revenue** |

---

## Tech Stack Per Phase

### Phase 1 Stack
```
UV + Python 3.11
LangGraph
OpenRouter → Gemini Flash
Serper.dev
Crawl4AI
aiosmtplib (Gmail SMTP)
ZeroBounce
PostgreSQL + SQLAlchemy + Alembic
Loguru + Tenacity
Docker + Compose + Cron
pytest + Ruff
```

### Phase 2 Stack (additions)
```
FastAPI + Uvicorn
Next.js + Tailwind + shadcn/ui
recharts
JWT auth
boto3 (Amazon SES)
Instantly.ai API
Ollama
Railway / Render
Supabase (optional)
GitHub Actions
```

### Phase 3 Stack (additions)
```
Twilio / Wati.io (WhatsApp)
PhantomBuster (LinkedIn)
Stripe / Razorpay
slowapi (rate limiting)
NextAuth.js (SSO)
```

---

*Roadmap built for Syntrase — Syntrase, Mumbai.*