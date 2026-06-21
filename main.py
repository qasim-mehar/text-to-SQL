"""
QueryBridge — High-Accuracy Text-to-SQL Pipeline
Key upgrades over basic version:
  - DDL schema format (LLMs understand CREATE TABLE better than JSON)
  - SQL anti-pattern rules in prompt (teaches what NOT to do)
  - Few-shot examples covering joins, window functions, CTEs, self-joins
  - Query complexity classifier (simple vs analytical vs recursive)
  - Self-correcting retry loop
  - Pre-aggregation pattern enforced via prompt
"""

from sqlalchemy import create_engine, inspect, text, exc
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os, re, logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("QueryBridge")

DB_URL = os.getenv("DATABASE_URL", "sqlite:///company.db")
MODEL_NAME = os.getenv("LLM_MODEL", "mistral-medium-3-5")
MAX_ROWS = int(os.getenv("MAX_ROWS", "500"))

#  Single engine + model instance
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
model = ChatMistralAI(model=MODEL_NAME, temperature=0)

FORBIDDEN = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "CREATE",
}


# 1. SCHEMA — DDL format, includes types + FK relationships


def get_schema() -> str:
    inspector = inspect(engine)
    ddl_parts = []
    for table in inspector.get_table_names():
        cols = inspector.get_columns(table)
        fks = inspector.get_foreign_keys(table)
        col_defs = [f"  {c['name']} {c['type']}" for c in cols]
        fk_defs = [
            f"  FOREIGN KEY ({', '.join(fk['constrained_columns'])}) "
            f"REFERENCES {fk['referred_table']} ({', '.join(fk['referred_columns'])})"
            for fk in fks
        ]
        body = ",\n".join(col_defs + fk_defs)
        ddl_parts.append(f"CREATE TABLE {table} (\n{body}\n);")
    return "\n\n".join(ddl_parts)


SCHEMA = get_schema()
logger.info(f"Schema loaded: {SCHEMA.count('CREATE TABLE')} tables.")
