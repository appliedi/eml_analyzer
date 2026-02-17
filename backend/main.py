from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from Secweb.ContentSecurityPolicy import ContentSecurityPolicy

from backend import settings
from backend.api.api import api_router


def create_app():
    logger.add(
        settings.LOG_FILE, level=settings.LOG_LEVEL, backtrace=settings.LOG_BACKTRACE
    )

    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.PROJECT_NAME,
        description="REST API for analyzing EML and MSG email files. Extracts headers, body content, IOCs (URLs, domains, IPs, emails), attachments, and DKIM signatures. Integrates with VirusTotal, urlscan.io, EmailRep, IPQualityScore, and SpamAssassin for threat intelligence.",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        openapi_tags=[
            {
                "name": "analyze",
                "description": "Upload and analyze EML/MSG email files",
            },
            {
                "name": "submit",
                "description": "Submit IOCs to external threat intelligence services",
            },
            {"name": "lookup", "description": "Retrieve cached analysis results by ID"},
            {"name": "cache", "description": "Browse cached analysis keys"},
            {
                "name": "status",
                "description": "Check connectivity status of integrations",
            },
        ],
    )
    # add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.add_middleware(
        ContentSecurityPolicy,
        Option={
            "img-src": [
                "'self'",
                "data:",
                "t0.gstatic.com",
                "www.google.com",
                "https://img.clerk.com",
                "https://*.clerk.com",
                "https://fastapi.tiangolo.com",
            ],
            "connect-src": [
                "'self'",
                "https://*.clerk.accounts.dev",
                "https://*.clerk.com",
                "https://cdn.jsdelivr.net",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://cdn.jsdelivr.net",
            ],
            "worker-src": ["'self'", "blob:"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",
                "https://*.clerk.accounts.dev",
                "https://cdn.jsdelivr.net",
            ],
            "frame-src": ["'self'", "https://*.clerk.accounts.dev"],
        },
        script_nonce=False,
        style_nonce=False,
        report_only=False,
    )

    # add routes
    app.include_router(api_router, prefix="/api")
    app.mount("/", StaticFiles(html=True, directory="frontend/dist/"), name="index")

    return app


app = create_app()
