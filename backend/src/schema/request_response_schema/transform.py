from typing import Any, Optional

from pydantic import BaseModel, Field


class TransformationCreate(BaseModel):
    step_order: int = Field(
        ...,
        ge=1,
        description="Sequence order of the transformation step.",
    )
    sql_query: str = Field(
        ...,
        min_length=1,
        description="SQL transformation query.",
    )
    input_view: str = Field(
        default="raw_data",
        min_length=1,
        description="Input view/table name used by the transformation.",
    )
    connection_id: str = Field(
        ...,
        min_length=1,
        description="ID of the stored database connection.",
    )


class TransformationUpdate(BaseModel):
    sql_query: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated SQL query for the transformation.",
    )
    input_view: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated input view name.",
    )
    output_view: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated output view name.",
    )


class TransformStepResponse(BaseModel):
    id: str = Field(
        description="Unique identifier of the transformation step.",
    )
    connection_id: str = Field(
        description="ID of the associated database connection.",
    )
    step_order: int = Field(
        description="Sequence order of the transformation step.",
    )
    input_view: str = Field(
        description="Name of the input view or source table used.",
    )
    output_view: str = Field(
        description="Name of the generated output view.",
    )
    sql_query: str = Field(
        description="SQL query executed for this step.",
    )
    created_at: Any = Field(
        description="Timestamp when the step was created.",
    )
    updated_at: Any = Field(
        description="Timestamp when the step was last updated.",
    )


class PreviewRequest(BaseModel):
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of rows to return in the preview.",
    )


class PreviewResponse(BaseModel):
    columns: list[str] = Field(
        description="List of column names returned by the preview.",
    )
    rows: list[dict[str, Any]] = Field(
        description="List of data rows represented as key-value pairs.",
    )
    row_count: int = Field(
        description="Total number of rows returned in the preview.",
    )
    step_order: int = Field(
        description="The transformation step order corresponding to this preview.",
    )