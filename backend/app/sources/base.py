from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.jobs import RawJob


class JobSourceAdapter(ABC):
    name: str

    @abstractmethod
    async def fetch_jobs(self) -> list[RawJob]:
        raise NotImplementedError

    @property
    def source_name(self) -> str:
        return self.name
