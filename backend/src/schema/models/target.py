from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from src.schema.request_response_schema.target import (
    TargetWriteMode,
)


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


def build_target_document(
    *,
    pipeline_id: str,
    connection_id: str,
    target_table: str,
    write_mode: str = TargetWriteMode.APPEND.value,
) -> dict[str, Any]:
    """Build the MongoDB document for a pipeline target."""

    now = utc_now()

    return {
        "pipeline_id": pipeline_id,
        "connection_id": connection_id,
        "target_table": target_table,
        "write_mode": write_mode,
        "created_at": now,
        "updated_at": now,
    }


class Target(BaseModel):
    """MongoDB representation of a pipeline target."""

    id: str | None = Field(
        default=None,
        alias="_id",
        description="Unique MongoDB identifier.",
    )

    pipeline_id: str = Field(
        min_length=1,
        description="ID of the pipeline this target belongs to.",
    )

    connection_id: str = Field(
        min_length=1,
        description="ID of the database connection used as the target.",
    )

    target_table: str = Field(
        min_length=1,
        max_length=255,
        description="Destination table name.",
    )

    write_mode: TargetWriteMode = Field(
        default=TargetWriteMode.APPEND,
        description="How rows should be written to the target table.",
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when the target was created.",
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        description="Timestamp when the target was last updated.",
    )

    class Config:
        populate_by_name = True