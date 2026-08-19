from __future__ import annotations

from datetime import datetime
import json

import httpx

from app.schemas.jobs import RawJob
from app.sources.base import JobSourceAdapter


class RemoteOKJobAdapter(JobSourceAdapter):
    name = "remoteok"
    base_url = "https://remoteok.com/api"

    async def fetch_jobs(self) -> list[RawJob]:
        headers = {"User-Agent": "JobPulse/1.0 (public job API demo)"}
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(self.base_url, headers=headers)
            response.raise_for_status()
            payload = json.loads(response.content.decode("utf-8"))

        if not isinstance(payload, list):
            raise ValueError("Remote OK response must be a JSON array")

        records: list[RawJob] = []
        for item in payload:
            if not isinstance(item, dict) or not item.get("id") or not item.get("position"):
                continue
            posted_at = None
            if item.get("date"):
                try:
                    posted_at = datetime.fromisoformat(str(item["date"]).replace("Z", "+00:00"))
                except ValueError:
                    pass
            records.append(
                RawJob(
                    source=self.name,
                    external_id=str(item["id"]),
                    title=str(item["position"]).strip(),
                    company=item.get("company"),
                    location=item.get("location") or "Remote",
                    description=item.get("description"),
                    employment_type=None,
                    url=item.get("apply_url") or item.get("url"),
                    posted_at=posted_at,
                    salary_min=item.get("salary_min") or None,
                    salary_max=item.get("salary_max") or None,
                    currency=None,
                    remote=True,
                    skills=item.get("tags") if isinstance(item.get("tags"), list) else None,
                    raw_payload=item,
                )
            )
        return records
