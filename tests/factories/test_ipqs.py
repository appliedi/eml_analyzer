import pytest
import vcr
from starlette.datastructures import Secret

from backend import clients, factories, settings


@pytest.fixture
async def client():
    async with clients.IPQualityScore(
        api_key=settings.IPQUALITYSCORE_API_KEY or Secret("")
    ) as client:
        yield client


@pytest.fixture
def ip_factory(client: clients.IPQualityScore):
    return factories.IPQSIPVerdictFactory(client)


@pytest.fixture
def url_factory(client: clients.IPQualityScore):
    return factories.IPQSURLVerdictFactory(client)


@pytest.fixture
def email_factory(client: clients.IPQualityScore):
    return factories.IPQSEmailVerdictFactory(client)


@vcr.use_cassette("tests/fixtures/vcr_cassettes/ipqs_ip.yaml")  # type: ignore
@pytest.mark.asyncio
async def test_ipqs_ip_factory(ip_factory: factories.IPQSIPVerdictFactory):
    verdict = await ip_factory.call(["1.2.3.4"])
    assert verdict.malicious is False


@vcr.use_cassette("tests/fixtures/vcr_cassettes/ipqs_url.yaml")  # type: ignore
@pytest.mark.asyncio
async def test_ipqs_url_factory(url_factory: factories.IPQSURLVerdictFactory):
    verdict = await url_factory.call(["http://example.com"])
    assert verdict.malicious is False


@vcr.use_cassette("tests/fixtures/vcr_cassettes/ipqs_email.yaml")  # type: ignore
@pytest.mark.asyncio
async def test_ipqs_email_factory(email_factory: factories.IPQSEmailVerdictFactory):
    verdict = await email_factory.call("test@example.com")
    assert verdict.malicious is False
