from pydantic import Field

from .api_model import APIModel


class IPQSIPLookup(APIModel):
    success: bool
    message: str | None = None
    fraud_score: int = 0
    country_code: str | None = None
    region: str | None = None
    city: str | None = None
    isp: str | None = Field(default=None, validation_alias="ISP")
    asn: int | None = None
    organization: str | None = None
    is_crawler: bool = False
    timezone: str | None = None
    mobile: bool = False
    host: str | None = None
    proxy: bool = False
    vpn: bool = False
    tor: bool = False
    active_vpn: bool = False
    active_tor: bool = False
    recent_abuse: bool = False
    bot_status: bool = False


class IPQSURLLookup(APIModel):
    success: bool
    message: str | None = None
    unsafe: bool = False
    domain: str | None = None
    ip_address: str | None = None
    country_code: str | None = None
    category: str | None = None
    risk_score: int = 0
    status_code: int | None = None
    page_size: int | None = None
    content_type: str | None = None
    server: str | None = None
    domain_rank: int | None = None
    dns_valid: bool = True
    parking: bool = False
    spamming: bool = False
    malware: bool = False
    phishing: bool = False
    suspicious: bool = False
    adult: bool = False


class IPQSEmailLookup(APIModel):
    success: bool
    message: str | None = None
    valid: bool = True
    disposable: bool = False
    smtp_score: int | None = None
    overall_score: int | None = None
    first_name: str | None = None
    common: bool = False
    generic: bool = False
    dns_valid: bool = True
    honeypot: bool = False
    deliverability: str | None = None
    frequent_complainer: bool = False
    spam_trap_score: str | None = None
    catch_all: bool = False
    timed_out: bool = False
    suspect: bool = False
    recent_abuse: bool = False
    fraud_score: int = 0
    suggested_domain: str | None = None
    leaked: bool = False
    domain_age: dict | None = None
    first_seen: dict | None = None
    sanitized_email: str | None = None
