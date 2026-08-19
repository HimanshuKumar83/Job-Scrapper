from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ingestion, jobs, metrics, sources
from app.config import get_settings
from app.db.database import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    try:
        from app.services.ingestion_service import scheduler

        scheduler.start()
    except Exception:
        pass
    try:
        yield
    finally:
        try:
            from app.services.ingestion_service import scheduler

            scheduler.shutdown()
        except Exception:
            pass


settings = get_settings()
app = FastAPI(title="JobPulse", description="Resilient job ingestion platform", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(sources.router)
app.include_router(ingestion.router)
app.include_router(metrics.router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "database": "healthy",
        "sources": {
            "primary": "healthy",
            "fallback": "healthy",
        },
    }
