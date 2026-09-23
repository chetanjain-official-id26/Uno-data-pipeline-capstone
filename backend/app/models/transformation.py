from typing import Optional

from pydantic import BaseModel, Field


class Transformation(BaseModel):

    id: Optional[str] = Field(
        default=None,
        alias="_id"
    )

    pipeline_id: str

    step_order: int

    name: str

    sql_query: str

    output_view: str

    enabled: bool = True

    class Config:
        populate_by_name = True