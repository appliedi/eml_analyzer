from confusable_homoglyphs import confusables

from backend import schemas, types

from .abstract import AbstractAsyncFactory


def extract_from_domain(from_: str) -> str | None:
    """Extract domain from an email address."""
    if "@" in from_:
        return from_.split("@")[-1].strip().lower()
    return None


def is_punycode(domain: str) -> bool:
    """Check if a domain contains punycode-encoded labels (xn-- prefix)."""
    return any(label.startswith("xn--") for label in domain.split("."))


def decode_punycode(domain: str) -> str:
    """Decode a punycode domain to its Unicode representation."""
    try:
        return domain.encode("ascii").decode("idna")
    except (UnicodeError, UnicodeDecodeError):
        return domain


def check_domain(domain: str) -> list[str]:
    """Check a domain for homoglyph indicators. Returns list of finding descriptions."""
    findings: list[str] = []

    # Check for punycode
    if is_punycode(domain):
        decoded = decode_punycode(domain)
        findings.append(f"Punycode domain: {domain} decodes to {decoded}")
        domain = decoded

    # Check for mixed scripts (e.g., Latin + Cyrillic)
    if confusables.is_mixed_script(domain):
        findings.append(f"Mixed script detected in: {domain}")

    # Check for confusable characters
    result = confusables.is_confusable(domain, greedy=True)
    if result:
        for item in result:
            char = item["character"]
            aliases = [h["name"] for h in item.get("homoglyphs", []) if "name" in h]
            if aliases:
                findings.append(
                    f"Confusable character '{char}' in {domain} (similar to: {', '.join(aliases[:3])})"
                )

    return findings


def transform(
    flagged: dict[str, list[str]],
    *,
    name: str,
) -> schemas.Verdict:
    """Transform homoglyph findings into a Verdict."""
    details: list[schemas.VerdictDetail] = []
    malicious = False

    if flagged:
        malicious = True
        for domain, findings in flagged.items():
            details.append(
                schemas.VerdictDetail(
                    key=domain,
                    description="; ".join(findings),
                )
            )
    else:
        details.append(
            schemas.VerdictDetail(
                key="clean",
                description="No homoglyph or punycode domains detected",
            )
        )

    return schemas.Verdict(name=name, malicious=malicious, details=details)


class HomoglyphVerdictFactory(AbstractAsyncFactory):
    def __init__(self, *, name: str = "Homoglyph Detection"):
        self.name = name

    async def call(
        self,
        domains: types.ListSet[str],
        from_: str | None = None,
    ) -> schemas.Verdict:
        all_domains: set[str] = set(domains)

        if from_:
            from_domain = extract_from_domain(from_)
            if from_domain:
                all_domains.add(from_domain)

        flagged: dict[str, list[str]] = {}
        for domain in all_domains:
            findings = check_domain(domain)
            if findings:
                flagged[domain] = findings

        return transform(flagged, name=self.name)
