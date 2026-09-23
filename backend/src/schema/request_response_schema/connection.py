from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


from datetime import datetime




class CreateConnectionRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    type: str = Field(
        ...,
        min_length=1,
    )

    host: str = Field(
        ...,
        min_length=1,
    )

    port: int = Field(
        ...,
        gt=0,
        le=65535,
    )

    database: str = Field(
        ...,
        min_length=1,
    )

    username: str = Field(
        ...,
        min_length=1,
    )

    password: str = Field(
        ...,
        min_length=1,
    )


class UpdateConnectionRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    type: str | None = None

    host: str | None = None

    port: int | None = Field(
        default=None,
        gt=0,
        le=65535,
    )

    database: str | None = None

    username: str | None = None

    password: str | None = None


class ConnectionResponse(BaseModel):
    """Safe representation returned to the client.

    Credentials are intentionally excluded.
    """

    id: str 
    name: str
    pipeline_id: str
    type: str
    host: str
    port: int
    database: str
    username: str
    status: str