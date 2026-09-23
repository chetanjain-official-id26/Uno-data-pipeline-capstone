from typing import Optional

from pydantic import BaseModel, Field
from src.enums.enum import PipelineStatus

class Pipeline(BaseModel):

    id: Optional[str] = Field(
        default=None,
        alias="_id"
    )

    name: str

    source_id: str

    status: str = PipelineStatus.DRAFT.value

    class Config:
        populate_by_name = True