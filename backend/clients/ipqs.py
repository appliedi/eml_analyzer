from urllib.parse import quote

import httpx
from starlette.datastructures import Secret

from backend import schemas


class IPQualityScore(httpx.AsyncClient):
    def __init__(self, api_key: Secret) -> None:
        self._api_key = str(api_key)
        super().__init__(base_url="https://ipqualityscore.com")

    async def lookup_ip(self, ip: str, *, strictness: int = 1) -> schemas.IPQSIPLookup:
        r = await self.get(
            f"/api/json/ip/{self._api_key}/{ip}",
            params={"strictness": strictness},
        )
        r.raise_for_status()
        return schemas.IPQSIPLookup.model_validate(r.json())

    async def lookup_url(
        self, url: str, *, strictness: int = 0
    ) -> schemas.IPQSURLLookup:
        encoded_url = quote(url, safe="")
        r = await self.get(
            f"/api/json/url/{self._api_key}/{encoded_url}",
            params={"strictness": strictness},
        )
        r.raise_for_status()
        return schemas.IPQSURLLookup.model_validate(r.json())

    async def lookup_email(self, email: str) -> schemas.IPQSEmailLookup:
        r = await self.get(f"/api/json/email/{self._api_key}/{email}")
        r.raise_for_status()
        return schemas.IPQSEmailLookup.model_validate(r.json())
