from pydantic import BaseModel, Field


class DatabaseInfo(BaseModel):
    name: str


class DatabaseListResponse(BaseModel):
    databases: list[DatabaseInfo]


class SchemaInfo(BaseModel):
    name: str


class SchemaListResponse(BaseModel):
    database: str
    schemas: list[SchemaInfo]


class TableInfo(BaseModel):
    name: str
    schema: str


class TableListResponse(BaseModel):
    database: str
    schema: str
    tables: list[TableInfo]


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    nullable: bool
    ordinal_position: int


class ColumnListResponse(BaseModel):
    database: str
    schema: str
    table: str
    columns: list[ColumnInfo]