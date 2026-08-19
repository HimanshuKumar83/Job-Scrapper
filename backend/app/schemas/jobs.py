from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RawJob(BaseModel):
    model_config = ConfigDict(extra="allow")

    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    employment_type: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[datetime] = None
    source: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    remote: Optional[bool] = None
    skills: Optional[list[str]] = None
    raw_payload: Optional[dict[str, Any]] = None


class NormalizedJob(BaseModel):
    source: str
    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    employment_type: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    remote: Optional[bool] = None
    skills: Optional[str] = None
    raw_payload: Optional[str] = None
    content_hash: str


class JobRead(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    employment_type: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    remote: Optional[bool] = None
    skills: Optional[str] = None
    content_hash: str
    created_at: datetime
    updated_at: datetime
