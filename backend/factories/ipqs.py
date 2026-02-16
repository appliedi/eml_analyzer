import contextlib
import ipaddress
from functools import partial

import aiometer

from backend import clients, schemas, settings, types

from .abstract import AbstractAsyncFactory

FRAUD_SCORE_THRESHOLD = 75


def filter_global_ips(ips: types.ListSet[str]) -> set[str]:
    """Filter out private, reserved, loopback, and link-local IPs."""
    result: set[str] = set()
    for ip in ips:
        try:
            if ipaddress.ip_address(ip).is_global:
                result.add(ip)
        except ValueError:
            pass
    return result


async def lookup_ip(
    ip: str, *, client: clients.IPQualityScore
) -> schemas.IPQSIPLookup | None:
    with contextlib.suppress(Exception):
        return await client.lookup_ip(ip)
    return None


async def bulk_lookup_ip(
    ips: types.ListSet[str],
    *,
    client: clients.IPQualityScore,
    max_per_second: float | None = settings.ASYNC_MAX_PER_SECOND,
    max_at_once: int | None = settings.ASYNC_MAX_AT_ONCE,
) -> list[tuple[str, schemas.IPQSIPLookup]]:
    global_ips = filter_global_ips(ips)
    if not global_ips:
        return []
    tasks = [partial(lookup_ip, ip, client=client) for ip in global_ips]
    ip_list = list(global_ips)
    results = await aiometer.run_all(
        tasks, max_at_once=max_at_once, max_per_second=max_per_second
    )
    return [
        (ip, result) for ip, result in zip(ip_list, results, strict=False) if result
    ]


def transform_ip(
    lookups: list[tuple[str, schemas.IPQSIPLookup]], *, name: str
) -> schemas.Verdict:
    details: list[schemas.VerdictDetail] = []
    malicious = False

    for ip, result in lookups:
        if result.fraud_score > FRAUD_SCORE_THRESHOLD:
            malicious = True
            flags = []
            if result.proxy:
                flags.append("proxy")
            if result.vpn:
                flags.append("VPN")
            if result.tor:
                flags.append("Tor")
            if result.bot_status:
                flags.append("bot")
            if result.recent_abuse:
                flags.append("recent abuse")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            details.append(
                schemas.VerdictDetail(
                    key=ip,
                    score=result.fraud_score,
                    description=f"{ip} has fraud score {result.fraud_score}{flag_str}.",
                    reference_link=f"https://ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/{ip}",
                )
            )

    if not malicious:
        return schemas.Verdict(
            name=name,
            malicious=False,
            details=[
                schemas.VerdictDetail(
                    key="benign",
                    description="No suspicious IPs detected by IPQS.",
                )
            ],
        )

    return schemas.Verdict(name=name, malicious=True, score=100, details=details)


async def lookup_url(
    url: str, *, client: clients.IPQualityScore
) -> schemas.IPQSURLLookup | None:
    with contextlib.suppress(Exception):
        return await client.lookup_url(url)
    return None


async def bulk_lookup_url(
    urls: types.ListSet[str],
    *,
    client: clients.IPQualityScore,
    max_per_second: float | None = settings.ASYNC_MAX_PER_SECOND,
    max_at_once: int | None = settings.ASYNC_MAX_AT_ONCE,
) -> list[tuple[str, schemas.IPQSURLLookup]]:
    tasks = [partial(lookup_url, url, client=client) for url in set(urls)]
    url_list = list(set(urls))
    results = await aiometer.run_all(
        tasks, max_at_once=max_at_once, max_per_second=max_per_second
    )
    return [
        (url, result) for url, result in zip(url_list, results, strict=False) if result
    ]


def transform_url(
    lookups: list[tuple[str, schemas.IPQSURLLookup]], *, name: str
) -> schemas.Verdict:
    details: list[schemas.VerdictDetail] = []
    malicious = False

    for url, result in lookups:
        if result.unsafe or result.risk_score > FRAUD_SCORE_THRESHOLD:
            malicious = True
            flags = []
            if result.phishing:
                flags.append("phishing")
            if result.malware:
                flags.append("malware")
            if result.spamming:
                flags.append("spamming")
            if result.suspicious:
                flags.append("suspicious")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            details.append(
                schemas.VerdictDetail(
                    key=url,
                    score=result.risk_score,
                    description=f"{url} has risk score {result.risk_score}{flag_str}.",
                    reference_link=f"https://ipqualityscore.com/threat-intelligence/malicious-url-scanner/lookup/{url}",
                )
            )

    if not malicious:
        return schemas.Verdict(
            name=name,
            malicious=False,
            details=[
                schemas.VerdictDetail(
                    key="benign",
                    description="No malicious URLs or domains detected by IPQS.",
                )
            ],
        )

    return schemas.Verdict(name=name, malicious=True, score=100, details=details)


def transform_email(
    email: str, result: schemas.IPQSEmailLookup, *, name: str
) -> schemas.Verdict:
    details: list[schemas.VerdictDetail] = []
    malicious = False

    if result.fraud_score > FRAUD_SCORE_THRESHOLD:
        malicious = True
        flags = []
        if result.disposable:
            flags.append("disposable")
        if result.honeypot:
            flags.append("honeypot")
        if result.recent_abuse:
            flags.append("recent abuse")
        if result.suspect:
            flags.append("suspect")
        if result.leaked:
            flags.append("leaked")
        flag_str = f" ({', '.join(flags)})" if flags else ""
        details.append(
            schemas.VerdictDetail(
                key=email,
                score=result.fraud_score,
                description=f"{email} has fraud score {result.fraud_score}{flag_str}.",
                reference_link=f"https://ipqualityscore.com/free-email-verifier/lookup/{email}",
            )
        )

    if not malicious:
        return schemas.Verdict(
            name=name,
            malicious=False,
            details=[
                schemas.VerdictDetail(
                    key="benign",
                    description=f"{email} is not suspicious according to IPQS.",
                )
            ],
        )

    return schemas.Verdict(name=name, malicious=True, score=100, details=details)


class IPQSIPVerdictFactory(AbstractAsyncFactory):
    def __init__(self, client: clients.IPQualityScore, *, name: str = "IPQS IP"):
        self.client = client
        self.name = name

    async def call(self, ips: types.ListSet[str]) -> schemas.Verdict:
        lookups = await bulk_lookup_ip(ips, client=self.client)
        return transform_ip(lookups, name=self.name)


class IPQSURLVerdictFactory(AbstractAsyncFactory):
    def __init__(self, client: clients.IPQualityScore, *, name: str = "IPQS URL"):
        self.client = client
        self.name = name

    async def call(self, urls: types.ListSet[str]) -> schemas.Verdict:
        lookups = await bulk_lookup_url(urls, client=self.client)
        return transform_url(lookups, name=self.name)


class IPQSEmailVerdictFactory(AbstractAsyncFactory):
    def __init__(self, client: clients.IPQualityScore, *, name: str = "IPQS Email"):
        self.client = client
        self.name = name

    async def call(self, email: str) -> schemas.Verdict:
        result = await self.client.lookup_email(email)
        return transform_email(email, result, name=self.name)
