from typing import Any

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):
    connection_id: str = Field(
        ...,
        min_length=1,
        description="MongoDB connection ID.",
    )


class PreviewResponse(BaseModel):
    connection_id: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int