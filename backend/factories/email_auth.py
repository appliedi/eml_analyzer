import re

import aiodns

from backend import schemas

from .abstract import AbstractAsyncFactory

# Severity scores for authentication results (0 = best, 100 = worst)
AUTH_SEVERITY: dict[str, int] = {
    "pass": 0,
    "none": 25,
    "neutral": 25,
    "temperror": 25,
    "permerror": 50,
    "policy": 50,
    "softfail": 75,
    "fail": 100,
}

# Regex to extract method=result pairs from Authentication-Results headers
# Matches patterns like "spf=pass", "dkim=fail", "dmarc=none"
AUTH_RESULT_RE = re.compile(
    r"\b(spf|dkim|dmarc)\s*=\s*(pass|fail|softfail|neutral|none|temperror|permerror|policy)",
    re.IGNORECASE,
)

# Regex to extract the result from Received-SPF headers
# Matches the leading result word, e.g. "Fail (protection.outlook.com: ...)"
RECEIVED_SPF_RE = re.compile(
    r"^\s*(pass|fail|softfail|neutral|none|temperror|permerror)",
    re.IGNORECASE,
)


def parse_authentication_results(
    header_values: list[str | int],
) -> dict[str, str]:
    """Parse Authentication-Results header values and extract SPF/DKIM/DMARC results."""
    results: dict[str, str] = {}
    for value in header_values:
        if not isinstance(value, str):
            continue
        for match in AUTH_RESULT_RE.finditer(value):
            method = match.group(1).lower()
            result = match.group(2).lower()
            # Keep the first result for each method (most authoritative)
            if method not in results:
                results[method] = result
    return results


def parse_received_spf(
    header_values: list[str | int],
) -> str | None:
    """Parse Received-SPF header values and extract the SPF result.

    The Received-SPF header starts with the result, e.g.:
    Fail (protection.outlook.com: domain of example.com does not designate ...)
    """
    for value in header_values:
        if not isinstance(value, str):
            continue
        match = RECEIVED_SPF_RE.match(value)
        if match:
            return match.group(1).lower()
    return None


def extract_from_domain(from_: str) -> str | None:
    """Extract domain from an email address."""
    if "@" in from_:
        return from_.split("@")[-1].strip().lower()
    return None


async def lookup_dmarc_policy(domain: str) -> str | None:
    """Look up the DMARC policy for a domain via DNS TXT record."""
    resolver = aiodns.DNSResolver()
    try:
        records = await resolver.query_dns(f"_dmarc.{domain}", "TXT")
        for record in records:
            text = record.text if isinstance(record.text, str) else record.text.decode()
            if text.startswith("v=DMARC1"):
                match = re.search(
                    r"\bp=(none|quarantine|reject)\b", text, re.IGNORECASE
                )
                if match:
                    return match.group(1).lower()
    except Exception:
        pass
    return None


def transform(
    auth_results: dict[str, str],
    dmarc_policy: str | None,
    *,
    name: str,
) -> schemas.Verdict:
    """Transform parsed authentication results into a Verdict."""
    details: list[schemas.VerdictDetail] = []
    malicious = False

    for method in ("spf", "dkim", "dmarc"):
        result = auth_results.get(method)
        if result:
            is_fail = result in ("fail", "softfail")
            if is_fail and method in ("spf", "dmarc"):
                malicious = True
            details.append(
                schemas.VerdictDetail(
                    key=method,
                    score=AUTH_SEVERITY.get(result, 0),
                    description=f"{method.upper()}: {result}",
                )
            )

    if dmarc_policy:
        details.append(
            schemas.VerdictDetail(
                key="dmarc_policy",
                description=f"DMARC policy: p={dmarc_policy}",
            )
        )

    if not details:
        details.append(
            schemas.VerdictDetail(
                key="no_auth",
                description="No SPF/DKIM/DMARC authentication results found",
            )
        )

    scored_details = [d.score for d in details if d.score is not None]
    verdict_score = max(scored_details) if scored_details else None

    return schemas.Verdict(name=name, malicious=malicious, score=verdict_score, details=details)


class EmailAuthVerdictFactory(AbstractAsyncFactory):
    def __init__(self, *, name: str = "Email Authentication"):
        self.name = name

    async def call(self, eml: schemas.Eml) -> schemas.Verdict | None:
        # Parse Authentication-Results headers
        auth_header_values = eml.header.header.get("authentication-results", [])
        auth_results = parse_authentication_results(auth_header_values)

        # Fall back to Received-SPF header if no SPF result found
        if "spf" not in auth_results:
            received_spf_values = eml.header.header.get("received-spf", [])
            spf_result = parse_received_spf(received_spf_values)
            if spf_result:
                auth_results["spf"] = spf_result

        # Look up DMARC policy for the sender domain
        dmarc_policy = None
        if eml.header.from_:
            domain = extract_from_domain(eml.header.from_)
            if domain:
                dmarc_policy = await lookup_dmarc_policy(domain)

        # Return None if we have no useful information
        if not auth_results and not dmarc_policy:
            return None

        return transform(auth_results, dmarc_policy, name=self.name)
