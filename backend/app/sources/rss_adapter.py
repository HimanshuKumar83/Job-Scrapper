from __future__ import annotations

from datetime import datetime

import httpx

from app.config import get_settings
from app.schemas.jobs import RawJob
from app.sources.base import JobSourceAdapter


class RSSJobAdapter(JobSourceAdapter):
    name = "jobicy"

    def __init__(self, base_url: str | None = None) -> None:
        self.settings = get_settings()
        self.base_url = base_url or "https://jobicy.com/api/v2/remote-jobs"

    async def fetch_jobs(self) -> list[RawJob]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            payload = response.json()

        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        normalized = []
        for item in jobs:
            if not isinstance(item, dict):
                continue
            posted_at = None
            if item.get("pubDate"):
                try:
                    posted_at = datetime.fromisoformat(str(item["pubDate"]).replace("Z", "+00:00"))
                except ValueError:
                    posted_at = None
            normalized.append(
                RawJob(
                    source=self.name,
                    external_id=str(item.get("id") or item.get("jobSlug") or item.get("url") or "unknown"),
                    title=str(item.get("jobTitle") or item.get("title") or "Untitled job"),
                    company=item.get("companyName") or item.get("company") or item.get("company_name"),
                    location=item.get("jobGeo") or item.get("location") or item.get("remote_location") or "Remote",
                    description=item.get("jobDescription") or item.get("jobExcerpt") or item.get("description") or item.get("job_description"),
                    employment_type=", ".join(item["jobType"]) if isinstance(item.get("jobType"), list) else item.get("jobType") or item.get("employment_type") or item.get("type"),
                    url=item.get("url") or item.get("apply_url"),
                    posted_at=posted_at,
                    salary_min=item.get("salaryMin") or item.get("salary_min"),
                    salary_max=item.get("salaryMax") or item.get("salary_max"),
                    currency=item.get("salaryCurrency") or item.get("currency"),
                    remote=item.get("remote") if isinstance(item.get("remote"), bool) else None,
                    skills=item.get("jobIndustry") if isinstance(item.get("jobIndustry"), list) else item.get("skills"),
                    raw_payload=item,
                )
            )
        return normalized
