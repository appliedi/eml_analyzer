from backend.schemas.ipqs import IPQSEmailLookup, IPQSIPLookup, IPQSURLLookup


def test_ip_lookup_from_api_response():
    data = {
        "success": True,
        "message": "Success",
        "fraud_score": 85,
        "country_code": "US",
        "region": "California",
        "city": "Los Angeles",
        "ISP": "Example ISP",
        "ASN": 12345,
        "organization": "Example Org",
        "is_crawler": False,
        "timezone": "America/Los_Angeles",
        "mobile": False,
        "host": "example.com",
        "proxy": True,
        "vpn": True,
        "tor": False,
        "active_vpn": True,
        "active_tor": False,
        "recent_abuse": True,
        "bot_status": False,
    }
    result = IPQSIPLookup.model_validate(data)
    assert result.success is True
    assert result.fraud_score == 85
    assert result.isp == "Example ISP"
    assert result.proxy is True
    assert result.vpn is True
    assert result.tor is False
    assert result.recent_abuse is True


def test_ip_lookup_isp_alias():
    data = {"success": True, "ISP": "Test ISP"}
    result = IPQSIPLookup.model_validate(data)
    assert result.isp == "Test ISP"


def test_ip_lookup_defaults():
    data = {"success": True}
    result = IPQSIPLookup.model_validate(data)
    assert result.fraud_score == 0
    assert result.proxy is False
    assert result.vpn is False
    assert result.tor is False
    assert result.bot_status is False
    assert result.isp is None


def test_url_lookup_from_api_response():
    data = {
        "success": True,
        "unsafe": True,
        "domain": "malicious.example.com",
        "ip_address": "1.2.3.4",
        "country_code": "US",
        "category": "phishing",
        "risk_score": 95,
        "status_code": 200,
        "page_size": 12345,
        "content_type": "text/html",
        "server": "nginx",
        "domain_rank": 0,
        "dns_valid": True,
        "parking": False,
        "spamming": True,
        "malware": True,
        "phishing": True,
        "suspicious": True,
        "adult": False,
    }
    result = IPQSURLLookup.model_validate(data)
    assert result.success is True
    assert result.unsafe is True
    assert result.risk_score == 95
    assert result.phishing is True
    assert result.malware is True
    assert result.spamming is True


def test_url_lookup_defaults():
    data = {"success": True}
    result = IPQSURLLookup.model_validate(data)
    assert result.unsafe is False
    assert result.risk_score == 0
    assert result.phishing is False
    assert result.malware is False


def test_email_lookup_from_api_response():
    data = {
        "success": True,
        "valid": True,
        "disposable": True,
        "smtp_score": 0,
        "overall_score": 1,
        "first_name": "Unknown",
        "common": False,
        "generic": False,
        "dns_valid": True,
        "honeypot": True,
        "deliverability": "low",
        "frequent_complainer": False,
        "spam_trap_score": "none",
        "catch_all": False,
        "timed_out": False,
        "suspect": True,
        "recent_abuse": True,
        "fraud_score": 90,
        "suggested_domain": None,
        "leaked": True,
        "sanitized_email": "test@example.com",
    }
    result = IPQSEmailLookup.model_validate(data)
    assert result.success is True
    assert result.fraud_score == 90
    assert result.disposable is True
    assert result.honeypot is True
    assert result.recent_abuse is True
    assert result.leaked is True


def test_email_lookup_defaults():
    data = {"success": True}
    result = IPQSEmailLookup.model_validate(data)
    assert result.fraud_score == 0
    assert result.disposable is False
    assert result.honeypot is False
    assert result.valid is True
