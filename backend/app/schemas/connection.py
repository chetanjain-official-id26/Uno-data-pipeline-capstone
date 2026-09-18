from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CreateConnectionRequest(BaseModel):
    """Request payload for creating an external data connection."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    type: Literal["cockroachdb"]

    host: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    port: int = Field(
        default=26257,
        ge=1,
        le=65535,
    )

    database: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=2048,
    )


class ConnectionResponse(BaseModel):
    """Safe representation returned to the client.

    Credentials are intentionally excluded.
    """

    id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    status: str