# CrodlinOutreachAgent

**Autonomous AI cold email engine for Crodlin Technology**

An AI-powered cold email outreach agent that finds target businesses, extracts contacts, writes personalized emails, sends them via SMTP with account rotation, and learns from results — all running autonomously via Docker + cron.

---

## Architecture

```
Niche + Location
      │
      ▼
┌─────────────────┐
│  Research Agent │  ← Serper.dev (Google Search)
└────────┬────────┘
         │ list[Business]
         ▼
┌──────────────────────┐
│  Contact Finder Agent│  ← Website scrape + email find
└────────┬─────────────┘
         │ list[Contact]
         ▼
┌──────────────────────┐
│  Email Writer Agent  │  ← OpenRouter LLM (Gemini Flash)
└────────┬─────────────┘
         │ list[EmailRecord]
         ▼
┌────────────────┐
│  Sender Module │  ← SMTP rotation (multi-account)
└────────┬───────┘
         │ tracking
         ▼
┌─────────────────┐
│  Feedback Agent │  ← Analyze results → optimize next batch
└─────────────────┘
```

---

## Tech Stack

| Component       | Tool                          | Why                                        |
|-----------------|-------------------------------|--------------------------------------------|
| LLM Provider    | OpenRouter (Gemini Flash)     | Free tier, fast, reliable                  |
| Web Search      | Serper.dev                    | 2500 free searches, structured JSON output |
| Orchestration   | LangGraph                     | Graph-based agent pipeline                 |
| Validation      | Pydantic v2                   | Type-safe data models                      |
| Configuration   | Pydantic Settings             | Env-based config with validation           |
| Async HTTP      | httpx                         | Fast async requests for APIs               |
| Storage         | CSV via pandas                | Simple, portable, no DB needed             |
| SMTP            | aiosmtplib                    | Async SMTP with multi-account rotation     |
| Task Scheduling | cron (Docker)                 | Reliable Linux scheduler                   |
| Container       | Docker                        | Portable, reproducible deployment          |
| Logging         | Loguru                        | Structured logging with rotation           |
| Retry           | Tenacity                      | Exponential backoff for API calls          |
| Testing         | pytest + pytest-asyncio       | Async test support                         |
| Linting         | Ruff                          | Fast Python linter                         |
| Package Manager | uv                            | Fast, reliable Python package management   |

---

## Setup

### Prerequisites

- **Docker** (for production deployment)
- **Python 3.11+** (for local development)
- **uv** — install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/CRODLIN-TECHNOLOGY/Crodlin-Outreach-agent.git
cd Crodlin-Outreach-agent
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

| Variable | How to Get |
|---|---|
| `OPENROUTER_API_KEY` | Sign up at [OpenRouter](https://openrouter.ai/keys) |
| `SERPER_API_KEY` | Sign up at [Serper.dev](https://serper.dev) (2500 free searches) |
| `EMAIL_ACCOUNTS` | See "Gmail App Passwords" below |
| `TRACKING_BASE_URL` | Your tracking domain (e.g., `https://track.yourdomain.com`) |
| `WEBHOOK_SECRET` | Generate a random secret: `openssl rand -hex 32` |

### 3. Gmail App Passwords Setup

For each email account you want to use for outreach:

1. Enable **2-Factor Authentication** on the Gmail account
2. Go to **Google Account → Security → App Passwords**
3. Select **Mail** and **Other (custom name)** → e.g., "Crodlin Outreach"
4. Copy the 16-character app password
5. Add to the `EMAIL_ACCOUNTS` JSON array in `.env`

Format:
```json
[
  {
    "email": "outreach1@gmail.com",
    "password": "xxxx xxxx xxxx xxxx",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587
  },
  {
    "email": "outreach2@gmail.com",
    "password": "xxxx xxxx xxxx xxxx",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587
  }
]
```

> **Note:** Each Gmail account has a daily limit of ~500 emails. Add more accounts to increase total daily volume.

### 4. Install Dependencies (Local Development)

```bash
uv sync
```

### 5. Install Dev Dependencies

```bash
uv sync --group dev
```

---

## Running Manually

### Full Outreach Pipeline

```bash
uv run main.py --mode outreach --niche "CA firms" --location "Mumbai"
```

### Feedback/Learning Loop

```bash
uv run main.py --mode feedback
```

### Using Custom Arguments

```bash
uv run main.py --mode outreach --niche "Software development agencies" --location "Bangalore, India"
```

---

## Docker Deployment

### Build and Run

```bash
docker compose -f docker/docker-compose.yml up -d
```

### View Logs

```bash
docker compose -f docker/docker-compose.yml logs -f
```

### Stop

```bash
docker compose -f docker/docker-compose.yml down
```

---

## Cron Schedule

The outreach agent runs automatically inside the Docker container based on IST (Asia/Kolkata) timezone.

| Time (IST)      | Frequency | Mode        | Description                          |
|-----------------|-----------|-------------|--------------------------------------|
| 9:00 AM         | Daily     | `outreach`  | Main outreach pipeline runs          |
| 6:00 PM         | Daily     | `feedback`  | Feedback/learning analyzes results   |
| Midnight (Sun)  | Weekly    | —           | Backup CSV data files                |

---

## Data Files

All data is stored as CSV files in the `data/` directory.

| File               | Contents                                               |
|--------------------|--------------------------------------------------------|
| `businesses.csv`   | Target businesses found by Research Agent              |
| `contacts.csv`     | Email contacts extracted by Contact Finder Agent       |
| `emails_sent.csv`  | Email records with content, status, and tracking data  |
| `results.csv`      | Campaign-level results and analytics                   |

> CSV files are persisted on the host machine via Docker volumes.

---

## Roadmap

- [x] Project scaffold — folder structure, configs, Docker, placeholders
- [ ] `core/storage.py` — CSV read/write logic (append, load, update)
- [ ] `agents/research/` — Serper search → business list
- [ ] `agents/contact_finder/` — Website scrape → email extraction
- [ ] `agents/email_writer/` — LLM → personalized email generation
- [ ] `core/pipeline.py` — Wire all agents in LangGraph
- [ ] Sender module — SMTP rotation with rate limiting
- [ ] Tracker module — Open/reply/bounce tracking via pixel
- [ ] `agents/feedback/` — Learning loop that optimizes next batch

---

## License

MIT — Crodlin Technology