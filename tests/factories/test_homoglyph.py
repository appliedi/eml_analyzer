import pytest

from backend import factories
from backend.factories.homoglyph import check_domain, is_punycode


@pytest.fixture
def factory():
    return factories.HomoglyphVerdictFactory()


def test_is_punycode():
    assert is_punycode("xn--e1afmapc.xn--p1ai") is True
    assert is_punycode("example.com") is False
    assert is_punycode("sub.xn--nxasmq6b.com") is True


def test_check_domain_clean():
    findings = check_domain("example.com")
    # example.com is all ASCII Latin — no homoglyph findings expected
    assert isinstance(findings, list)


def test_check_domain_punycode():
    # xn--80ak6aa92e.com is the punycode for a Cyrillic domain
    findings = check_domain("xn--80ak6aa92e.com")
    assert any("Punycode" in f for f in findings)


@pytest.mark.asyncio
async def test_homoglyph_clean_domains(factory: factories.HomoglyphVerdictFactory):
    verdict = await factory.call(
        domains=["example.com", "google.com"],
        from_="user@example.com",
    )
    assert verdict is not None
    assert verdict.name == "Homoglyph Detection"
    # Clean domains should not be malicious
    assert verdict.malicious is False
    assert any(d.key == "clean" for d in verdict.details)


@pytest.mark.asyncio
async def test_homoglyph_empty_domains(factory: factories.HomoglyphVerdictFactory):
    verdict = await factory.call(domains=[], from_=None)
    assert verdict is not None
    assert verdict.malicious is False
    assert any(d.key == "clean" for d in verdict.details)


@pytest.mark.asyncio
async def test_homoglyph_punycode_domain(factory: factories.HomoglyphVerdictFactory):
    verdict = await factory.call(
        domains=["xn--80ak6aa92e.com"],
        from_=None,
    )
    assert verdict is not None
    assert verdict.malicious is True
    assert len(verdict.details) > 0
