"""Lever Postings API adapter.

Docs: https://github.com/lever/postings-api
Public GETs only (`?mode=json`); no POST/application calls, ever.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from app.adapters.base import HttpFetcher, normalized_text_hash
from app.contracts import NormalizedJob

LEVER_BASE = "https://api.lever.co/v0/postings"


def parse_lever_job(item: dict[str, Any], company: str) -> NormalizedJob:
    categories = item.get("categories") or {}
    location = categories.get("location") if isinstance(categories, dict) else None
    created_raw = item.get("createdAt")
    if isinstance(created_raw, (int, float)):
        captured = datetime.fromtimestamp(created_raw / 1000.0, tz=UTC)
    else:
        captured = datetime.now(tz=UTC)
    # Lever provides plaintext directly; normalize whitespace for stable hashing.
    description = " ".join(str(item.get("descriptionPlain") or "").split())
    job_id = str(item["id"])
    hosted_url = str(item.get("hostedUrl") or "")
    return NormalizedJob(
        source="lever",
        source_job_id=job_id,
        company=company,
        title=str(item.get("text") or ""),
        location=location,
        source_url=hosted_url or f"https://jobs.lever.co/{site_or_company(company, item)}/{job_id}",
        captured_at=captured,
        text_hash=normalized_text_hash(description),
        description_text=description,
    )


def site_or_company(company: str, _item: dict[str, Any]) -> str:
    return company.lower().replace(" ", "")


class LeverAdapter:
    def __init__(self, client: httpx.Client | None = None, **fetcher_kwargs: Any) -> None:
        self.fetcher = HttpFetcher(client=client, **fetcher_kwargs)

    @property
    def timeout_seconds(self) -> float:
        return self.fetcher.timeout_seconds

    def fetch_jobs(self, site: str, company: str | None = None) -> list[NormalizedJob]:
        company_name = company or site
        url = f"{LEVER_BASE}/{site}?mode=json"
        payload = self.fetcher.get_json(url)
        if not isinstance(payload, list):
            raise ValueError(f"Lever response for '{site}' is not a postings array")
        return [parse_lever_job(item, company_name) for item in payload]
