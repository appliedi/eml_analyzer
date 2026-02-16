# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EML Analyzer is a full-stack web application for analyzing EML and MSG email files. It extracts headers, body content, IOCs (URLs, domains, IPs, emails), attachments, DKIM signatures, and integrates with external security services (VirusTotal, urlscan.io, EmailRep, SpamAssassin).

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, async/await throughout
- **Frontend**: Vue 3 (Composition API), TypeScript, Vite, Tailwind CSS v4, DaisyUI, Pinia, Zod
- **Package Manager**: `uv` for Python, `npm` for frontend
- **Services**: Redis (caching), SpamAssassin (spam scoring)

## Common Commands

### Backend

```bash
# Install dependencies
uv sync

# Run dev server (requires frontend/dist/ to exist)
uv run uvicorn backend.main:app --reload

# Run all tests (starts SpamAssassin via Docker automatically in local dev)
uv run pytest

# Run a single test file
uv run pytest tests/factories/test_eml.py

# Run a single test by name
uv run pytest -k "test_name"

# Lint
uv run ruff check backend/ tests/

# Lint with auto-fix
uv run ruff check --fix backend/ tests/

# Format
uv run ruff format backend/ tests/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Dev server (proxies /api to localhost:8000)
npm run dev

# Build for production
npm run build

# Run tests
npm run test:unit

# Type check
npm run type-check

# Lint with auto-fix
npm run lint

# Format
npm run format
```

### Docker

```bash
# Full stack (Gunicorn + Redis + SpamAssassin) - port 8050
docker compose up

# Single container (Uvicorn + SpamAssassin via Circus) - port 8000
docker build -t eml_analyzer . && docker run -p 8000:8000 eml_analyzer
```

## Architecture

### Backend (`backend/`)

FastAPI app created in `backend/main.py:create_app()`. API routes are mounted at `/api`, frontend static files at `/`.

**API Endpoints** (`backend/api/endpoints/`):
- `/api/analyze` - POST EML/MSG files for analysis
- `/api/submit` - POST to submit IOCs to external services
- `/api/lookup` - GET cached analysis results by ID
- `/api/cache` - GET list of cached analysis keys
- `/api/status` - GET connectivity status of Redis and SpamAssassin

**Factory Pattern** (`backend/factories/`): Each analysis type has a factory class (inheriting from `AbstractFactory`) that processes data. `EmlFactory` parses emails; `SpamAssassinFactory`, `DkimFactory`, `OleIdFactory`, `VirusTotalFactory`, `UrlScanFactory`, `EmailRepFactory` handle specific analysis types.

**Schemas** (`backend/schemas/`): Pydantic models for request/response validation and serialization. Frontend Zod schemas in `frontend/src/schemas.ts` mirror these.

**Configuration** (`backend/settings.py`): All config via environment variables (loaded from `.env`). Key settings: `REDIS_URL`, `SPAMASSASSIN_HOST`/`PORT`, `VIRUSTOTAL_API_KEY`, `URLSCAN_API_KEY`, `EMAIL_REP_API_KEY`.

**Dependencies** (`backend/dependencies.py`): FastAPI dependency injection for Redis client, SpamAssassin client, and API clients.

### Frontend (`frontend/src/`)

Vue 3 SPA with three routes: `/` (home/upload), `/cache` (browse cached), `/lookup/:id` (view cached result). State managed via Pinia store (`store.ts`). API calls in `api.ts` using Axios.

Components are organized by domain: `attachments/`, `bodies/`, `headers/`, `verdicts/` for rendering different parts of an analysis result.

### Testing

Backend tests use pytest with `pytest-asyncio` (auto mode), `pytest-docker` (SpamAssassin), and `vcrpy` (HTTP recording). Test fixtures are EML/MSG/DOCX/XLS files in `tests/fixtures/`. In CI, SpamAssassin runs as a GitHub Actions service; locally, `pytest-docker` starts it via `test.docker-compose.yml`.

Frontend tests use Vitest with jsdom environment.

## Linting & Formatting

- **Python**: Ruff for both linting and formatting. Line length not enforced (E501 ignored).
- **Frontend**: ESLint + Prettier. Line width 100, no semicolons, no trailing commas.
- **Pre-commit hooks**: Managed by lefthook (`lefthook.yml`). Runs ruff, eslint, prettier, vue-tsc type-check, and `uv lock`/`uv-sort` on pyproject.toml changes.

## CI

- **Python** (`.github/workflows/python.yml`): Ruff lint + pytest with coverage on Python 3.12
- **Node** (`.github/workflows/node.yml`): Vitest + ESLint + type-check on Node 24
- **Deploy** (`.github/workflows/deploy.yml`): Auto-deploy to Heroku on push to master
