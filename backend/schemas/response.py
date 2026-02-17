import itertools
from functools import cached_property

from pydantic import Field

from .api_model import APIModel
from .eml import Eml
from .verdict import Verdict


class Response(APIModel):
    eml: Eml = Field(
        description="Parsed email content including headers, bodies, and attachments"
    )
    verdicts: list[Verdict] = Field(
        default_factory=list,
        description="Threat intelligence verdicts from configured services",
    )
    id: str = Field(description="Unique identifier for this analysis result")

    @cached_property
    def urls(self) -> set[str]:
        return set(
            itertools.chain.from_iterable([body.urls for body in self.eml.bodies])
        )

    @cached_property
    def sha256s(self) -> set[str]:
        return {attachment.hash.sha256 for attachment in self.eml.attachments}

    @cached_property
    def ip_addresses(self) -> set[str]:
        ips: set[str] = set()
        if self.eml.header.received_ip:
            ips.update(self.eml.header.received_ip)
        for body in self.eml.bodies:
            ips.update(body.ip_addresses)
        return ips

    @cached_property
    def domains(self) -> set[str]:
        return set(
            itertools.chain.from_iterable([body.domains for body in self.eml.bodies])
        )
