import json
import time
import logging
from typing import Any
from sqlalchemy import inspect as sa_inspect, text
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.database import get_engine
from app.core.config import get_settings
from app.features.text_to_sql.schemas import (
    SchemaResponse, TableInfo, ColumnInfo, ForeignKeyInfo,
    ExecuteResponse, GenerateResponse,
)

logger = logging.getLogger(__name__)

BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "REPLACE"]


class SchemaService:
    """Extracts and formats database schema for both LLM context and API responses."""

    def __init__(self, engine):
        self.engine = engine

    def get_schema_string(self) -> str:
        """Returns JSON string schema for LLM consumption (exact logic from main.py get_schema())."""
        inspector = sa_inspect(self.engine)
        schema = {}
        for table in inspector.get_table_names():
            columns = [
                f"{col['name']} ({col['type']})" for col in inspector.get_columns(table)
            ]
            fks = [
                f"{fk['constrained_columns']} → {fk['referred_table']}({fk['referred_columns']})"
                for fk in inspector.get_foreign_keys(table)
            ]
            schema[table] = {"columns": columns, "foreign_keys": fks or []}
        return json.dumps(schema, indent=2)

    def get_schema_response(self) -> SchemaResponse:
        """Returns structured schema for API response."""
        inspector = sa_inspect(self.engine)
        tables = []
        for table_name in inspector.get_table_names():
            raw_columns = inspector.get_columns(table_name)
            raw_fks = inspector.get_foreign_keys(table_name)

            columns = [
                ColumnInfo(name=col["name"], type=str(col["type"]))
                for col in raw_columns
            ]
            foreign_keys = [
                ForeignKeyInfo(
                    from_col=", ".join(fk["constrained_columns"]),
                    to_table=fk["referred_table"],
                    to_column=", ".join(fk["referred_columns"]),
                )
                for fk in raw_fks
            ]
            tables.append(TableInfo(name=table_name, columns=columns, foreign_keys=foreign_keys))
        return SchemaResponse(tables=tables)


class LLMService:
    """Handles SQL generation using LangChain + Mistral AI."""

    def __init__(self, api_key: str, model_name: str):
        self.model = ChatMistralAI(model=model_name, temperature=0, api_key=api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert SQLite query generator for a company analytics database.

RULES:
1. Output ONLY the raw SQL query — no markdown, no backticks, no explanation.
2. Never use SELECT * — always name specific columns.
3. Use table aliases for readability (e.g. e for employees).
4. Use proper JOINs when data spans multiple tables.
5. If the question is unrelated to the schema, output exactly: NULL

SCHEMA:
{schema}""",
            ),
            ("human", "{question}"),
        ])
        # Exact LCEL chain from main.py
        self.sql_chain = self.prompt | self.model | StrOutputParser() | self._clean_sql

        # Correction chain for self-correction on SQL execution failure
        self.correction_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert SQLite query generator.
Fix the SQL error below and output ONLY the corrected raw SQL — no markdown, no backticks.
SCHEMA:
{schema}""",
            ),
            ("human", "Original SQL:\n{sql}\n\nError:\n{error}\n\nFixed SQL:"),
        ])
        self.correction_chain = self.correction_prompt | self.model | StrOutputParser() | self._clean_sql

    @staticmethod
    def _clean_sql(raw: str) -> str:
        """Strips markdown/backtick wrapping (exact logic from main.py clean_sql())."""
        sql = raw.strip()
        if sql.startswith("```"):
            sql = sql.split("\n", 1)[-1]
            sql = sql.rsplit("```", 1)[0]
        return sql.strip()

    def generate_sql(self, question: str, schema: str) -> str:
        """Invokes the LCEL chain to generate SQL from a natural language question."""
        return self.sql_chain.invoke({"schema": schema, "question": question})

    def correct_sql(self, sql: str, error: str, schema: str) -> str:
        """Attempts to fix SQL given an error message (self-correction)."""
        return self.correction_chain.invoke({"schema": schema, "sql": sql, "error": error})


class QueryService:
    """Validates and executes SQL queries safely."""

    def __init__(self, engine):
        self.engine = engine

    def validate_sql(self, sql: str) -> None:
        """Raises ValueError if SQL is not a safe SELECT statement."""
        clean = sql.strip().upper()
        if not clean.startswith("SELECT"):
            raise ValueError(f"Only SELECT queries are allowed. Got: {sql[:50]}")
        for keyword in BLOCKED_KEYWORDS:
            if keyword in clean:
                raise ValueError(f"Blocked SQL keyword detected: {keyword}")

    def execute(self, sql: str) -> ExecuteResponse:
        """Executes SQL and returns structured results (ports run_query() from main.py)."""
        self.validate_sql(sql)
        start = time.time()
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            cols = list(result.keys())
        elapsed_ms = (time.time() - start) * 1000
        row_dicts = [dict(zip(cols, row)) for row in rows]
        # Convert non-serializable types to strings for JSON safety
        serializable_rows = [
            {
                k: (str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v)
                for k, v in row.items()
            }
            for row in row_dicts
        ]
        return ExecuteResponse(
            columns=cols,
            rows=serializable_rows,
            row_count=len(serializable_rows),
            execution_time_ms=round(elapsed_ms, 2),
        )


class TextToSQLOrchestrator:
    """Orchestrates schema extraction → SQL generation → execution with self-correction."""

    def __init__(
        self,
        schema_service: SchemaService,
        llm_service: LLMService,
        query_service: QueryService,
    ):
        self.schema_service = schema_service
        self.llm_service = llm_service
        self.query_service = query_service

    def generate(self, question: str) -> GenerateResponse:
        """Generates SQL from a natural language question."""
        schema = self.schema_service.get_schema_string()
        sql = self.llm_service.generate_sql(question, schema)
        return GenerateResponse(sql=sql, success=True, retry_count=0)

    def execute_with_correction(self, sql: str) -> tuple[ExecuteResponse, int]:
        """Executes SQL with one self-correction retry on failure."""
        try:
            result = self.query_service.execute(sql)
            return result, 0
        except Exception as e:
            error_msg = str(e)
            logger.warning(
                f"SQL execution failed, attempting self-correction. Error: {error_msg}"
            )
            schema = self.schema_service.get_schema_string()
            corrected_sql = self.llm_service.correct_sql(sql, error_msg, schema)
            result = self.query_service.execute(corrected_sql)
            return result, 1
