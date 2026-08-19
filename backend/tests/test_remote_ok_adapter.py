import httpx
import json
import pytest

from app.sources.remote_ok_adapter import RemoteOKJobAdapter


@pytest.mark.asyncio
async def test_remote_ok_adapter_maps_public_json(monkeypatch):
    payload = [{
        "id": "123",
        "position": "Platform Engineer",
        "company": "Example Co",
        "location": "Worldwide",
        "date": "2026-08-19T10:00:00+00:00",
        "url": "https://remoteok.com/example",
        "tags": ["python"],
    }]

    class FakeResponse:
        content = json.dumps(payload).encode("utf-8")

        def raise_for_status(self):
            pass

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: FakeClient())
    jobs = await RemoteOKJobAdapter().fetch_jobs()
    assert jobs[0].title == "Platform Engineer"
    assert jobs[0].company == "Example Co"
    assert jobs[0].remote is True
