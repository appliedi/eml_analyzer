import pytest

from backend import factories
from backend.factories.url_unshorten import filter_shortened_urls, is_shortened_url


@pytest.fixture
def factory():
    return factories.URLUnshortenVerdictFactory()


def test_is_shortened_url():
    assert is_shortened_url("https://bit.ly/abc123") is True
    assert is_shortened_url("https://t.co/xyz") is True
    assert is_shortened_url("https://tinyurl.com/foo") is True
    assert is_shortened_url("https://example.com/page") is False
    assert is_shortened_url("https://google.com") is False


def test_is_shortened_url_invalid():
    assert is_shortened_url("not-a-url") is False
    assert is_shortened_url("") is False


def test_filter_shortened_urls():
    urls = [
        "https://bit.ly/abc",
        "https://example.com/page",
        "https://t.co/xyz",
        "https://google.com",
    ]
    result = filter_shortened_urls(urls)
    assert len(result) == 2
    assert "https://bit.ly/abc" in result
    assert "https://t.co/xyz" in result


def test_filter_shortened_urls_empty():
    assert filter_shortened_urls([]) == []
    assert filter_shortened_urls(["https://example.com"]) == []


@pytest.mark.asyncio
async def test_url_unshorten_no_shortened_urls(
    factory: factories.URLUnshortenVerdictFactory,
):
    verdict = await factory.call(urls=["https://example.com", "https://google.com"])
    assert verdict is None


@pytest.mark.asyncio
async def test_url_unshorten_empty_urls(
    factory: factories.URLUnshortenVerdictFactory,
):
    verdict = await factory.call(urls=[])
    assert verdict is None
