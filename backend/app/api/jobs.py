from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Job

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if source:
        query = query.filter(Job.source == source)

    total = query.count()
    rows = query.order_by(Job.posted_at.desc().nullslast()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": rows, "page": page, "page_size": page_size, "total": total}


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
