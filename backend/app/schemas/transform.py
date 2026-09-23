from datetime import datetime

from pydantic import BaseModel, Field


class TransformationCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    sql_query: str = Field(..., min_length=1)
    input_view: str = Field(default="raw_data", min_length=1)


class TransformationUpdate(BaseModel):
    sql_query: str | None = Field(default=None, min_length=1)
    input_view: str | None = Field(default=None, min_length=1)
    output_view: str | None = Field(default=None, min_length=1)


class TransformStepResponse(BaseModel):
    id: str
    pipeline_id: str
    step_order: int
    input_view: str
    output_view: str
    sql_query: str
    created_at: datetime
    updated_at: datetime


class TransformPreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict]
    row_count: int