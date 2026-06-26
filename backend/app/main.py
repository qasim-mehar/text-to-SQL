import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.features.text_to_sql.router import router as text_to_sql_router
from app.features.text_to_sql.dependencies import get_llm_service


import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# ... your routes ...

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize singleton services on startup."""
    logger.info("Starting QueryBridge API...")
    settings = get_settings()
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Model: {settings.MODEL_NAME}")
    # Warm up the LLM service singleton so it's ready on first request
    get_llm_service()
    logger.info("LLM service initialized.")
    yield
    logger.info("Shutting down QueryBridge API.")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="QueryBridge API",
        description="Text-to-SQL API powered by Mistral AI and LangChain",
        version="1.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS — allow the Vite dev server origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5175",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global fallback exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "type": "internal_error",
            },
        )

    # Mount feature routers under /api/v1
    app.include_router(text_to_sql_router, prefix="/api/v1")

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "QueryBridge API"}

    return app


app = create_app()
