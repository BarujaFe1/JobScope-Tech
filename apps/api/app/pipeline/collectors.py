"""Fixture collectors and parsers for demo sources."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.domain.types import ParsedJob

# Repo root / data/fixtures relative to backend/
FIXTURES_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def load_fixture(source_key: str) -> list[dict]:
    path = FIXTURES_DIR / f"{source_key}.json"
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found for source '{source_key}': {path}")
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Fixture {path} must be a JSON array")
    return data


def parse_board_a(item: dict) -> ParsedJob:
    """Parser for fixture_board_a (generic ATS-like JSON)."""
    return ParsedJob(
        external_id=str(item["id"]),
        source_key="fixture_board_a",
        title=str(item["title"]),
        company=str(item["company"]),
        description=str(item.get("description") or ""),
        location=item.get("location"),
        seniority_hint=item.get("seniority"),
        work_model_hint=item.get("work_model"),
        original_url=str(item.get("url") or f"https://example.com/jobs/{item['id']}"),
        published_at=_parse_iso(item.get("published_at")),
        raw_payload=item,
    )


def parse_board_b(item: dict) -> ParsedJob:
    """Parser for fixture_board_b (noisier free-text fields)."""
    title = str(item.get("job_title") or item.get("title") or "")
    company = str(item.get("employer") or item.get("company") or "")
    body = str(item.get("body") or item.get("description") or "")
    meta = str(item.get("meta") or "")
    return ParsedJob(
        external_id=str(item.get("external_code") or item.get("id")),
        source_key="fixture_board_b",
        title=title,
        company=company,
        description=f"{body}\n{meta}".strip(),
        location=item.get("city") or item.get("location"),
        seniority_hint=None,
        work_model_hint=None,
        original_url=str(item.get("link") or f"https://example.org/vagas/{item.get('id')}"),
        published_at=_parse_iso(item.get("posted_at")),
        raw_payload=item,
    )


PARSERS = {
    "fixture_board_a": parse_board_a,
    "fixture_board_b": parse_board_b,
}


def collect_source(source_key: str) -> list[ParsedJob]:
    parser = PARSERS.get(source_key)
    if parser is None:
        raise KeyError(f"No parser registered for source '{source_key}'")
    return [parser(item) for item in load_fixture(source_key)]
