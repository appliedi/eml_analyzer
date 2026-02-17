# EML Analyzer Documentation

## Table of Contents

- [Overview](#overview)
- [Analysis Capabilities](#analysis-capabilities)
- [External Integrations](#external-integrations)
- [Verdict Scoring](#verdict-scoring)
- [User Interface](#user-interface)
- [Configuration Reference](#configuration-reference)
- [Deployment](#deployment)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)

---

## Overview

EML Analyzer is a full-stack web application for analyzing email files. Upload an EML or MSG file, and it extracts headers, body content, IOCs, and attachments, then runs them through multiple analysis engines to produce threat verdicts.

**Tech stack**: FastAPI (Python 3.12) backend, Vue 3 frontend with Tailwind CSS and DaisyUI, Redis for caching, SpamAssassin for spam scoring.

**Supported formats**: `.eml` (RFC 5322) and `.msg` (Microsoft Outlook).

---

## Analysis Capabilities

### Email Parsing

Extracts structured data from the email:

- **Headers** — displayed in five views: basic (From, To, Subject, Date, Message-ID), security (Authentication-Results, Received-SPF, ARC), X-headers, received hops (with hop-by-hop trace), and all other headers
- **Bodies** — HTML and plain text content, rendered separately
- **Attachments** — filename, content type, size, MD5, SHA-256, and SHA-512 hashes

### IOC Extraction

Extracts indicators of compromise from message bodies:

- URLs
- Domains
- IP addresses
- Email addresses

Each IOC is clickable with a dropdown menu linking to external lookup services (see [IOC Lookup Links](#ioc-lookup-links)).

### SpamAssassin

Scores the email against SpamAssassin rules. Produces a numeric score and a rule-by-rule breakdown showing each fired rule's name, individual score, and description. Emails scoring above 5.0 are flagged as spam.

### Email Authentication

Verifies SPF, DKIM, and DMARC from the email's `Authentication-Results` and `Received-SPF` headers. Additionally performs a live DNS lookup for the sender domain's DMARC policy (`_dmarc.<domain>` TXT record).

Authentication results are scored by severity:

| Result | Score |
|---|---|
| `pass` | 0 |
| `none` | 25 |
| `neutral` | 25 |
| `temperror` | 25 |
| `permerror` | 50 |
| `policy` | 50 |
| `softfail` | 75 |
| `fail` | 100 |

The verdict is flagged as malicious if SPF or DMARC result is `fail` or `softfail`.

A separate DKIM verification module performs cryptographic signature validation using the `dkim` library when a `DKIM-Signature` header is present.

### Homoglyph Detection

Detects domain spoofing using mixed-script characters. For each domain found in the email (including the sender domain), it checks for:

- **Punycode domains** — any domain label starting with `xn--` is decoded to reveal the actual Unicode characters
- **Mixed-script characters** — detects domains mixing character sets (e.g., Latin + Cyrillic)
- **Confusable characters** — identifies characters that visually resemble characters from another script

This module is always active and requires no API key.

### OLE Analysis

Scans Office document attachments using `oletools` for suspicious content:

| Check | Description |
|---|---|
| VBA macros | Visual Basic for Applications macros |
| XLM macros | Excel 4.0 macros |
| Flash objects | Embedded Flash/SWF content |
| Encryption | Password-protected/encrypted files |
| External relationships | Links to external resources |
| ObjectPool | Embedded OLE objects |

Only processes files that are valid OLE containers. Always active, no API key required.

### URL Unshortening

Resolves shortened URLs to their final destinations. This is informational only and does not affect the risk score. Supports 30 URL shortener services:

`bit.ly`, `t.co`, `tinyurl.com`, `goo.gl`, `ow.ly`, `is.gd`, `buff.ly`, `adf.ly`, `bl.ink`, `lnkd.in`, `db.tt`, `qr.ae`, `cur.lv`, `ity.im`, `q.gs`, `po.st`, `bc.vc`, `twitthis.com`, `su.pr`, `short.to`, `v.gd`, `tr.im`, `clck.ru`, `rb.gy`, `shorturl.at`, `tiny.cc`, `x.co`, `yourls.org`, `soo.gd`, `s2r.co`

---

## External Integrations

All external integrations are optional. If an API key is not configured, the integration is skipped and its status indicator shows as inactive.

### VirusTotal

Looks up attachment SHA-256 hashes against VirusTotal's database. If any antivirus engine flags the file as malicious, the verdict includes the detection count and a link to the VirusTotal report. You can also submit unrecognized attachments to VirusTotal for scanning.

**Requires**: `VIRUSTOTAL_API_KEY`

### urlscan.io

Searches urlscan.io for each URL found in the email body. Returns scan results with malicious verdicts and links to the urlscan.io report page.

**Requires**: `URLSCAN_API_KEY`

### EmailRep

Checks the sender's email address reputation. Reports whether the sender is flagged as suspicious and provides a reputation level (high, medium, low, none).

**Requires**: `EMAIL_REP_API_KEY`

### IPQualityScore

Runs three types of checks:

- **IP scoring** — checks IP addresses from received headers and email bodies against IPQS. Filters out private/reserved IPs. Reports proxy, VPN, Tor, bot, and recent abuse flags.
- **URL/domain scoring** — checks all URLs and domains from email bodies. Reports phishing, malware, spamming, and suspicious flags.
- **Email scoring** — checks the sender email address. Reports disposable, honeypot, recent abuse, suspect, and leaked flags.

For all three, a fraud/risk score above 75 is flagged as malicious.

**Requires**: `IPQUALITYSCORE_API_KEY`

---

## Verdict Scoring

Each analysis module produces a verdict with a `malicious` flag, optional numeric `score`, and detailed findings. The frontend aggregates all verdicts into an overall risk indicator.

### Risk Levels

The overall risk level is computed from the ratio of malicious verdicts to total scoring verdicts. URL Unshortening and errored verdicts are excluded from the calculation.

| Risk Level | Condition | Label |
|---|---|---|
| Unknown | No scoring verdicts | No Verdicts |
| Clean | 0% malicious | Clean |
| Low Risk | Up to 20% malicious | Low Risk |
| Suspicious | 21–50% malicious | Suspicious |
| High Risk | 51–75% malicious | High Risk |
| Malicious | Over 75% malicious | Malicious |

Individual verdict cards show a green (clean) or red (malicious) indicator with expandable details. Errored verdicts (e.g., API quota exceeded) are shown in a dimmed state.

---

## User Interface

### Home Page

Drag-and-drop or click-to-upload interface for EML and MSG files. After upload, analysis runs and results are displayed automatically.

### Results View

After analysis, the results page shows:

- **Scorecard** — overall risk indicator with the aggregate verdict level
- **Email summary** — sender, recipient, subject, date
- **Verdict cards** — one card per analysis module showing malicious/clean status with expandable details
- **IOC cross-reference table** — unified table of all extracted IOCs with per-service verdict status (flagged, clean, error, or N/A)
- **Headers** — five tabbed views: basic, security, X-headers, received hops, and all other headers
- **Bodies** — rendered HTML and plain text content
- **Attachments** — file details with hashes and VirusTotal submission option

### IOC Cross-Reference Table

A table listing every extracted IOC (URLs, domains, IPs, emails, SHA-256 hashes) with columns for each active service. Each cell shows:

- Flagged (red) — the service found this IOC malicious, with a link to the report
- Clean (green) — the service checked this IOC and found it benign
- Error (yellow) — the service encountered an error checking this IOC
- N/A (grey) — the service doesn't check this IOC type

Rows are sorted with malicious IOCs first, then by type (URL > domain > IP > email > SHA-256), then alphabetically.

### IOC Lookup Links

Clicking any IOC opens a dropdown menu with links to look it up on external services. Available services vary by IOC type:

- **VirusTotal** — URLs, domains, IPs, SHA-256 hashes
- **urlscan.io** — URLs, domains, IPs
- **IPQualityScore** — URLs, domains, IPs, emails
- **Shodan** — IPs
- **SecurityTrails** — domains
- **ANY.RUN** — SHA-256 hashes
- **Hybrid Analysis** — SHA-256 hashes
- **Browserling** — URLs
- **crt.sh** — domains
- **EmailRep** — emails

Each link also includes a "Copy to clipboard" option.

### Report View

A print-friendly analysis report available at `/#/report/:id`. Designed for sharing or archiving analysis results.

### Cache Browser

Browse previously analyzed emails at `/#/cache`. Lists all cached analysis IDs with links to view the full results. Requires Redis to be configured.

### API Keys Page

Available at `/#/api-keys` when Clerk authentication is enabled. Allows users to create and manage API keys for programmatic access to the API.

### Status Indicators

The navbar shows status badges for each integration (Redis, VirusTotal, urlscan.io, EmailRep, IPQS) indicating whether the service is connected and active.

### Dark Mode

Toggle between light and dark themes using the switch in the navbar.

---

## Configuration Reference

All configuration is done via environment variables. You can set them in a `.env` file in the project root.

### General

| Variable | Description | Default |
|---|---|---|
| `PROJECT_NAME` | Application name | `eml_analyzer` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_FILE` | Log output destination | `stderr` |
| `LOG_LEVEL` | Log level | `DEBUG` |
| `LOG_BACKTRACE` | Include backtraces in logs | `True` |

### SpamAssassin

| Variable | Description | Default |
|---|---|---|
| `SPAMASSASSIN_HOST` | SpamAssassin host | `127.0.0.1` |
| `SPAMASSASSIN_PORT` | SpamAssassin port | `783` |
| `SPAMASSASSIN_TIMEOUT` | SpamAssassin timeout in seconds | `10` |

### Redis

| Variable | Description | Default |
|---|---|---|
| `REDIS_URL` | Redis connection URL (e.g., `redis://localhost:6379`) | — |
| `REDIS_EXPIRE` | Cache expiration time in seconds | `3600` |
| `REDIS_KEY_PREFIX` | Redis key prefix for cached analyses | `analysis` |
| `REDIS_CACHE_LIST_AVAILABLE` | Enable the `/api/cache` endpoint | `True` |

### API Keys

| Variable | Description | Default |
|---|---|---|
| `VIRUSTOTAL_API_KEY` | VirusTotal API key | — |
| `URLSCAN_API_KEY` | urlscan.io API key | — |
| `EMAIL_REP_API_KEY` | EmailRep API key | — |
| `IPQUALITYSCORE_API_KEY` | IPQualityScore API key | — |

### Authentication

| Variable | Description | Default |
|---|---|---|
| `CLERK_SECRET_KEY` | Clerk secret key (enables authentication) | — |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (frontend build argument) | — |

### Rate Limiting

| Variable | Description | Default |
|---|---|---|
| `ASYNC_MAX_AT_ONCE` | Max concurrent async requests to external services | — |
| `ASYNC_MAX_PER_SECOND` | Max requests per second to external services | — |

---

## Deployment

### Docker Compose (Recommended)

Docker Compose runs three services: the app (Gunicorn), Redis (with Redis Insight on port 8001), and SpamAssassin.

```bash
git clone https://github.com/appliedi/eml_analyzer.git
cd eml_analyzer
docker compose up
```

The app is available at http://localhost:8050.

**Passing configuration**: Create a `.env` file in the project root. Docker Compose reads it automatically for API keys and other settings. The Clerk publishable key is passed as a Docker build argument:

```bash
docker compose build --build-arg VITE_CLERK_PUBLISHABLE_KEY=pk_...
docker compose up
```

**Frontend changes**: Docker caches the `COPY ./frontend` layer aggressively. After modifying frontend code, rebuild with `--no-cache`:

```bash
docker compose build --no-cache
docker compose up
```

**Port customization** via environment variables:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8050` | Application port |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_INSIGHT_PORT` | `8001` | Redis Insight web UI port |
| `SPAMASSASSIN_PORT` | `783` | SpamAssassin port |

### Single Container (Docker)

Runs Uvicorn and SpamAssassin together in one container, managed by Circus. No Redis, so caching is not available.

```bash
docker build -t eml_analyzer .
docker run -p 8000:8000 eml_analyzer
```

The app is available at http://localhost:8000.

Pass environment variables with `-e` flags or `--env-file`:

```bash
docker run -p 8000:8000 \
  -e VIRUSTOTAL_API_KEY=your_key \
  -e URLSCAN_API_KEY=your_key \
  eml_analyzer
```

### Heroku

The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that auto-deploys to Heroku on push to the `master` branch. It uses the single-container `Dockerfile`.

Required GitHub Actions secrets:

| Secret | Description |
|---|---|
| `HEROKU_API_KEY` | Heroku API key for deployment |
| `HEROKU_EMAIL` | Email associated with the Heroku account |

---

## Authentication

Authentication is optional. When `CLERK_SECRET_KEY` is not set, all API routes are accessible without authentication.

When enabled:

1. Set both `CLERK_SECRET_KEY` (backend) and `VITE_CLERK_PUBLISHABLE_KEY` (frontend build argument)
2. Users sign in via the Clerk authentication UI
3. The frontend automatically attaches Bearer tokens to all API requests
4. The API Keys page (`/#/api-keys`) becomes available for creating programmatic API keys

Both the secret key and publishable key must be set for authentication to work. The publishable key must be available at frontend build time (it's embedded into the JavaScript bundle).

---

## API Endpoints

All endpoints are mounted under `/api`. When Clerk authentication is enabled, all routes require a valid Bearer token or API key.

Interactive API documentation is available at:

- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI JSON**: `/api/openapi.json`

### Analyze

| Method | Path | Description |
|---|---|---|
| POST | `/api/analyze/` | Analyze a base64-encoded EML or MSG file. Request body: `{"file": "<base64>"}`. Returns full analysis results. |
| POST | `/api/analyze/file` | Analyze an uploaded file (multipart form data, field name: `file`). Returns full analysis results. |

### Submit

| Method | Path | Description |
|---|---|---|
| POST | `/api/submit/virustotal` | Submit an attachment to VirusTotal for scanning. Returns a link to the VirusTotal report. Requires `VIRUSTOTAL_API_KEY`. |

### Lookup

| Method | Path | Description |
|---|---|---|
| GET | `/api/lookup/{id}` | Retrieve a cached analysis by its SHA-256 ID. Returns 404 if not found, 501 if Redis is not configured. |

### Cache

| Method | Path | Description |
|---|---|---|
| GET | `/api/cache/` | List all cached analysis IDs. Returns 501 if Redis is not configured or `REDIS_CACHE_LIST_AVAILABLE` is `False`. |

### Status

| Method | Path | Description |
|---|---|---|
| GET | `/api/status/` | Check integration connectivity. Returns `{"cache": bool, "vt": bool, "email_rep": bool, "urlscan": bool, "ipqs": bool}`. |
