from pydantic import Field

from .api_model import APIModel


class IPQSIPLookup(APIModel):
    success: bool = Field(description="Whether the API request was successful")
    message: str | None = Field(default=None, description="API status or error message")
    fraud_score: int = Field(
        default=0, description="Fraud score from 0 (clean) to 100 (high risk)"
    )
    country_code: str | None = Field(
        default=None, description="Two-letter country code of the IP"
    )
    region: str | None = Field(
        default=None, description="Geographic region or state of the IP"
    )
    city: str | None = Field(default=None, description="City associated with the IP")
    isp: str | None = Field(
        default=None,
        validation_alias="ISP",
        description="Internet Service Provider name",
    )
    asn: int | None = Field(default=None, description="Autonomous System Number")
    organization: str | None = Field(
        default=None, description="Organization that owns the IP"
    )
    is_crawler: bool = Field(
        default=False, description="Whether the IP belongs to a known web crawler"
    )
    timezone: str | None = Field(
        default=None, description="Timezone of the IP location"
    )
    mobile: bool = Field(
        default=False, description="Whether the IP is a mobile connection"
    )
    host: str | None = Field(
        default=None, description="Reverse DNS hostname for the IP"
    )
    proxy: bool = Field(default=False, description="Whether the IP is a known proxy")
    vpn: bool = Field(
        default=False, description="Whether the IP is a known VPN exit node"
    )
    tor: bool = Field(
        default=False, description="Whether the IP is a known Tor exit node"
    )
    active_vpn: bool = Field(
        default=False, description="Whether the IP is actively connected via VPN"
    )
    active_tor: bool = Field(
        default=False, description="Whether the IP is actively connected via Tor"
    )
    recent_abuse: bool = Field(
        default=False, description="Whether the IP has been involved in recent abuse"
    )
    bot_status: bool = Field(
        default=False, description="Whether the IP is associated with bot activity"
    )


class IPQSURLLookup(APIModel):
    success: bool = Field(description="Whether the API request was successful")
    message: str | None = Field(default=None, description="API status or error message")
    unsafe: bool = Field(
        default=False, description="Whether the URL is considered unsafe"
    )
    domain: str | None = Field(default=None, description="Domain of the scanned URL")
    ip_address: str | None = Field(
        default=None, description="IP address the domain resolves to"
    )
    country_code: str | None = Field(
        default=None, description="Country code of the hosting server"
    )
    category: str | None = Field(
        default=None, description="Content category of the URL"
    )
    risk_score: int = Field(
        default=0, description="Risk score from 0 (clean) to 100 (high risk)"
    )
    status_code: int | None = Field(
        default=None, description="HTTP status code returned by the URL"
    )
    page_size: int | None = Field(default=None, description="Page size in bytes")
    content_type: str | None = Field(
        default=None, description="Content-Type header of the URL response"
    )
    server: str | None = Field(
        default=None, description="Server header of the URL response"
    )
    domain_rank: int | None = Field(
        default=None, description="Estimated domain popularity rank"
    )
    dns_valid: bool = Field(
        default=True, description="Whether the domain has valid DNS records"
    )
    parking: bool = Field(default=False, description="Whether the domain is parked")
    spamming: bool = Field(
        default=False, description="Whether the URL is associated with spam"
    )
    malware: bool = Field(
        default=False, description="Whether the URL is associated with malware"
    )
    phishing: bool = Field(
        default=False, description="Whether the URL is associated with phishing"
    )
    suspicious: bool = Field(
        default=False, description="Whether the URL is considered suspicious"
    )
    adult: bool = Field(
        default=False, description="Whether the URL contains adult content"
    )


class IPQSEmailLookup(APIModel):
    success: bool = Field(description="Whether the API request was successful")
    message: str | None = Field(default=None, description="API status or error message")
    valid: bool = Field(default=True, description="Whether the email address is valid")
    disposable: bool = Field(
        default=False, description="Whether the email uses a disposable email service"
    )
    smtp_score: int | None = Field(default=None, description="SMTP verification score")
    overall_score: int | None = Field(
        default=None, description="Overall quality score for the email address"
    )
    first_name: str | None = Field(
        default=None, description="First name associated with the email, if known"
    )
    common: bool = Field(
        default=False, description="Whether the email address pattern is common"
    )
    generic: bool = Field(
        default=False,
        description="Whether the email is a generic address (e.g. info@, admin@)",
    )
    dns_valid: bool = Field(
        default=True, description="Whether the email domain has valid DNS records"
    )
    honeypot: bool = Field(
        default=False, description="Whether the email is a known honeypot or spam trap"
    )
    deliverability: str | None = Field(
        default=None,
        description="Deliverability assessment (e.g. 'high', 'medium', 'low')",
    )
    frequent_complainer: bool = Field(
        default=False, description="Whether the email owner frequently reports spam"
    )
    spam_trap_score: str | None = Field(
        default=None, description="Likelihood of being a spam trap"
    )
    catch_all: bool = Field(
        default=False, description="Whether the domain accepts all email addresses"
    )
    timed_out: bool = Field(
        default=False,
        description="Whether the SMTP connection timed out during verification",
    )
    suspect: bool = Field(
        default=False, description="Whether the email is suspected of being fraudulent"
    )
    recent_abuse: bool = Field(
        default=False, description="Whether the email has been involved in recent abuse"
    )
    fraud_score: int = Field(
        default=0, description="Fraud score from 0 (clean) to 100 (high risk)"
    )
    suggested_domain: str | None = Field(
        default=None, description="Suggested correct domain if a typo was detected"
    )
    leaked: bool = Field(
        default=False, description="Whether the email has been found in data breaches"
    )
    domain_age: dict | None = Field(
        default=None,
        description="Age of the email domain with creation and update dates",
    )
    first_seen: dict | None = Field(
        default=None, description="When the email was first observed by IPQS"
    )
    sanitized_email: str | None = Field(
        default=None, description="Sanitized version of the email address"
    )
