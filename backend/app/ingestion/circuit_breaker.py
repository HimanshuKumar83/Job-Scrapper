from __future__ import annotations

import time
from enum import Enum

from app.config import get_settings


class CircuitState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    COOLDOWN = "COOLDOWN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, failure_threshold: int | None = None, cooldown_seconds: int | None = None) -> None:
        settings = get_settings()
        self.failure_threshold = failure_threshold or settings.circuit_breaker_failure_threshold
        self.cooldown_seconds = cooldown_seconds or settings.circuit_breaker_cooldown_seconds
        self.state = CircuitState.HEALTHY
        self.consecutive_failures = 0
        self.last_failure_at: float | None = None
        self.last_success_at: float | None = None

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.last_success_at = time.monotonic()
        self.state = CircuitState.HEALTHY

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.last_failure_at = time.monotonic()
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.DEGRADED

    def allow_request(self) -> bool:
        if self.state == CircuitState.HEALTHY:
            return True
        if self.state == CircuitState.DEGRADED:
            if self.last_failure_at is None:
                return False
            if time.monotonic() - self.last_failure_at >= self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def on_half_open_result(self, success: bool) -> None:
        if success:
            self.record_success()
        else:
            self.state = CircuitState.DEGRADED
            self.consecutive_failures = self.failure_threshold
            self.last_failure_at = time.monotonic()
