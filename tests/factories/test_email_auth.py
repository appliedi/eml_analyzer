import pytest

from backend import factories, schemas
from backend.factories.email_auth import (
    extract_from_domain,
    parse_authentication_results,
)
from backend.schemas.eml import Header


@pytest.fixture
def factory():
    return factories.EmailAuthVerdictFactory()


@pytest.fixture
def basic_email_eml() -> bytes:
    with open("tests/fixtures/emails/plain_emails/basic_email.eml", "rb") as f:
        return f.read()


def test_parse_authentication_results_spf():
    values = [
        "mx.google.com; spf=neutral (google.com: 203.12.160.161 is neither permitted) smtp.mail=test@example.com"
    ]
    results = parse_authentication_results(values)
    assert results["spf"] == "neutral"


def test_parse_authentication_results_multiple():
    values = [
        "antispamcloud.com; spf=pass smtp.mailfrom=user@example.com; dkim=pass header.i=example.com; dkim=fail header.i=other.com"
    ]
    results = parse_authentication_results(values)
    assert results["spf"] == "pass"
    assert results["dkim"] == "pass"  # first match wins


def test_parse_authentication_results_dmarc():
    values = ["mx.example.com; dmarc=fail (p=reject) header.from=example.com"]
    results = parse_authentication_results(values)
    assert results["dmarc"] == "fail"


def test_parse_authentication_results_empty():
    assert parse_authentication_results([]) == {}


def test_parse_authentication_results_non_string():
    assert parse_authentication_results([42, 100]) == {}


def test_extract_from_domain():
    assert extract_from_domain("user@example.com") == "example.com"
    assert extract_from_domain("user@Sub.Example.COM") == "sub.example.com"
    assert extract_from_domain("no-at-sign") is None


@pytest.mark.asyncio
async def test_email_auth_with_basic_email(
    basic_email_eml: bytes, factory: factories.EmailAuthVerdictFactory
):
    eml = factories.EmlFactory().call(basic_email_eml)
    verdict = await factory.call(eml)
    assert verdict is not None
    assert verdict.name == "Email Authentication"
    assert any(d.key == "spf" for d in verdict.details)


@pytest.mark.asyncio
async def test_email_auth_no_headers(factory: factories.EmailAuthVerdictFactory):
    """Test with an EML that has no Authentication-Results and a domain that likely has no DMARC."""
    eml = schemas.Eml(
        attachments=[],
        bodies=[],
        header=Header(
            subject="Test",
            to=["test@example.com"],
            received=[],
            header={},
            **{"from": "test@invalid.test"},
        ),
    )
    verdict = await factory.call(eml)
    # May return None or a verdict depending on DNS — either is acceptable
    if verdict is not None:
        assert verdict.name == "Email Authentication"


@pytest.mark.asyncio
async def test_email_auth_spf_fail_is_malicious(
    factory: factories.EmailAuthVerdictFactory,
):
    eml = schemas.Eml(
        attachments=[],
        bodies=[],
        header=Header(
            subject="Test",
            to=["test@example.com"],
            received=[],
            header={
                "authentication-results": [
                    "mx.example.com; spf=fail smtp.mailfrom=evil@spoofed.com"
                ]
            },
            **{"from": "test@invalid.test"},
        ),
    )
    verdict = await factory.call(eml)
    assert verdict is not None
    assert verdict.malicious is True
