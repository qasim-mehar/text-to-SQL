from pydantic import BaseModel, Field
from typing import Any


class GenerateRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Natural language question")


class GenerateResponse(BaseModel):
    sql: str
    success: bool
    retry_count: int = 0


class ExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=6, description="SQL SELECT query to execute")


class ExecuteResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: float


class ColumnInfo(BaseModel):
    name: str
    type: str


class ForeignKeyInfo(BaseModel):
    from_col: str
    to_table: str
    to_column: str


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    foreign_keys: list[ForeignKeyInfo]


class SchemaResponse(BaseModel):
    tables: list[TableInfo]


class ErrorResponse(BaseModel):
    detail: str
    type: str
