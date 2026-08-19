from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "total_jobs" in response.json()


def test_jobs_endpoint():
    response = client.get("/api/jobs?page=1&page_size=10")
    assert response.status_code == 200
    assert "items" in response.json()
