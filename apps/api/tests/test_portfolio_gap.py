"""G7 golden scenario: gap analysis credits ONLY explicitly registered evidence."""

import pytest
from pydantic import ValidationError

from app.services.portfolio_gap import (
    PortfolioEvidence,
    analyze_portfolio_gap,
)


def _evidence(yaml_text: str) -> PortfolioEvidence:
    return PortfolioEvidence.from_yaml_text(yaml_text)


def test_g7_skill_without_registered_evidence_gets_none() -> None:
    evidence = _evidence(
        """
skills:
  Statistics:
    level: strong
    evidence:
      - repo: BarujaFe1/StatLab
        reason: A/B testing engine
"""
    )
    report = analyze_portfolio_gap(
        market_frequencies={"Statistics": 40, "dbt": 55, "Airflow": 30},
        evidence=evidence,
    )
    by_skill = {row.skill: row for row in report.rows}
    assert by_skill["dbt"].evidence_level == "none"
    assert by_skill["dbt"].status == "market_demand_no_evidence"
    # registered skill gets factual credit, nothing more
    assert by_skill["Statistics"].evidence_level == "strong"
    assert by_skill["Statistics"].status == "market_demand_with_evidence"


def test_low_demand_skill_without_evidence_is_no_signal() -> None:
    evidence = _evidence("skills: {}")
    report = analyze_portfolio_gap(
        market_frequencies={"ObscureTool": 1},
        evidence=evidence,
    )
    row = report.rows[0]
    assert row.status == "low_demand_no_evidence"


def test_status_thresholds_are_documented_and_stable() -> None:
    evidence = _evidence(
        """
skills:
  SQL:
    level: working
    evidence:
      - repo: BarujaFe1/x
        reason: used across projects
"""
    )
    high = {"SQL": 50}
    report = analyze_portfolio_gap(market_frequencies=high, evidence=evidence)
    assert report.rows[0].status == "market_demand_with_evidence"
    assert report.demand_threshold == 5


def test_invalid_evidence_level_rejected() -> None:
    with pytest.raises(ValidationError):
        _evidence(
            """
skills:
  SQL:
    level: guru
    evidence: []
"""
        )


def test_report_never_invents_unregistered_skills() -> None:
    evidence = _evidence("skills: {}")
    report = analyze_portfolio_gap(
        market_frequencies={"Python": 30},
        evidence=evidence,
        extra_skills=["MadeUpSkill"],
    )
    # extra_skills outside the market slice are ignored entirely
    assert {r.skill for r in report.rows} == {"Python"}
