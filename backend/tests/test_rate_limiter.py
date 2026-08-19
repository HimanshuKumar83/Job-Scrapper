import asyncio

import pytest

from app.ingestion.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_spaces_requests():
    limiter = RateLimiter(requests_per_minute=2, min_interval_seconds=0.1)
    start = asyncio.get_running_loop().time()
    await limiter.acquire()
    await limiter.acquire()
    elapsed = asyncio.get_running_loop().time() - start
    assert elapsed >= 0.1
