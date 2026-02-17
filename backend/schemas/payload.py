from pydantic import Field, field_validator

from backend.validator import is_eml_or_msg_file

from .api_model import APIModel


class Payload(APIModel):
    file: str = Field(description="Base64-encoded EML or MSG file content")


class FilePayload(APIModel):
    file: bytes = Field(description="Raw EML or MSG file bytes")

    @field_validator("file")
    @classmethod
    def eml_file_must_be_eml(cls, v: bytes):
        if not is_eml_or_msg_file(v):
            raise ValueError("Invalid file format.")
        return v
