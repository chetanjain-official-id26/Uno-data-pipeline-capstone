from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TargetWriteMode(str, Enum):
    APPEND = "APPEND"
    OVERWRITE = "OVERWRITE"


class TargetCreate(BaseModel):
    connection_id: str = Field(..., min_length=1)
    target_table: str = Field(..., min_length=1, max_length=255)
    write_mode: TargetWriteMode = TargetWriteMode.APPEND


class TargetUpdate(BaseModel):
    connection_id: str | None = Field(default=None, min_length=1)
    target_table: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    write_mode: TargetWriteMode | None = None


class TargetResponse(BaseModel):
    id: str
    pipeline_id: str
    connection_id: str
    target_table: str
    write_mode: TargetWriteMode
    created_at: datetime
    updated_at: datetime


class TargetTestResponse(BaseModel):
    success: bool
    message: str


class TargetRunResponse(BaseModel):
    success: bool
    pipeline_id: str
    target_table: str
    write_mode: TargetWriteMode
    rows_written: int
    message: str