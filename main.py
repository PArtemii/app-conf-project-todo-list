import logging
import os

import psycopg
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Project Name",
    description="Project description",
    version="0.2.0",
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
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "DATABASE_URL is not set",
            },
        )

    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
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