from pydantic import Field

from .api_model import APIModel


class SubmissionResult(APIModel):
    reference_url: str = Field(
        description="URL to view the submission results on the external service"
    )
    status: str | None = Field(
        default=None, description="Submission status message, if any"
    )
