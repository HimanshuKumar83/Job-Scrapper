from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.ingestion.circuit_breaker import CircuitBreaker, CircuitState


@dataclass
class SourceHealth:
    name: str
    status: str = "healthy"
    breaker: CircuitBreaker | None = None

    def update_from_failure(self) -> None:
        if self.breaker is not None:
            self.breaker.record_failure()
            self.status = self.breaker.state.value

    def update_from_success(self) -> None:
        if self.breaker is not None:
            self.breaker.record_success()
            self.status = self.breaker.state.value


class SourceHealthRegistry:
    def __init__(self) -> None:
        self.sources: Dict[str, SourceHealth] = {}

    def ensure(self, name: str) -> SourceHealth:
        if name not in self.sources:
            self.sources[name] = SourceHealth(name=name, breaker=CircuitBreaker())
        return self.sources[name]

    def get_status(self, name: str) -> str:
        return self.sources.get(name, SourceHealth(name=name)).status
