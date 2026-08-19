from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import SessionLocal
from app.db.models import IngestionError, IngestionRun, Job, SourceConfig
from app.ingestion.circuit_breaker import CircuitBreaker
from app.ingestion.health import SourceHealthRegistry
from app.ingestion.pipeline import deduplicate_jobs, normalize_job
from app.sources.rss_adapter import RSSJobAdapter
from app.sources.remote_ok_adapter import RemoteOKJobAdapter
from app.sources.sandbox_adapter import SandboxJobAdapter

settings = get_settings()
logger = logging.getLogger("jobpulse")
source_health = SourceHealthRegistry()


class IngestionService:
    def __init__(self) -> None:
        self.adapters = {
            "jobicy": RSSJobAdapter(),
            "remoteok": RemoteOKJobAdapter(),
            "sandbox": SandboxJobAdapter(),
        }

    async def run_ingestion(self, source_name: str | None = None) -> dict[str, Any]:
        source_name = source_name or settings.primary_source
        db = SessionLocal()
        run = IngestionRun(source=source_name, started_at=datetime.now(timezone.utc), status="running")
        db.add(run)
        db.commit()

        try:
            adapter = self.adapters.get(source_name)
            if adapter is None:
                raise ValueError(f"Unknown source: {source_name}")
            jobs = await adapter.fetch_jobs()
            if not jobs:
                run.status = "success"
                run.jobs_found = 0
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
                return {"status": "success", "jobs_processed": 0, "source": source_name, "fallback_used": source_name != settings.primary_source}

            metrics = self._ingest_jobs(db, jobs, source_name)
            run.jobs_found = metrics["jobs_found"]
            run.jobs_inserted = metrics["jobs_inserted"]
            run.jobs_updated = metrics["jobs_updated"]
            run.jobs_skipped = metrics["jobs_skipped"]
            run.status = "success"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            return metrics
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            self._record_error(source_name, exc)
            if source_name == settings.primary_source and settings.fallback_source != source_name:
                fallback_result = await self.run_ingestion(settings.fallback_source)
                fallback_result["fallback_used"] = True
                fallback_result["primary_error"] = exc.__class__.__name__
                return fallback_result
            raise
        finally:
            db.close()

    def _ingest_jobs(self, db: Session, jobs: list, source_name: str) -> dict[str, Any]:
        existing_hashes = {row[0] for row in db.query(Job.content_hash).all()}
        existing_external_ids = {row[0] for row in db.query(Job.external_id).filter(Job.source == source_name).all()}

        parsed = []
        for job in jobs:
            try:
                item = job.model_dump() if hasattr(job, "model_dump") else dict(job)
                item["id"] = item.get("external_id")
                parsed.append(normalize_job(item, source_name))
            except Exception:
                continue

        accepted, duplicates, invalid = deduplicate_jobs(parsed, existing_hashes, existing_external_ids)
        inserted = updated = 0

        for job in accepted:
            existing = db.query(Job).filter(Job.source == job.source, Job.external_id == job.external_id).first()
            if existing:
                existing.title = job.title
                existing.company = job.company
                existing.location = job.location
                existing.description = job.description
                existing.employment_type = job.employment_type
                existing.url = job.url
                existing.posted_at = job.posted_at
                existing.fetched_at = job.fetched_at
                existing.salary_min = job.salary_min
                existing.salary_max = job.salary_max
                existing.currency = job.currency
                existing.remote = job.remote
                existing.skills = job.skills
                existing.raw_payload = job.raw_payload
                existing.content_hash = job.content_hash
                existing.updated_at = datetime.now(timezone.utc)
                updated += 1
            else:
                db.add(
                    Job(
                        source=job.source,
                        external_id=job.external_id,
                        title=job.title,
                        company=job.company,
                        location=job.location,
                        description=job.description,
                        employment_type=job.employment_type,
                        url=job.url,
                        posted_at=job.posted_at,
                        fetched_at=job.fetched_at,
                        salary_min=job.salary_min,
                        salary_max=job.salary_max,
                        currency=job.currency,
                        remote=job.remote,
                        skills=job.skills,
                        raw_payload=job.raw_payload,
                        content_hash=job.content_hash,
                    )
                )
                inserted += 1

        db.commit()
        source_cfg = db.query(SourceConfig).filter(SourceConfig.name == source_name).first()
        if source_cfg is None:
            source_cfg = SourceConfig(name=source_name, type="rss", enabled=True, status="healthy")
            db.add(source_cfg)
        source_cfg.last_success_at = datetime.now(timezone.utc)
        source_cfg.consecutive_failures = 0
        source_cfg.status = "healthy"
        db.commit()

        logger.info(
            "ingestion_completed",
            extra={
                "source": source_name,
                "jobs_found": len(jobs),
                "jobs_inserted": inserted,
                "jobs_updated": updated,
                "jobs_skipped": duplicates + invalid,
                "duration_ms": 0,
            },
        )
        return {
            "status": "success",
            "jobs_processed": inserted + updated,
            "jobs_found": len(jobs),
            "jobs_inserted": inserted,
            "jobs_updated": updated,
            "jobs_skipped": duplicates + invalid,
            "source": source_name,
            "fallback_used": False,
        }

    def _record_error(self, source_name: str, exc: Exception) -> None:
        db = SessionLocal()
        db.add(
            IngestionError(
                source=source_name,
                timestamp=datetime.now(timezone.utc),
                error_type=exc.__class__.__name__,
                status_code=getattr(getattr(exc, "response", None), "status_code", None),
                message=str(exc),
                retry_count=0,
            )
        )
        source_cfg = db.query(SourceConfig).filter(SourceConfig.name == source_name).first()
        if source_cfg is None:
            source_cfg = SourceConfig(name=source_name, type="rss", enabled=True, status="degraded")
            db.add(source_cfg)
        source_cfg.last_failure_at = datetime.now(timezone.utc)
        source_cfg.consecutive_failures = (source_cfg.consecutive_failures or 0) + 1
        if source_cfg.consecutive_failures >= settings.circuit_breaker_failure_threshold:
            source_cfg.status = "degraded"
        db.commit()
        db.close()


service = IngestionService()


def start_scheduler() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(service.run_ingestion, IntervalTrigger(minutes=settings.ingestion_interval_minutes), args=[settings.primary_source])
    return scheduler


scheduler = start_scheduler()
