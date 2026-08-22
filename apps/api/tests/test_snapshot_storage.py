"""G3 golden scenario: duplicate jobs in the same snapshot are collapsed."""

from datetime import UTC, datetime

from app.contracts import NormalizedJob
from app.services.snapshot import build_derived_records


def _job(source: str, job_id: str, company: str, text: str, captured: str) -> NormalizedJob:
    import hashlib

    return NormalizedJob(
        source=source,
        source_job_id=job_id,
        company=company,
        title="Analytics Engineer",
        location="São Paulo",
        source_url=f"https://example.invalid/{source}/{job_id}",
        captured_at=datetime.fromisoformat(captured),
        text_hash=hashlib.sha256(" ".join(text.split()).encode()).hexdigest(),
        description_text=text,
    )


def test_g3_same_source_and_id_dedups_keeping_latest_capture() -> None:
    older = _job("greenhouse", "1001", "ExampleCo", "dbt models", "2026-08-01T12:00:00+00:00")
    newer = _job("greenhouse", "1001", "ExampleCo", "dbt models v2", "2026-08-10T12:00:00+00:00")
    records, stats = build_derived_records([older, newer])
    assert len(records) == 1
    assert records[0].description_text == "dbt models v2"
    assert stats.same_key_collapsed == 1


def test_g3_identical_text_across_sources_dedups_by_hash() -> None:
    gh = _job(
        "greenhouse", "2001", "Alpha", "identical body text here", "2026-08-02T12:00:00+00:00"
    )
    lv = _job(
        "lever", "abc", "Beta", "identical  body  text here", "2026-08-03T12:00:00+00:00"
    )
    records, stats = build_derived_records([gh, lv])
    assert len(records) == 1
    assert stats.cross_source_hash_collapsed == 1
    # provenance of the dropped origin preserved on the surviving record
    assert records[0].source == "greenhouse"
    assert set(records[0].duplicate_of) == {"lever:abc"}


def test_g3_distinct_jobs_are_kept() -> None:
    a = _job("greenhouse", "1", "A", "text one", "2026-08-01T12:00:00+00:00")
    b = _job("lever", "2", "B", "completely different", "2026-08-01T12:00:00+00:00")
    records, stats = build_derived_records([a, b])
    assert len(records) == 2
    assert stats.same_key_collapsed == 0
    assert stats.cross_source_hash_collapsed == 0


def test_g3_empty_input_yields_empty_records() -> None:
    records, stats = build_derived_records([])
    assert records == []
    assert stats.total_input == 0
