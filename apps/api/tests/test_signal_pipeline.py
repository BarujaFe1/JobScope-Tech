"""Snapshot aggregation pipeline: derived records -> public aggregate JSON model."""

import hashlib
from datetime import datetime

from app.contracts import NormalizedJob
from app.services.signal_pipeline import (
    SNIPPET_MAX_CHARS,
    build_market_snapshot,
)
from app.services.skills import SkillDictionary
from app.services.snapshot import build_derived_records


def _job(source: str, jid: str, company: str, title: str, text: str) -> NormalizedJob:
    canonical = " ".join(text.split())
    return NormalizedJob(
        source=source,
        source_job_id=jid,
        company=company,
        title=title,
        location="São Paulo, Brazil",
        source_url=f"https://example.invalid/{jid}",
        captured_at=datetime.fromisoformat("2026-08-20T12:00:00+00:00"),
        text_hash=hashlib.sha256(canonical.encode()).hexdigest(),
        description_text=text,
    )


def _synthetic_jobs():
    return [
        _job("greenhouse", "g1", "ExampleCo", "Analytics Engineer", "dbt models, SQL e Python no dia a dia."),
        _job("greenhouse", "g2", "ExampleCo", "Data Analyst", "SQL avançado, Power BI e experimentação A/B."),
        _job("lever", "l1", "ExampleLabs", "Data Analyst", "Dashboards em Power BI com SQL."),
        _job("lever", "l2", "ExampleLabs", "Product Analyst", "Experimentação A/B e SQL para produto."),
        _job("lever", "l3", "ExampleLabs", "Engenheiro de Dados", "Airflow, Spark e pipelines ELT em Python."),
    ]


def test_snapshot_builds_role_aggregates() -> None:
    dictionary = SkillDictionary(version="test", skills={"SQL": ["sql"], "Python": ["python"], "dbt": ["dbt"], "Power BI": ["power bi"], "Experimentation": ["a/b"], "Airflow": [], "Spark": [], "ELT": []})
    records, stats = build_derived_records(_synthetic_jobs())
    snapshot = build_market_snapshot(
        records,
        dictionary=dictionary,
        generated_at="2026-08-22T00:00:00Z",
        sources_provenance=[{"company": "ExampleCo", "ats": "greenhouse"}],
        demand_threshold=2,
        min_support=2,
    )

    assert stats.total_input == 5
    roles = {r["role"] for r in snapshot["roles"]}
    assert "data_analyst" in roles and "analytics_engineer" in roles

    analyst_skills = dict(snapshot["skill_frequencies"]["data_analyst"])
    assert analyst_skills.get("SQL") == 2  # g2 + l1; l2 é product_analyst


def test_snapshot_contains_no_full_descriptions_only_short_snippets() -> None:
    dictionary = SkillDictionary(version="t", skills={"SQL": ["sql"]})
    long_text = ("SQL " + "lorem ipsum dolor sit amet consectetur " * 30).strip()
    records, _ = build_derived_records([_job("lever", "x1", "C", "Data Analyst", long_text)])
    snapshot = build_market_snapshot(records, dictionary=dictionary, generated_at="t0")
    for example in snapshot["evidence_examples"]:
        assert len(example["snippet"]) <= SNIPPET_MAX_CHARS
        assert example["source_url"].startswith("http")


def test_snapshot_records_provenance_and_versions() -> None:
    dictionary = SkillDictionary(version="v-test", skills={"SQL": ["sql"]})
    records, _ = build_derived_records(_synthetic_jobs())
    snapshot = build_market_snapshot(
        records,
        dictionary=dictionary,
        generated_at="2026-08-22T00:00:00Z",
        sources_provenance=[{"company": "ExampleLabs", "ats": "lever", "site": "examplelabs"}],
    )
    assert snapshot["meta"]["skills_dictionary_version"] == "v-test"
    assert snapshot["meta"]["generated_at"] == "2026-08-22T00:00:00Z"
    assert snapshot["meta"]["sources"][0]["ats"] == "lever"
    assert "não representa todo o mercado" in snapshot["meta"]["disclaimer"]


def test_gap_block_present_and_factual() -> None:
    dictionary = SkillDictionary(version="t", skills={"SQL": ["sql"]})
    records, _ = build_derived_records(_synthetic_jobs())
    snapshot = build_market_snapshot(
        records, dictionary=dictionary, generated_at="t", demand_threshold=2
    )
    assert "gap" in snapshot
    assert snapshot["gap"]["demand_threshold"] == 2
