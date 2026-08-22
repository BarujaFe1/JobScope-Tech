"""Source registry: auditable YAML list of ATS boards we are allowed to collect."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

RepoRoot = Path(__file__).resolve().parents[4]
DEFAULT_REGISTRY_PATH = RepoRoot / "data" / "config" / "sources.yml"


class SourceConfig(BaseModel):
    """One ATS board. Greenhouse needs board_token; Lever needs site."""

    company: str = Field(min_length=1)
    ats: Literal["greenhouse", "lever"]
    board_token: str | None = None
    site: str | None = None
    country: str = "BR"
    scope: str = "data-analytics"
    enabled: bool = True
    provenance: str | None = None

    @model_validator(mode="after")
    def _require_ats_identifier(self) -> SourceConfig:
        if self.ats == "greenhouse" and not self.board_token:
            raise ValueError(f"source '{self.company}' (greenhouse) requires 'board_token'")
        if self.ats == "lever" and not self.site:
            raise ValueError(f"source '{self.company}' (lever) requires 'site'")
        return self


class SourceRegistry(BaseModel):
    sources: list[SourceConfig]

    def enabled_sources(self, ats: str | None = None) -> list[SourceConfig]:
        return [
            s
            for s in self.sources
            if s.enabled and (ats is None or s.ats == ats)
        ]


def load_source_registry(path: Path | str | None = None) -> SourceRegistry:
    registry_path = Path(path) if path else DEFAULT_REGISTRY_PATH
    if not registry_path.exists():
        raise FileNotFoundError(f"Source registry not found: {registry_path}")
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    entries = raw.get("sources")
    if not isinstance(entries, list):
        raise ValueError(f"{registry_path} must contain a top-level 'sources' list")
    return SourceRegistry.model_validate({"sources": entries})
