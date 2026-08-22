#!/usr/bin/env python3
"""Build the public aggregate market snapshot.

Modes:
  synthetic (default): build from repo fixtures -> safe, reproducible demo data.
  live:                collect from ENABLED boards in data/config/sources.yml.

Output: data/public/market_snapshot.json (aggregates only; no full descriptions).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from app.adapters.greenhouse import GreenhouseAdapter
from app.adapters.lever import LeverAdapter
from app.contracts import NormalizedJob
from app.domain.types import ParsedJob
from app.pipeline.collectors import load_fixture
from app.services.portfolio_gap import PortfolioEvidence
from app.services.signal_pipeline import build_market_snapshot
from app.services.skills import load_skill_dictionary
from app.services.snapshot import build_derived_records
from app.services.source_registry import load_source_registry

OUTPUT_PATH = REPO_ROOT / "data" / "public" / "market_snapshot.json"


def _parsed_to_normalized(parsed: ParsedJob, source_name: str) -> NormalizedJob:
    from app.adapters.base import normalized_text_hash

    text = parsed.description or ""
    return NormalizedJob(
        source="greenhouse" if "greenhouse" in source_name else "lever",
        source_job_id=parsed.external_id,
        company=parsed.company,
        title=parsed.title,
        location=parsed.location,
        source_url=parsed.original_url,
        captured_at=parsed.published_at or datetime.now(tz=UTC),
        text_hash=normalized_text_hash(text),
        description_text=text,
    )


def collect_synthetic() -> list[NormalizedJob]:
    """Deterministic synthetic corpus from committed fixtures."""
    jobs: list[NormalizedJob] = []
    mapping = {
        "fixture_board_a": ("greenhouse", "synthetic-greenhouse"),
        "fixture_board_b": ("lever", "synthetic-lever"),
    }
    for fixture_key, (source_name, provenance_company) in mapping.items():
        for item in load_fixture(fixture_key):
            parsed = _parse_fixture_item(item, fixture_key)
            normalized = _parsed_to_normalized(parsed, source_name)
            normalized = normalized.model_copy(update={"company": provenance_company})
            jobs.append(normalized)
    return jobs


def _parse_fixture_item(item: dict, fixture_key: str) -> ParsedJob:
    from app.pipeline.collectors import PARSERS

    return PARSERS[fixture_key](item)


def collect_live() -> tuple[list[NormalizedJob], list[dict]]:
    registry = load_source_registry()
    jobs: list[NormalizedJob] = []
    provenance: list[dict] = []
    gh = GreenhouseAdapter()
    lv = LeverAdapter()
    for src in registry.enabled_sources():
        before = len(jobs)
        if src.ats == "greenhouse":
            jobs.extend(gh.fetch_jobs(board_token=src.board_token, company=src.company))
        else:
            jobs.extend(lv.fetch_jobs(site=src.site, company=src.company))
        provenance.append(
            {
                "company": src.company,
                "ats": src.ats,
                "identifier": src.board_token or src.site,
                "country": src.country,
                "scope": src.scope,
                "jobs_captured": len(jobs) - before,
            }
        )
    return jobs, provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["synthetic", "live"], default="synthetic")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    if args.mode == "live":
        raw_jobs, provenance = collect_live()
    else:
        raw_jobs = collect_synthetic()
        provenance = [
            {"company": "synthetic-greenhouse", "ats": "greenhouse", "jobs_captured": sum(1 for j in raw_jobs if j.source == "greenhouse")},
            {"company": "synthetic-lever", "ats": "lever", "jobs_captured": sum(1 for j in raw_jobs if j.source == "lever")},
        ]

    records, stats = build_derived_records(raw_jobs)
    dictionary = load_skill_dictionary()
    evidence = PortfolioEvidence.load()
    snapshot = build_market_snapshot(
        records,
        dictionary=dictionary,
        generated_at=datetime.now(tz=UTC).isoformat(timespec="seconds"),
        sources_provenance=provenance,
        evidence=evidence,
    )
    snapshot["meta"]["dedup"] = stats.model_dump()
    snapshot["meta"]["mode"] = args.mode

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"snapshot written: {args.output} ({len(records)} records, mode={args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
