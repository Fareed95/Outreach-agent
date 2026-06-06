FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml .python-version ./

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p data logs

# Copy crontab and entrypoint
COPY docker/cron/crontab /etc/cron.d/outreach-cron
COPY docker/cron/entrypoint.sh /entrypoint.sh

# Set permissions
RUN chmod 0644 /etc/cron.d/outreach-cron && \
    chmod +x /entrypoint.sh && \
    crontab /etc/cron.d/outreach-cron

# Apply cron job
RUN crontab /etc/cron.d/outreach-cron

ENTRYPOINT ["/entrypoint.sh"]