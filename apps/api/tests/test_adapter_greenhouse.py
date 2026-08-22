"""G1 golden scenario: Greenhouse fixture normalizes stably into NormalizedJob."""

import hashlib
import json
from pathlib import Path

import httpx
import pytest

from app.adapters.greenhouse import GreenhouseAdapter

FIXTURE = Path(__file__).parent / "fixtures" / "greenhouse_exampleco.json"


def _mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def _fixture_response(request: httpx.Request) -> httpx.Response:
    assert request.url.host == "boards.greenhouse.io"
    assert request.url.path == "/v1/boards/exampleco/jobs"
    assert request.url.params.get("content") == "true"
    return httpx.Response(200, json={"jobs": json.loads(FIXTURE.read_text(encoding="utf-8"))})


def test_g1_greenhouse_fixture_normalizes_stable() -> None:
    adapter = GreenhouseAdapter(client=_mock_client(_fixture_response))
    jobs = adapter.fetch_jobs(board_token="exampleco", company="ExampleCo")

    assert len(jobs) == 2
    job = jobs[0]
    assert job.source == "greenhouse"
    assert job.source_job_id == "1001"
    assert job.company == "ExampleCo"
    assert job.title == "Analytics Engineer"
    assert job.location == "São Paulo, Brazil"
    assert job.source_url == "https://jobs.exampleco.com/jobs/1001?gh_jid=1001"
    # deterministic capture from payload updated_at, converted to UTC
    assert job.captured_at.isoformat() == "2026-08-20T13:00:00+00:00"
    expected_hash = hashlib.sha256(
        b"Build and maintain dbt models. Strong SQL and Python required."
    ).hexdigest()
    assert job.text_hash == expected_hash
    assert "<" not in job.description_text
    assert "dbt" in job.description_text


def test_g1_greenhouse_normalization_is_deterministic() -> None:
    adapter = GreenhouseAdapter(client=_mock_client(_fixture_response))
    first = adapter.fetch_jobs(board_token="exampleco", company="ExampleCo")
    second = adapter.fetch_jobs(board_token="exampleco", company="ExampleCo")
    assert [j.model_dump() for j in first] == [j.model_dump() for j in second]


def test_greenhouse_retries_on_server_error_then_succeeds() -> None:
    calls = {"n": 0}

    def flaky_handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(502)
        return _fixture_response(request)

    adapter = GreenhouseAdapter(
        client=_mock_client(flaky_handler),
        max_retries=3,
        backoff=lambda attempt: None,
    )
    jobs = adapter.fetch_jobs(board_token="exampleco", company="ExampleCo")
    assert calls["n"] == 3
    assert len(jobs) == 2


def test_greenhouse_gives_up_after_max_retries() -> None:
    def broken_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    adapter = GreenhouseAdapter(
        client=_mock_client(broken_handler),
        max_retries=2,
        backoff=lambda attempt: None,
    )
    with pytest.raises(httpx.HTTPStatusError):
        adapter.fetch_jobs(board_token="exampleco", company="ExampleCo")


def test_greenhouse_timeout_is_configurable() -> None:
    adapter = GreenhouseAdapter(timeout=7.5)
    assert adapter.timeout_seconds == 7.5
