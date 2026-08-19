from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import httpx

from app.config import get_settings
from app.schemas.jobs import RawJob
from app.sources.base import JobSourceAdapter


class SandboxJobAdapter(JobSourceAdapter):
    name = "sandbox"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_jobs(self) -> list[RawJob]:
        scenario = self.settings.sandbox_scenario
        if scenario == "normal":
            payload = {
                "jobs": [
                    {
                        "id": "sandbox-1",
                        "title": "Python Backend Engineer",
                        "company": "Acme Labs",
                        "location": "Remote",
                        "description": "Build resilient APIs and ingestion systems.",
                        "employment_type": "full-time",
                        "url": "https://example.com/jobs/python-backend",
                        "posted_at": "2026-08-19T09:00:00Z",
                        "salary_min": 110000,
                        "salary_max": 150000,
                        "currency": "USD",
                        "remote": True,
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                    }
                ]
            }
            return [
                RawJob(
                    source=self.name,
                    external_id=item["id"],
                    title=item["title"],
                    company=item.get("company"),
                    location=item.get("location"),
                    description=item.get("description"),
                    employment_type=item.get("employment_type"),
                    url=item.get("url"),
                    posted_at=datetime.fromisoformat(item["posted_at"].replace("Z", "+00:00")),
                    salary_min=item.get("salary_min"),
                    salary_max=item.get("salary_max"),
                    currency=item.get("currency"),
                    remote=item.get("remote"),
                    skills=item.get("skills"),
                    raw_payload=item,
                )
                for item in payload["jobs"]
            ]
        if scenario == "empty_response":
            return []
        if scenario == "malformed_response":
            return [RawJob(source=self.name, external_id="bad", title="", company=None, location=None, description=None, employment_type=None, url=None, posted_at=None, raw_payload={})]
        if scenario == "rate_limited":
            raise httpx.HTTPStatusError("Rate limited", request=httpx.Request("GET", "https://sandbox.example/jobs"), response=httpx.Response(429, request=httpx.Request("GET", "https://sandbox.example/jobs")))
        if scenario == "timeout":
            raise TimeoutError("Sandbox timeout")
        if scenario == "server_error":
            raise httpx.HTTPStatusError("Server error", request=httpx.Request("GET", "https://sandbox.example/jobs"), response=httpx.Response(500, request=httpx.Request("GET", "https://sandbox.example/jobs")))
        return []
