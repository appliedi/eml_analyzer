import pytest

from backend import factories
from backend.factories.dkim_ import transform


@pytest.fixture
def factory():
    return factories.DKIMVerdictFactory()


@pytest.mark.asyncio
async def test_dkim_valid(dkim_valid_eml: bytes, factory: factories.DKIMVerdictFactory):
    """Test that an email with a DKIM-Signature header produces a verdict.

    Note: the fixture uses a fake signature that can't pass real DNS verification,
    so this only tests that a verdict is produced — not that it's a clean verdict.
    """
    verdict = await factory.call(
        eml_file=dkim_valid_eml, eml=factories.EmlFactory().call(dkim_valid_eml)
    )
    assert verdict
    assert verdict.name == "DKIM"
    assert verdict.score is not None
    assert len(verdict.details) > 0
    assert verdict.details[0].score is not None


@pytest.mark.asyncio
async def test_dkim_invalid(
    dkim_invalid_eml: bytes, factory: factories.DKIMVerdictFactory
):
    verdict = await factory.call(
        eml_file=dkim_invalid_eml, eml=factories.EmlFactory().call(dkim_invalid_eml)
    )
    assert verdict
    assert verdict.name == "DKIM"
    assert verdict.malicious
    assert verdict.score == 100
    assert len(verdict.details) > 0
    assert verdict.details[0].score == 100


@pytest.mark.asyncio
async def test_dkim_no_signature(
    dkim_no_signature_eml: bytes, factory: factories.DKIMVerdictFactory
):
    verdict = await factory.call(
        eml_file=dkim_no_signature_eml,
        eml=factories.EmlFactory().call(dkim_no_signature_eml),
    )
    assert verdict is None


def test_transform_valid():
    verdict = transform(True, name="DKIM")
    assert verdict.malicious is False
    assert verdict.score == 0
    assert verdict.details[0].score == 0


def test_transform_invalid():
    verdict = transform(False, name="DKIM")
    assert verdict.malicious is True
    assert verdict.score == 100
    assert verdict.details[0].score == 100
