from pydantic import BaseModel, Field


class ConnectionTestRequest(BaseModel):
    table_name: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the table to execute the test query against.",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=1000,
        description="Maximum number of sample rows to retrieve.",
    )


class ConnectionTestResponse(BaseModel):
    connection_id: str = Field(
        description="Unique identifier of the tested connection.",
    )
    status: str = Field(
        description="Status of the connection test (e.g., 'successful').",
    )
    message: str = Field(
        description="Human-readable result summary message.",
    )
    columns: list[str] = Field(
        description="List of column names returned by the query.",
    )
    rows: list[list] = Field(
        description="List of sample data rows fetched from the table.",
    )
    tested_at: str = Field(
        description="ISO 8601 formatted UTC timestamp of when the test was run.",
    )