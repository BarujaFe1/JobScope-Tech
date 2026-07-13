"""Canonical parsed job shape used between collectors and persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedJob:
    external_id: str
    source_key: str
    title: str
    company: str
    description: str
    location: str | None = None
    seniority_hint: str | None = None
    work_model_hint: str | None = None
    original_url: str = ""
    published_at: datetime | None = None
    raw_payload: dict = field(default_factory=dict)
