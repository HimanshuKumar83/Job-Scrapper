from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SourceConfig

router = APIRouter(prefix="/api", tags=["sources"])


@router.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    rows = db.query(SourceConfig).order_by(SourceConfig.name).all()
    return {"items": rows}
