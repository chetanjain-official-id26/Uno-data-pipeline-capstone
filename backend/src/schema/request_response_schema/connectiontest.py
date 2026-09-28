from typing import Any

from pydantic import BaseModel, Field


class ConnectionTestRequest(BaseModel):
    table_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description=(
            "Name of the source table to test and store "
            "for this connection."
        ),
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=1000,
        description=(
            "Maximum number of sample rows to retrieve "
            "during the connection test."
        ),
    )


class ConnectionTestResponse(BaseModel):
    connection_id: str = Field(
        description="Unique identifier of the tested connection.",
    )

    status: str = Field(
        description=(
            "Status of the connection test, "
            "for example 'successful'."
        ),
    )

    message: str = Field(
        description="Human-readable result summary message.",
    )

    columns: list[str] = Field(
        description="Column names returned by the test query.",
    )

    rows: list[list[Any]] = Field(
        description="Sample rows returned by the test query.",
    )

    tested_at: str = Field(
        description=(
            "ISO 8601 formatted UTC timestamp "
            "of when the test was run."
        ),
    )