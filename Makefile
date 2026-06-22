# ─────────────────────────────────────────────────────────────────────────────
# Syntrase — Makefile
# ─────────────────────────────────────────────────────────────────────────────
# This file abstracts away raw alembic/docker/uv commands into simple
# make targets. Run `make help` to see all available commands.
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install migrate migrate-new migrate-down migrate-history \
        db-shell docker-up docker-down docker-build docker-logs \
        run test lint format clean

help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:        ## Install dependencies via uv
	uv sync

migrate:        ## Apply all pending migrations
	uv run alembic upgrade head

migrate-new:    ## Create new migration (usage: make migrate-new name="add_xyz")
	uv run alembic revision --autogenerate -m "$(name)"

migrate-down:   ## Rollback last migration
	uv run alembic downgrade -1

migrate-history: ## Show migration history
	uv run alembic history --verbose

db-shell:       ## Open psql shell to Supabase DB
	@echo "Connecting to Supabase..."
	uv run python -c "from config.settings import settings; print(settings.DATABASE_URL_MIGRATIONS)"

docker-up:      ## Start all containers (detached)
	docker compose up -d

docker-down:    ## Stop all containers
	docker compose down

docker-build:   ## Rebuild containers
	docker compose up --build -d

docker-logs:    ## Tail logs from syntrase container
	docker compose logs -f syntrase

run:            ## Run main entrypoint locally
	uv run python main.py

test:           ## Run test suite
	uv run pytest -v

lint:           ## Run ruff linter
	uv run ruff check .

format:         ## Auto-format code with ruff
	uv run ruff format .

clean:          ## Remove cache/build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
