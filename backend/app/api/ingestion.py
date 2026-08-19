from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import get_db
from app.db.models import IngestionError, IngestionRun, SourceConfig
from app.services.ingestion_service import service

router = APIRouter(prefix="/api", tags=["ingestion"])
settings = get_settings()


@router.get("/ingestion/runs")
async def list_runs(db: Session = Depends(get_db)):
    runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(20).all()
    return {"items": runs}


@router.post("/ingestion/run")
async def run_ingestion(db: Session = Depends(get_db)):
    try:
        result = await service.run_ingestion(source_name=settings.primary_source)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"message": "Ingestion failed", "source": settings.primary_source})


@router.get("/ingestion/errors")
async def list_errors(db: Session = Depends(get_db)):
    rows = db.query(IngestionError).order_by(IngestionError.timestamp.desc()).limit(20).all()
    return {"items": rows}
