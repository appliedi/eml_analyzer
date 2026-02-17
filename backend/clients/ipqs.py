from urllib.parse import quote

import httpx
from starlette.datastructures import Secret

from backend import schemas


class IPQSError(Exception):
    """Raised when IPQS returns success=false (quota exceeded, invalid key, etc.)."""

    def __init__(self, message: str):
        super().__init__(message)


class IPQualityScore(httpx.AsyncClient):
    def __init__(self, api_key: Secret) -> None:
        self._api_key = str(api_key)
        super().__init__(base_url="https://ipqualityscore.com")

    @staticmethod
    def _check_success(data: dict) -> None:
        if not data.get("success", True):
            raise IPQSError(data.get("message", "IPQS request failed"))

    async def lookup_ip(self, ip: str, *, strictness: int = 1) -> schemas.IPQSIPLookup:
        r = await self.get(
            f"/api/json/ip/{self._api_key}/{ip}",
            params={"strictness": strictness},
        )
        r.raise_for_status()
        data = r.json()
        self._check_success(data)
        return schemas.IPQSIPLookup.model_validate(data)

    async def lookup_url(
        self, url: str, *, strictness: int = 0
    ) -> schemas.IPQSURLLookup:
        encoded_url = quote(url, safe="")
        r = await self.get(
            f"/api/json/url/{self._api_key}/{encoded_url}",
            params={"strictness": strictness},
        )
        r.raise_for_status()
        data = r.json()
        self._check_success(data)
        return schemas.IPQSURLLookup.model_validate(data)

    async def lookup_email(self, email: str) -> schemas.IPQSEmailLookup:
        r = await self.get(f"/api/json/email/{self._api_key}/{email}")
        r.raise_for_status()
        data = r.json()
        self._check_success(data)
        return schemas.IPQSEmailLookup.model_validate(data)
