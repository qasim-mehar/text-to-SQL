import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.features.text_to_sql.schemas import (
    GenerateRequest,
    GenerateResponse,
    ExecuteRequest,
    ExecuteResponse,
    SchemaResponse,
)
from app.features.text_to_sql.dependencies import (
    get_orchestrator,
    get_schema_service,
    get_query_service,
)
from app.features.text_to_sql.service import (
    TextToSQLOrchestrator,
    SchemaService,
    QueryService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/text-to-sql", tags=["text-to-sql"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_sql(
    request: GenerateRequest,
    orchestrator: TextToSQLOrchestrator = Depends(get_orchestrator),
):
    """Generate SQL from a natural language question."""
    try:
        response = orchestrator.generate(request.question)
        return response
    except Exception as e:
        logger.error(f"SQL generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")


@router.post("/execute", response_model=ExecuteResponse)
async def execute_sql(
    request: ExecuteRequest,
    orchestrator: TextToSQLOrchestrator = Depends(get_orchestrator),
):
    """Execute a SQL query with self-correction on failure."""
    try:
        result, retry_count = orchestrator.execute_with_correction(request.sql)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
    except Exception as e:
        logger.error(f"Query execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/schema", response_model=SchemaResponse)
async def get_schema(
    schema_service: SchemaService = Depends(get_schema_service),
):
    """Get the database schema for display."""
    try:
        return schema_service.get_schema_response()
    except Exception as e:
        logger.error(f"Schema extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Schema extraction failed: {str(e)}")
