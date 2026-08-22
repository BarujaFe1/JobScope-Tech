"""G2 golden scenario: Lever fixture normalizes into the same contract as Greenhouse."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from app.adapters.greenhouse import GreenhouseAdapter
from app.adapters.lever import LeverAdapter
from tests.test_adapter_greenhouse import _fixture_response as gh_response

FIXTURE = Path(__file__).parent / "fixtures" / "lever_examplelabs.json"


def _lever_handler(request: httpx.Request) -> httpx.Response:
    assert request.url.host == "api.lever.co"
    assert request.url.path == "/v0/postings/examplelabs"
    assert request.url.params.get("mode") == "json"
    return httpx.Response(200, json=json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_g2_lever_fixture_normalizes_to_same_contract() -> None:
    adapter = LeverAdapter(client=httpx.Client(transport=httpx.MockTransport(_lever_handler)))
    jobs = adapter.fetch_jobs(site="examplelabs", company="ExampleLabs")

    assert len(jobs) == 2
    job = jobs[0]
    assert job.source == "lever"
    assert job.source_job_id == "a1b2c3d4-0000-1111-2222-333344445555"
    assert job.company == "ExampleLabs"
    assert job.title == "Analytics Engineer II"
    assert job.location == "Remote - Brazil"
    assert job.source_url == "https://jobs.lever.co/examplelabs/a1b2c3d4-0000-1111-2222-333344445555"
    # createdAt epoch millis -> UTC
    assert job.captured_at == datetime(2025, 8, 18, 12, 0, 0, tzinfo=UTC)
    expected_hash = hashlib.sha256(
        " ".join(
            "You will build and maintain dbt models and semantic layers.\n\n"
            "Requirements: strong SQL, Python, and communication skills.".split()
        ).encode()
    ).hexdigest()
    assert job.text_hash == expected_hash


def test_g2_lever_and_greenhouse_share_normalized_contract() -> None:
    lever = LeverAdapter(client=httpx.Client(transport=httpx.MockTransport(_lever_handler)))
    greenhouse = GreenhouseAdapter(
        client=httpx.Client(transport=httpx.MockTransport(gh_response))
    )
    lever_jobs = lever.fetch_jobs(site="examplelabs", company="ExampleLabs")
    gh_jobs = greenhouse.fetch_jobs(board_token="exampleco", company="ExampleCo")
    all_jobs = lever_jobs + gh_jobs
    for job in all_jobs:
        assert job.source in {"greenhouse", "lever"}
        assert job.source_job_id
        assert job.company
        assert job.title
        assert job.source_url.startswith("http")
        assert len(job.text_hash) == 64
        assert isinstance(job.description_text, str)


def test_lever_404_raises_http_error() -> None:
    def not_found(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    adapter = LeverAdapter(
        client=httpx.Client(transport=httpx.MockTransport(not_found)),
        max_retries=1,
        backoff=lambda attempt: None,
    )
    with pytest.raises(httpx.HTTPStatusError):
        adapter.fetch_jobs(site="ghostsite", company="Ghost")


def test_lever_retries_on_429_then_succeeds() -> None:
    calls = {"n": 0}

    def rate_limited(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 2:
            return httpx.Response(429)
        return _lever_handler(request)

    adapter = LeverAdapter(
        client=httpx.Client(transport=httpx.MockTransport(rate_limited)),
        max_retries=3,
        backoff=lambda attempt: None,
    )
    jobs = adapter.fetch_jobs(site="examplelabs", company="ExampleLabs")
    assert calls["n"] == 2
    assert len(jobs) == 2
