from __future__ import annotations

import asyncio
import time
from typing import Optional

from app.config import get_settings


class RateLimiter:
    def __init__(self, requests_per_minute: Optional[int] = None, min_interval_seconds: Optional[float] = None) -> None:
        settings = get_settings()
        self.requests_per_minute = requests_per_minute or settings.requests_per_minute
        self.min_interval_seconds = min_interval_seconds or settings.min_request_interval_seconds
        self._lock = asyncio.Lock()
        self._timestamps: list[float] = []

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            window_start = now - 60
            self._timestamps = [ts for ts in self._timestamps if ts > window_start]

            if len(self._timestamps) >= self.requests_per_minute:
                sleep_for = max(0.0, 60.0 - (now - self._timestamps[0]))
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)
                    now = time.monotonic()
                    self._timestamps = [ts for ts in self._timestamps if ts > now - 60]

            if self._timestamps:
                last_call = self._timestamps[-1]
                gap = now - last_call
                if gap < self.min_interval_seconds:
                    await asyncio.sleep(self.min_interval_seconds - gap)

            self._timestamps.append(time.monotonic())
