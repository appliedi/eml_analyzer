from pydantic import BaseModel, Field


class Verdicts(BaseModel):
    score: int = Field(description="urlscan.io threat score (0-100)")
    malicious: bool = Field(
        description="Whether urlscan.io considers the URL malicious"
    )


class Page(BaseModel):
    url: str = Field(description="The scanned URL")


Task = Page


class Result(BaseModel):
    page: Page = Field(description="Page information for the scanned URL")
    task: Task = Field(description="Task information for the scan")
    verdicts: Verdicts = Field(description="Threat verdicts from urlscan.io")
    result: str = Field(description="API result URL for the scan")

    @property
    def link(self):
        return self.result.replace("/api/v1/", "")


class UrlScanLookup(BaseModel):
    results: list[Result] = Field(
        default_factory=list,
        description="List of urlscan.io scan results for the queried URL",
    )
