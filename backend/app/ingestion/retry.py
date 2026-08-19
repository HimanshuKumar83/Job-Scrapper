from __future__ import annotations

import asyncio
import inspect
import random
from typing import Callable, TypeVar

from app.config import get_settings

T = TypeVar("T")
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def is_retryable_error(exc: Exception) -> bool:
    if isinstance(exc, TimeoutError):
        return True
    if isinstance(exc, ConnectionError):
        return True
    if isinstance(exc, asyncio.TimeoutError):
        return True
    if exc.__class__.__name__ == "ReadTimeout":
        return True
    if getattr(exc, "status_code", None) in RETRYABLE_STATUS_CODES:
        return True
    if getattr(exc, "response", None) is not None and getattr(exc.response, "status_code", None) in RETRYABLE_STATUS_CODES:
        return True
    return False


async def retry_with_backoff(func: Callable[[], T], *, max_retries: int | None = None, base_seconds: float | None = None):
    settings = get_settings()
    max_retries = max_retries if max_retries is not None else settings.max_retries
    base_seconds = base_seconds if base_seconds is not None else settings.backoff_base_seconds

    for attempt in range(max_retries + 1):
        try:
            result = func()
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as exc:
            if not is_retryable_error(exc) or attempt == max_retries:
                raise
            delay = base_seconds * (2 ** attempt) + random.uniform(0, 0.5)
            await asyncio.sleep(delay)

    raise RuntimeError("Retry loop exhausted")
