"""Golden contract tests: canonical models + source registry (G-contract layer)."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.contracts import NormalizedJob, SkillEvidence
from app.services.source_registry import (
    SourceConfig,
    load_source_registry,
)


def test_normalized_job_contract_fields() -> None:
    job = NormalizedJob(
        source="greenhouse",
        source_job_id="123",
        company="ExampleCo",
        title="Analytics Engineer",
        location="Remote - Brazil",
        source_url="https://boards.greenhouse.io/exampleco/jobs/123",
        captured_at=datetime(2026, 8, 22, 12, 0, 0, tzinfo=UTC),
        text_hash="a" * 64,
        description_text="build and maintain dbt models",
    )
    assert job.source == "greenhouse"
    assert job.source_job_id == "123"
    assert job.text_hash == "a" * 64


def test_normalized_job_rejects_unknown_source() -> None:
    with pytest.raises(ValidationError):
        NormalizedJob(
            source="linkedin",  # type: ignore[arg-type]
            source_job_id="1",
            company="X",
            title="X",
            location=None,
            source_url="https://example.invalid",
            captured_at=datetime.now(tz=UTC),
            text_hash="a" * 64,
            description_text="",
        )


def test_skill_evidence_contract() -> None:
    ev = SkillEvidence(skill="dbt", confidence=1.0, evidence="build dbt models", method="dictionary")
    assert ev.method == "dictionary"
    with pytest.raises(ValidationError):
        SkillEvidence(skill="dbt", confidence=1.0, evidence="x", method="oracle")  # type: ignore[arg-type]


def test_source_config_requires_token_for_greenhouse() -> None:
    with pytest.raises(ValidationError):
        SourceConfig(company="ExampleCo", ats="greenhouse", enabled=True)


def test_source_config_requires_site_for_lever() -> None:
    with pytest.raises(ValidationError):
        SourceConfig(company="ExampleLabs", ats="lever", enabled=True)


def test_load_source_registry_from_yaml(tmp_path: Path) -> None:
    yml = tmp_path / "sources.yml"
    yml.write_text(
        """
sources:
  - company: ExampleCo
    ats: greenhouse
    board_token: exampleco
    enabled: true
  - company: ExampleLabs
    ats: lever
    site: examplelabs
    enabled: false
""",
        encoding="utf-8",
    )
    registry = load_source_registry(yml)
    assert len(registry.sources) == 2
    gh = registry.sources[0]
    assert gh.ats == "greenhouse" and gh.board_token == "exampleco" and gh.enabled is True
    lv = registry.sources[1]
    assert lv.ats == "lever" and lv.site == "examplelabs" and lv.enabled is False


def test_load_source_registry_rejects_unknown_ats(tmp_path: Path) -> None:
    yml = tmp_path / "sources.yml"
    yml.write_text(
        """
sources:
  - company: SketchCo
    ats: gupy
    site: sketchco
    enabled: true
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_source_registry(yml)
