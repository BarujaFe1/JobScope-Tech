"""Canonical cross-adapter contracts (see 01_DESIGN_SPEC.md)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SourceName = Literal["greenhouse", "lever"]
SkillMethod = Literal["dictionary", "llm"]


class NormalizedJob(BaseModel):
    source: SourceName
    source_job_id: str = Field(min_length=1)
    company: str
    title: str
    location: str | None = None
    source_url: str
    captured_at: datetime
    text_hash: str = Field(min_length=64, max_length=64)
    description_text: str


class SkillEvidence(BaseModel):
    skill: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str
    method: SkillMethod


class DerivedJob(BaseModel):
    """Normalized, deduplicated, skill-annotated record ready for aggregation."""

    source: SourceName
    source_job_id: str
    company: str
    title: str
    location: str | None = None
    source_url: str
    captured_at: datetime
    text_hash: str
    description_text: str
    duplicate_of: list[str] = Field(default_factory=list)
    skills: list[SkillEvidence] = Field(default_factory=list)


class DedupStats(BaseModel):
    total_input: int = 0
    same_key_collapsed: int = 0
    cross_source_hash_collapsed: int = 0
