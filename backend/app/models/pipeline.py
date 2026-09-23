from typing import Optional

from pydantic import BaseModel, Field


class Pipeline(BaseModel):

    id: Optional[str] = Field(
        default=None,
        alias="_id"
    )

    name: str

    source_id: str

    status: str = "DRAFT"

    class Config:
        populate_by_name = True