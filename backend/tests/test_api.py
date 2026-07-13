"""API integration tests with in-memory SQLite."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.database import Base, get_db
from app.main import create_app
from app.pipeline import run_pipeline


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("JOBSCOPE_DEMO_MODE", "false")
    get_settings.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    run_pipeline(db)
    db.close()

    app = create_app()

    def _override():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["jobs_count"] > 0


def test_stats_and_skills(client: TestClient):
    stats = client.get("/stats").json()
    assert stats["total_jobs"] >= 10
    assert stats["unique_companies"] >= 5
    assert len(stats["top_skills"]) >= 3

    skills = client.get("/skills").json()
    assert any(s["name"] == "Python" for s in skills)


def test_jobs_filter_and_detail(client: TestClient):
    page = client.get("/jobs", params={"seniority": "senior", "page_size": 50}).json()
    assert page["total"] >= 1
    assert all(item["seniority"] == "senior" for item in page["items"])

    job_id = page["items"][0]["id"]
    detail = client.get(f"/jobs/{job_id}").json()
    assert detail["id"] == job_id
    assert "description" in detail


def test_pipeline_status(client: TestClient):
    res = client.get("/pipeline/status")
    assert res.status_code == 200
    body = res.json()
    assert body["healthy"] is True
    assert len(body["sources"]) == 2
    assert len(body["recent_runs"]) >= 1


def test_dedup_across_boards(client: TestClient):
    """Same role on both boards should not create two rows."""
    page = client.get("/jobs", params={"q": "NuvemPay", "page_size": 50}).json()
    titles = [j["title"].lower() for j in page["items"]]
    # At most one pleno backend python for NuvemPay after fingerprint dedup
    pleno_backend = [
        t for t in titles if "backend" in t and "python" in t and "pleno" in t
    ]
    assert len(pleno_backend) == 1
