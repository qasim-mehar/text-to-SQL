from functools import lru_cache
from fastapi import Depends
from sqlalchemy import Engine

from app.core.database import get_engine
from app.core.config import get_settings
from app.features.text_to_sql.service import (
    SchemaService,
    LLMService,
    QueryService,
    TextToSQLOrchestrator,
)


@lru_cache()
def get_llm_service() -> LLMService:
    settings = get_settings()
    return LLMService(api_key=settings.MISTRAL_API_KEY, model_name=settings.MODEL_NAME)


def get_schema_service(engine: Engine = Depends(get_engine)) -> SchemaService:
    return SchemaService(engine)


def get_query_service(engine: Engine = Depends(get_engine)) -> QueryService:
    return QueryService(engine)


def get_orchestrator(
    schema_service: SchemaService = Depends(get_schema_service),
    llm_service: LLMService = Depends(get_llm_service),
    query_service: QueryService = Depends(get_query_service),
) -> TextToSQLOrchestrator:
    return TextToSQLOrchestrator(schema_service, llm_service, query_service)
