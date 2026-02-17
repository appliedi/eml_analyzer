from datetime import datetime

from pydantic import Field

from .api_model import APIModel


class Hash(APIModel):
    md5: str = Field(description="MD5 hash of the content")
    sha1: str = Field(description="SHA-1 hash of the content")
    sha256: str = Field(description="SHA-256 hash of the content")
    sha512: str = Field(description="SHA-512 hash of the content")


class Attachment(APIModel):
    raw: str = Field(description="Base64-encoded raw attachment content")
    filename: str = Field(description="Original filename of the attachment")
    size: int = Field(description="File size in bytes")
    extension: str | None = Field(
        default=None, description="File extension (e.g. '.pdf', '.docx')"
    )
    hash: Hash = Field(description="Cryptographic hashes of the attachment")
    mime_type: str = Field(description="Full MIME type (e.g. 'application/pdf')")
    mime_type_short: str = Field(description="Short MIME type (e.g. 'pdf')")
    content_id: str | None = Field(
        default=None, description="Content-ID header for inline attachments"
    )
    content_header: dict[str, list[str | int]] = Field(
        description="MIME content headers of the attachment part"
    )


class Body(APIModel):
    content_type: str | None = Field(
        default=None, description="MIME content type (e.g. 'text/html', 'text/plain')"
    )
    hash: str = Field(description="SHA-256 hash of the body content")
    content_header: dict[str, list[str | int]] = Field(
        description="MIME content headers of the body part"
    )
    content: str = Field(description="Decoded body content as text")
    urls: list[str] = Field(description="URLs extracted from the body")
    emails: list[str] = Field(description="Email addresses extracted from the body")
    domains: list[str] = Field(description="Domain names extracted from the body")
    ip_addresses: list[str] = Field(description="IP addresses extracted from the body")


class Received(APIModel):
    by: list[str] | None = Field(
        default=None, description="Servers that received the message"
    )
    date: datetime | str = Field(description="Timestamp when the message was received")
    for_: list[str] | None = Field(
        default=None,
        alias="for",
        description="Intended recipients from the Received header",
    )
    from_: list[str] | None = Field(
        default=None,
        alias="from",
        description="Sending server from the Received header",
    )
    src: str = Field(description="Raw Received header string")
    with_: str | None = Field(
        default=None, alias="with", description="Protocol used (e.g. 'SMTP', 'ESMTPS')"
    )
    delay: int | None = Field(
        default=None,
        description="Delay in seconds between consecutive Received headers",
    )


class Header(APIModel):
    message_id: str | None = Field(default=None, description="Message-ID header value")
    subject: str = Field(description="Email subject line")
    defect: list[str] | None = Field(
        default=None, description="Parsing defects detected in the email headers"
    )
    from_: str | None = Field(
        default=None, alias="from", description="Sender address from the From header"
    )
    to: list[str] = Field(description="Recipient addresses from the To header")
    cc: list[str] | None = Field(default=None, description="CC recipient addresses")
    date: datetime | None = Field(default=None, description="Date header value")
    received_email: list[str] | None = Field(
        default=None, description="Email addresses extracted from Received headers"
    )
    received_foremail: list[str] | None = Field(
        default=None, description="For-email addresses extracted from Received headers"
    )
    received_domain: list[str] | None = Field(
        default=None, description="Domains extracted from Received headers"
    )
    received_ip: list[str] | None = Field(
        default=None, description="IP addresses extracted from Received headers"
    )
    received_src: str | None = Field(
        default=None, description="Source server from the first Received header"
    )
    received: list[Received] = Field(description="Parsed Received headers in order")
    header: dict[str, list[str | int]] = Field(
        description="All raw email headers as key-value pairs"
    )


class Eml(APIModel):
    attachments: list[Attachment] = Field(
        description="File attachments extracted from the email"
    )
    bodies: list[Body] = Field(
        description="Email body parts (text/plain, text/html, etc.)"
    )
    header: Header = Field(description="Parsed email headers")
