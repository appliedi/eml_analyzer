import typing

from fastapi import Depends, HTTPException, Request
from loguru import logger
from redis import Redis

from backend import clients, settings

if not settings.CLERK_SECRET_KEY:
    logger.warning("CLERK_SECRET_KEY is not configured — authentication is disabled")


def get_optional_redis():
    if settings.REDIS_URL:
        redis: Redis = Redis.from_url(str(settings.REDIS_URL))  # type: ignore
        try:
            yield redis
        finally:
            redis.close()
    else:
        yield None


async def get_optional_vt():
    if settings.VIRUSTOTAL_API_KEY:
        async with clients.VirusTotal(
            apikey=str(settings.VIRUSTOTAL_API_KEY)
        ) as client:
            yield client
    else:
        yield None


async def get_optional_urlscan():
    if settings.URLSCAN_API_KEY:
        async with clients.UrlScan(api_key=settings.URLSCAN_API_KEY) as client:
            yield client
    else:
        yield None


async def get_optional_email_rep():
    if settings.EMAIL_REP_API_KEY:
        async with clients.EmailRep(api_key=settings.EMAIL_REP_API_KEY) as client:
            yield client
    else:
        yield None


async def get_optional_ipqs():
    if settings.IPQUALITYSCORE_API_KEY:
        async with clients.IPQualityScore(
            api_key=settings.IPQUALITYSCORE_API_KEY
        ) as client:
            yield client
    else:
        yield None


def get_spam_assassin() -> clients.SpamAssassin:
    return clients.SpamAssassin(
        host=settings.SPAMASSASSIN_HOST,
        port=settings.SPAMASSASSIN_PORT,
        timeout=settings.SPAMASSASSIN_TIMEOUT,
    )


def verify_clerk_token(request: Request) -> dict | None:
    if not settings.CLERK_SECRET_KEY:
        return None

    from clerk_backend_api.security import (
        AuthenticateRequestOptions,
        authenticate_request,
    )

    options = AuthenticateRequestOptions(
        secret_key=str(settings.CLERK_SECRET_KEY),
    )
    state = authenticate_request(request, options)
    if not state.is_authenticated:
        raise HTTPException(status_code=401, detail=state.message or "Unauthorized")
    return state.payload


ClerkAuth = typing.Annotated[dict | None, Depends(verify_clerk_token)]

OptionalRedis = typing.Annotated[Redis | None, Depends(get_optional_redis)]
OptionalVirusTotal = typing.Annotated[
    clients.VirusTotal | None, Depends(get_optional_vt)
]
OptionalUrlScan = typing.Annotated[
    clients.UrlScan | None, Depends(get_optional_urlscan)
]
OptionalEmailRep = typing.Annotated[clients.EmailRep, Depends(get_optional_email_rep)]
OptionalIPQualityScore = typing.Annotated[
    clients.IPQualityScore | None, Depends(get_optional_ipqs)
]
SpamAssassin = typing.Annotated[clients.SpamAssassin, Depends(get_spam_assassin)]
