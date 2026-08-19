from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable

from app.config import get_settings
from app.schemas.jobs import NormalizedJob, RawJob


def safe_get(mapping: dict[str, Any] | None, *keys: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    current = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def validate_response(payload: Any, expected_key: str = "jobs") -> bool:
    if payload is None:
        return False
    if isinstance(payload, dict):
        return isinstance(payload.get(expected_key), list)
    return False


def parse_raw_jobs(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        items = payload.get("jobs", [])
        return [item for item in items if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def normalize_job(item: dict[str, Any], source_name: str) -> NormalizedJob:
    title = str(item.get("title") or "Untitled job").strip()
    if not title:
        raise ValueError("Job title is required")

    posted_at = item.get("posted_at")
    dt = None
    if posted_at:
        try:
            if isinstance(posted_at, str):
                dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            elif hasattr(posted_at, "isoformat"):
                dt = posted_at
        except ValueError:
            dt = None

    payload = json.dumps(item, default=str, sort_keys=True)
    content_hash = hashlib.sha256(f"{source_name}:{(item.get('title') or '')}:{(item.get('company') or '')}:{(item.get('location') or '')}:{(item.get('url') or '')}".strip().lower().replace('\n', ' ').replace('\r', ' ') .replace('  ', ' ')
                                  .encode()).hexdigest()

    normalized = NormalizedJob(
        source=source_name,
        external_id=str(item.get("id") or item.get("slug") or item.get("url") or item.get("external_id") or item.get("title") or "unknown"),
        title=title,
        company=item.get("company") or item.get("company_name") or None,
        location=item.get("location") or item.get("remote_location") or None,
        description=item.get("description") or item.get("job_description") or None,
        employment_type=item.get("employment_type") or item.get("type") or None,
        url=item.get("url") or item.get("apply_url") or None,
        posted_at=dt,
        fetched_at=datetime.now(timezone.utc),
        salary_min=item.get("salary_min"),
        salary_max=item.get("salary_max"),
        currency=item.get("currency") or None,
        remote=item.get("remote") if isinstance(item.get("remote"), bool) else None,
        skills=",".join(item.get("skills") or []) if isinstance(item.get("skills"), list) else None,
        raw_payload=payload,
        content_hash=content_hash,
    )
    return normalized


def deduplicate_jobs(jobs: Iterable[NormalizedJob], existing_hashes: set[str], existing_external_ids: set[str]) -> tuple[list[NormalizedJob], int, int]:
    accepted: list[NormalizedJob] = []
    duplicates = 0
    invalid = 0
    for job in jobs:
        if job.external_id in existing_external_ids or job.content_hash in existing_hashes:
            duplicates += 1
            continue
        if not job.title or not job.external_id:
            invalid += 1
            continue
        accepted.append(job)
        existing_external_ids.add(job.external_id)
        existing_hashes.add(job.content_hash)
    return accepted, duplicates, invalid
