import logging

from config import get_settings

import psycopg
from fastapi import FastAPI
from fastapi.responses import JSONResponse

settings = get_settings()

app = FastAPI(
    title="Project Name",
    description="Project description",
    version="0.2.0",
    docs_url="/docs" if settings.app_env == "dev" else None,
    redoc_url="/redoc" if settings.app_env == "dev" else None,
    openapi_url="/openapi.json" if settings.app_env == "dev" else None,
)

TEAM_NAME = "404"

logger = logging.getLogger("uvicorn.error")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    """Приложение работает и база данных отвечает на запрос."""
    """Проверка готовности API через запрос SELECT 1 к PostgreSQL."""
    database_url = settings.database_url

    if not database_url:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "DATABASE_URL is not set",
            },
        )

    try:
        with psycopg.connect(database_url, connect_timeout=settings.db_connect_timeout,) as conn:
            conn.execute("SELECT 1")
    except psycopg.Error as exc:
        logger.warning("Health check: database is unavailable: %s", exc)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "unavailable",
            },
        )

    return {"status": "healthy", "database": "ok"}


@app.get("/version")
async def version():
    """Версия приложения и команда-владелец."""
    return {"version": app.version, "team": TEAM_NAME}
