from typing import Any

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):

    limit: int = Field(
        default=100,
        ge=1,
        le=1000
    )


class PreviewResponse(BaseModel):

    columns: list[str]

    rows: list[dict[str, Any]]

    row_count: int

    step_order: int