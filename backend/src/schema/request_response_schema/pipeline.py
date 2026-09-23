from datetime import datetime

from pydantic import BaseModel, Field


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    
    source_table: str = Field(..., min_length=1, max_length=255)


class PipelineUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    source_connection_id: str | None = Field(
        default=None,
        min_length=1,
    )

    source_table: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class PipelineResponse(BaseModel):
    id: str
    name: str
    source_connection_id: str
    source_table: str
    status: str
    created_at: datetime
    updated_at: datetime