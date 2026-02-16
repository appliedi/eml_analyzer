import pytest
import vcr
from starlette.datastructures import Secret

from backend import clients, factories, settings
from backend.factories.ipqs import filter_global_ips


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


class TestFilterGlobalIPs:
    def test_private_ipv4_filtered(self):
        assert filter_global_ips(["10.0.0.1", "172.16.0.1", "192.168.1.1"]) == set()

    def test_loopback_filtered(self):
        assert filter_global_ips(["127.0.0.1", "::1"]) == set()

    def test_link_local_filtered(self):
        assert filter_global_ips(["169.254.1.1"]) == set()

    def test_global_ips_kept(self):
        assert filter_global_ips(["8.8.8.8", "1.2.3.4"]) == {"8.8.8.8", "1.2.3.4"}

    def test_mixed_input(self):
        result = filter_global_ips(["192.168.1.1", "8.8.8.8", "10.0.0.1", "1.1.1.1"])
        assert result == {"8.8.8.8", "1.1.1.1"}

    def test_malformed_strings_skipped(self):
        assert filter_global_ips(["not-an-ip", "999.999.999.999", ""]) == set()

    def test_empty_input(self):
        assert filter_global_ips([]) == set()


@pytest.mark.asyncio
async def test_bulk_lookup_ip_private_only(client: clients.IPQualityScore):
    """Private-only IPs should return empty without making API calls."""
    from backend.factories.ipqs import bulk_lookup_ip

    result = await bulk_lookup_ip(["192.168.1.1", "127.0.0.1"], client=client)
    assert result == []


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
