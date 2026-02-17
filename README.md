# EML Analyzer

EML Analyzer is a web application for analyzing EML and MSG email files. It extracts headers, body content, IOCs (URLs, domains, IPs, emails), attachments, and integrates with external security services to produce threat verdicts.

## Features

- **Email parsing** — headers (basic, security, X-headers, hops), HTML/plain text bodies, attachments with file hashes
- **IOC extraction** — URLs, domains, IP addresses, and email addresses from message bodies
- **SpamAssassin** — spam scoring with rule-by-rule breakdown
- **Email authentication** — SPF, DKIM, DMARC verification with severity scoring
- **Homoglyph detection** — mixed-script domain spoofing and punycode decoding
- **OLE analysis** — VBA macros, XLM macros, Flash objects, encryption in Office attachments
- **URL unshortening** — resolves 30 common URL shortener services
- **VirusTotal** — attachment hash reputation lookups and file submission
- **urlscan.io** — URL scanning with malicious verdicts
- **EmailRep** — sender email reputation scoring
- **IPQualityScore** — IP, URL/domain, and email fraud scoring
- **IOC cross-reference table** — unified view of all IOCs with per-service verdicts
- **IOC lookup links** — click any IOC to open in VirusTotal, urlscan.io, Shodan, ANY.RUN, crt.sh, and more
- **Verdict scoring** — aggregate risk indicator from all analysis modules
- **Report view** — print-friendly analysis report
- **Caching** — Redis-backed result caching with browsable cache list
- **Authentication** — optional Clerk-based authentication with API key management
- **Dark mode** — toggle between light and dark themes
- **API documentation** — interactive Swagger UI at `/api/docs` and ReDoc at `/api/redoc`

## Quickstart

### Docker Compose (recommended)

```bash
git clone https://github.com/appliedi/eml_analyzer.git
cd eml_analyzer
docker compose up
```

The application runs at http://localhost:8050 with Redis caching and SpamAssassin.

### Single Container

```bash
git clone https://github.com/appliedi/eml_analyzer.git
cd eml_analyzer
docker build -t eml_analyzer .
docker run -p 8000:8000 eml_analyzer
```

Runs at http://localhost:8000 with Uvicorn + SpamAssassin managed by Circus (no Redis/caching).

## Configuration

Create a `.env` file in the project root. Key settings:

| Variable | Description | Default |
|---|---|---|
| `VIRUSTOTAL_API_KEY` | VirusTotal API key | — |
| `URLSCAN_API_KEY` | urlscan.io API key | — |
| `EMAIL_REP_API_KEY` | EmailRep API key | — |
| `IPQUALITYSCORE_API_KEY` | IPQualityScore API key | — |
| `CLERK_SECRET_KEY` | Clerk secret key (enables auth) | — |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (frontend build arg) | — |
| `REDIS_URL` | Redis connection URL | — |

See [DOCS.md](DOCS.md) for the complete configuration reference and full documentation.

## Development

### Backend

```bash
uv sync
uv run uvicorn backend.main:app --reload
uv run pytest                     # run tests
uv run ruff check backend/ tests/ # lint
uv run ruff format backend/ tests/ # format
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # dev server (proxies /api to localhost:8000)
npm run build        # production build
npm run test:unit    # tests
npm run lint         # lint
npm run format       # format
npm run type-check   # TypeScript check
```

## License

MIT License. See [LICENSE](LICENSE) for details.
