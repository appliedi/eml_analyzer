from typing import Any

from pydantic import Field

from .api_model import APIModel


class EmailRepLookup(APIModel):
    email: str = Field(description="The email address that was looked up")
    reputation: str = Field(
        description="Reputation level (e.g. 'high', 'medium', 'low', 'none')"
    )
    suspicious: bool = Field(
        description="Whether EmailRep considers this address suspicious"
    )
    references: int = Field(
        description="Number of sources where this email has been observed"
    )
    details: dict[str, Any] = Field(
        description="Additional reputation details from EmailRep"
    )
