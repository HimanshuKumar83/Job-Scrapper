import pytest

from app.ingestion.retry import is_retryable_error, retry_with_backoff


@pytest.mark.asyncio
async def test_retry_success_after_transient_failure():
    attempts = {"count": 0}

    async def call():
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise TimeoutError("transient")
        return "ok"

    result = await retry_with_backoff(call, max_retries=3, base_seconds=0)
    assert result == "ok"


def test_retryable_error_detection():
    exc = TimeoutError("timed out")
    assert is_retryable_error(exc) is True

    exc2 = ValueError("bad")
    assert is_retryable_error(exc2) is False
