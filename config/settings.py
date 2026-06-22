"""
config/settings.py
------------------
Central configuration for Syntrase using Pydantic BaseSettings.
All values loaded from .env file automatically.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Syntrase application settings loaded from environment variables."""

    # ── OpenRouter ────────────────────────────────────────────
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemini-flash-1.5-8b"

    # ── Serper (Google Search API) ────────────────────────────
    SERPER_API_KEY: str
    SERPER_BASE_URL: str = "https://google.serper.dev"

    # ── SMTP Email Accounts ───────────────────────────────────
    # JSON array string: [{"email":"","password":"","smtp_host":"","smtp_port":587}]
    EMAIL_ACCOUNTS: str
    EMAIL_DAILY_LIMIT_PER_ACCOUNT: int = 80
    EMAIL_DELAY_SECONDS: int = 45

    # ── Tracking ──────────────────────────────────────────────
    TRACKING_BASE_URL: str
    WEBHOOK_SECRET: str

    # ── Campaign Defaults ─────────────────────────────────────
    DEFAULT_NICHE: str = ""
    DEFAULT_LOCATION: str = "India"
    MAX_EMAILS_PER_DAY: int = 3000
    BATCH_SIZE: int = 50

    # ── Storage (CSV paths) ───────────────────────────────────
    BUSINESSES_CSV: str = "data/businesses.csv"
    CONTACTS_CSV: str = "data/contacts.csv"
    EMAILS_SENT_CSV: str = "data/emails_sent.csv"
    RESULTS_CSV: str = "data/results.csv"

    # ── Logging ───────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/agent.log"

    # ── App ───────────────────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = False

    # ── Database (Supabase / PostgreSQL) ───────────────────
    # Runtime pooler connection (port 6543, asyncpg driver)
    DATABASE_URL: str = ""
    # Direct connection for Alembic migrations (port 5432, sync driver)
    DATABASE_URL_MIGRATIONS: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()