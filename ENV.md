# Environment Variables

EML Analyzer is configured through environment variables loaded from a `.env` file in the project root. All variables are optional and fall back to sensible defaults. Copy the provided `.env` file and fill in the values you need.

## Third-Party API Keys

These integrations are disabled when their key is left blank.

| Variable | Description | Default |
|---|---|---|
| `VIRUSTOTAL_API_KEY` | [VirusTotal](https://www.virustotal.com/) API key for scanning attachment hashes | *(disabled)* |
| `URLSCAN_API_KEY` | [urlscan.io](https://urlscan.io/) API key for checking URLs against known malicious verdicts | *(disabled)* |
| `EMAIL_REP_API_KEY` | [EmailRep](https://emailrep.io/) API key for sender email reputation lookups | *(disabled)* |
| `IPQUALITYSCORE_API_KEY` | [IPQualityScore](https://www.ipqualityscore.com/) API key for IP reputation, URL/domain scanning, and email validation | *(disabled)* |

## Redis (Caching)

| Variable | Description | Default |
|---|---|---|
| `REDIS_URL` | Full Redis connection URL (e.g. `redis://localhost:6379`). When unset, caching is disabled. | *(disabled)* |
| `REDIS_PORT` | Host port to expose the Redis container on (Docker Compose only) | `6379` |
| `REDIS_EXPIRE` | TTL in seconds for cached analysis results. Set to `0` for no expiration. | `3600` |
| `REDIS_KEY_PREFIX` | Key prefix for cached entries in Redis | `analysis` |
| `REDIS_CACHE_LIST_AVAILABLE` | Whether the `/api/cache` endpoint is enabled | `true` |
| `REDIS_INSIGHT_PORT` | Host port for the Redis Insight UI (Docker Compose only) | `8001` |

## SpamAssassin

| Variable | Description | Default |
|---|---|---|
| `SPAMASSASSIN_HOST` | Hostname of the SpamAssassin spamd service | `127.0.0.1` |
| `SPAMASSASSIN_PORT` | Port of the SpamAssassin spamd service | `783` |
| `SPAMASSASSIN_TIMEOUT` | Timeout in seconds for SpamAssassin requests | `10` |

## Application

| Variable | Description | Default |
|---|---|---|
| `PORT` | Host port to expose the app on (Docker Compose only) | `8050` |
| `PROJECT_NAME` | Application name used in logging | `eml_analyzer` |
| `DEBUG` | Enable debug mode | `false` |
| `TESTING` | Enable testing mode | `false` |

## Logging

| Variable | Description | Default |
|---|---|---|
| `LOG_FILE` | Log output destination (file path or `stderr`) | `stderr` |
| `LOG_LEVEL` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `DEBUG` |
| `LOG_BACKTRACE` | Include full backtraces in log output | `true` |

## Async / Rate Limiting

These control [aiometer](https://github.com/florimondmanca/aiometer) concurrency for bulk API lookups (VirusTotal, urlscan.io, IPQualityScore).

| Variable | Description | Default |
|---|---|---|
| `ASYNC_MAX_AT_ONCE` | Maximum number of concurrent API requests | *(unlimited)* |
| `ASYNC_MAX_PER_SECOND` | Maximum API requests per second | *(unlimited)* |

## Example `.env`

```bash
# Third-party API keys (optional - leave blank to disable)
VIRUSTOTAL_API_KEY=
URLSCAN_API_KEY=
EMAIL_REP_API_KEY=
IPQUALITYSCORE_API_KEY=

# Redis
REDIS_PORT=6379
REDIS_EXPIRE=3600

# SpamAssassin
SPAMASSASSIN_PORT=783

# App
PORT=8050
```
