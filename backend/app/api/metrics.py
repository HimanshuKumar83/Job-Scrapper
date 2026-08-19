from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import IngestionError, IngestionRun, Job

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    total_jobs = db.query(Job).count()
    successful_runs = db.query(IngestionRun).filter(IngestionRun.status == "success").count()
    failed_runs = db.query(IngestionRun).filter(IngestionRun.status == "failed").count()
    duplicate_jobs = db.query(IngestionRun).with_entities(IngestionRun.jobs_skipped).all()
    duplicate_count = sum(row[0] or 0 for row in duplicate_jobs)
    today = datetime.now(timezone.utc).date()
    today_runs = [run for run in db.query(IngestionRun).all() if run.started_at and run.started_at.date() == today]
    jobs_fetched_today = sum(run.jobs_found or 0 for run in today_runs)
    avg_duration = 0.0
    runs = db.query(IngestionRun).filter(IngestionRun.completed_at.is_not(None), IngestionRun.started_at.is_not(None)).all()
    if runs:
        durations = []
        for item in runs:
            if item.started_at and item.completed_at:
                durations.append((item.completed_at - item.started_at).total_seconds())
        if durations:
            avg_duration = sum(durations) / len(durations)
    return {
        "total_jobs": total_jobs,
        "jobs_fetched_today": jobs_fetched_today,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "duplicate_jobs": duplicate_count,
        "average_ingestion_time_seconds": round(avg_duration, 2),
    }
