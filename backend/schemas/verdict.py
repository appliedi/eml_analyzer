from pydantic import Field

from .api_model import APIModel


class VerdictDetail(APIModel):
    key: str = Field(
        description="Identifier for this verdict detail (e.g. rule name, check name)"
    )
    score: float | int | None = Field(
        default=None, description="Numeric score for this detail, if applicable"
    )
    description: str = Field(
        description="Human-readable description of the verdict detail"
    )
    reference_link: str | None = Field(
        default=None, description="URL to the external service results page"
    )


class Verdict(APIModel):
    name: str = Field(
        description="Name of the verdict source (e.g. 'SpamAssassin', 'VirusTotal')"
    )
    malicious: bool = Field(
        description="Whether this verdict considers the email malicious"
    )
    score: float | int | None = Field(
        default=None, description="Overall threat score from this source"
    )
    details: list[VerdictDetail] = Field(
        default_factory=list,
        description="Individual checks or rules that contributed to the verdict",
    )
    error: str | None = Field(
        default=None, description="Error message if the verdict source failed"
    )
