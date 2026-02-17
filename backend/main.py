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
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
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
