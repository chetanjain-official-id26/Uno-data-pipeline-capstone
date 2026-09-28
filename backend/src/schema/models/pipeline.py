from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.enums.enum import PipelineStatus


class Pipeline(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(
        default=None,
        alias="_id",
    )
    name: str = Field(
        min_length=1,
        max_length=200,
    )
    source_id: str | None = None
    source_table: str | None = None
    status: str = PipelineStatus.DRAFT.value
    created_at: datetime | None = None
    updated_at: datetime | None = None