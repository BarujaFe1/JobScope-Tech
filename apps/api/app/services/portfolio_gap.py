"""Portfolio Gap Analysis: market demand vs explicitly registered evidence.

G7 contract: only skills manually registered in portfolio/evidence.yml receive
evidence credit. The analyzer never invents evidence and never uses praise —
it emits factual statuses for the UI to present.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

RepoRoot = Path(__file__).resolve().parents[4]
DEFAULT_EVIDENCE_PATH = RepoRoot / "portfolio" / "evidence.yml"

ALLOWED_LEVELS = ("none", "learning", "working", "strong")
# Documented threshold: a skill is "market demand" when it appears in at least
# this many postings of the current snapshot slice.
DEMAND_THRESHOLD_DEFAULT = 5


class EvidenceItem(BaseModel):
    repo: str | None = None
    link: str | None = None
    reason: str


class SkillEvidenceEntry(BaseModel):
    level: str
    evidence: list[EvidenceItem]

    def model_post_init(self, _ctx) -> None:  # noqa: ANN001
        if self.level not in ALLOWED_LEVELS:
            raise ValueError(
                f"level '{self.level}' not in {ALLOWED_LEVELS} "
                "(portfolio restraint: only explicit levels allowed)"
            )


class PortfolioEvidence(BaseModel):
    skills: dict[str, SkillEvidenceEntry] = Field(default_factory=dict)

    @classmethod
    def from_yaml_text(cls, text: str) -> "PortfolioEvidence":
        raw = yaml.safe_load(text) or {}
        return cls.model_validate({"skills": raw.get("skills") or {}})

    @classmethod
    def load(cls, path=None) -> "PortfolioEvidence":  # noqa: ANN001
        evidence_path = path or DEFAULT_EVIDENCE_PATH
        return cls.from_yaml_text(evidence_path.read_text(encoding="utf-8"))


class GapRow(BaseModel):
    skill: str
    market_frequency: int
    evidence_level: str
    status: str


class GapReport(BaseModel):
    rows: list[GapRow]
    demand_threshold: int


def analyze_portfolio_gap(
    market_frequencies: dict[str, int],
    evidence: PortfolioEvidence,
    extra_skills: list[str] | None = None,
    demand_threshold: int = DEMAND_THRESHOLD_DEFAULT,
) -> GapReport:
    rows: list[GapRow] = []
    # extra_skills are intentionally ignored unless they carry real market signal
    for skill, frequency in sorted(
        market_frequencies.items(), key=lambda kv: (-kv[1], kv[0])
    ):
        entry = evidence.skills.get(skill)
        level = entry.level if entry else "none"
        has_evidence = entry is not None and len(entry.evidence) > 0
        is_demand = frequency >= demand_threshold

        if is_demand and has_evidence:
            status = "market_demand_with_evidence"
        elif is_demand:
            status = "market_demand_no_evidence"
        elif has_evidence:
            status = "low_demand_with_evidence"
        else:
            status = "low_demand_no_evidence"

        rows.append(
            GapRow(
                skill=skill,
                market_frequency=frequency,
                evidence_level=level if entry else "none",
                status=status,
            )
        )
    return GapReport(rows=rows, demand_threshold=demand_threshold)
