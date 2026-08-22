"""Greenhouse Job Board API adapter.

Docs: https://developers.greenhouse.io/job-board.html
Public GETs only; no authentication; no POST/application calls.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from app.adapters.base import HttpFetcher, html_content_to_text, normalized_text_hash
from app.contracts import NormalizedJob

GREENHOUSE_BASE = "https://boards.greenhouse.io/v1/boards"


def parse_greenhouse_job(item: dict[str, Any], company: str) -> NormalizedJob:
    location_obj = item.get("location") or {}
    location_name = location_obj.get("name") if isinstance(location_obj, dict) else None
    updated_at_raw = item.get("updated_at")
    captured = (
        datetime.fromisoformat(updated_at_raw)
        if isinstance(updated_at_raw, str)
        else datetime.now(tz=UTC)
    ).astimezone(UTC)
    description = html_content_to_text(str(item.get("content") or ""))
    job_id = str(item["id"])
    absolute_url = str(item.get("absolute_url") or "")
    return NormalizedJob(
        source="greenhouse",
        source_job_id=job_id,
        company=company,
        title=str(item.get("title") or ""),
        location=location_name,
        source_url=absolute_url or f"https://boards.greenhouse.io/{company}/jobs/{job_id}",
        captured_at=captured,
        text_hash=normalized_text_hash(description),
        description_text=description,
    )


class GreenhouseAdapter:
    def __init__(self, client: httpx.Client | None = None, **fetcher_kwargs: Any) -> None:
        self.fetcher = HttpFetcher(client=client, **fetcher_kwargs)

    @property
    def timeout_seconds(self) -> float:
        return self.fetcher.timeout_seconds

    def fetch_jobs(self, board_token: str, company: str | None = None) -> list[NormalizedJob]:
        company_name = company or board_token
        url = f"{GREENHOUSE_BASE}/{board_token}/jobs?content=true"
        payload = self.fetcher.get_json(url)
        items = payload.get("jobs")
        if not isinstance(items, list):
            raise ValueError(f"Greenhouse response for '{board_token}' has no jobs list")
        return [parse_greenhouse_job(item, company_name) for item in items]
