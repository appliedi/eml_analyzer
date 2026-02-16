import contextlib
from functools import partial
from urllib.parse import urlparse

import aiometer
import httpx

from backend import schemas, settings, types

from .abstract import AbstractAsyncFactory

SHORTENER_DOMAINS: set[str] = {
    "bit.ly",
    "t.co",
    "tinyurl.com",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "adf.ly",
    "bl.ink",
    "lnkd.in",
    "db.tt",
    "qr.ae",
    "cur.lv",
    "ity.im",
    "q.gs",
    "po.st",
    "bc.vc",
    "twitthis.com",
    "su.pr",
    "short.to",
    "v.gd",
    "tr.im",
    "clck.ru",
    "rb.gy",
    "shorturl.at",
    "tiny.cc",
    "x.co",
    "yourls.org",
    "soo.gd",
    "s2r.co",
}


def is_shortened_url(url: str) -> bool:
    """Check if a URL belongs to a known URL shortener service."""
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname in SHORTENER_DOMAINS
    except Exception:
        return False


def filter_shortened_urls(urls: types.ListSet[str]) -> list[str]:
    """Filter a list of URLs to only those from known shortener services."""
    return [url for url in urls if is_shortened_url(url)]


async def resolve_url(url: str) -> tuple[str, str | None]:
    """Resolve a shortened URL by following redirects. Returns (original_url, final_url)."""
    with contextlib.suppress(Exception):
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=5.0, verify=False
        ) as client:
            response = await client.head(url)
            final_url = str(response.url)
            if final_url != url:
                return (url, final_url)
    return (url, None)


async def bulk_resolve(
    urls: list[str],
    *,
    max_per_second: float | None = settings.ASYNC_MAX_PER_SECOND,
    max_at_once: int | None = settings.ASYNC_MAX_AT_ONCE,
) -> list[tuple[str, str | None]]:
    """Resolve multiple shortened URLs concurrently."""
    tasks = [partial(resolve_url, url) for url in urls]
    return await aiometer.run_all(
        tasks, max_at_once=max_at_once, max_per_second=max_per_second
    )


def transform(
    results: list[tuple[str, str | None]],
    *,
    name: str,
) -> schemas.Verdict:
    """Transform URL resolution results into a Verdict."""
    details: list[schemas.VerdictDetail] = []

    resolved = [(orig, final) for orig, final in results if final]

    if resolved:
        for original, final in resolved:
            details.append(
                schemas.VerdictDetail(
                    key=original,
                    description=f"{original} -> {final}",
                )
            )
    else:
        details.append(
            schemas.VerdictDetail(
                key="no_resolve",
                description="No shortened URLs could be resolved",
            )
        )

    # Informational only — malicious is always False
    return schemas.Verdict(name=name, malicious=False, details=details)


class URLUnshortenVerdictFactory(AbstractAsyncFactory):
    def __init__(self, *, name: str = "URL Unshortening"):
        self.name = name

    async def call(self, urls: types.ListSet[str]) -> schemas.Verdict | None:
        shortened = filter_shortened_urls(urls)
        if not shortened:
            return None

        results = await bulk_resolve(shortened)
        return transform(results, name=self.name)
