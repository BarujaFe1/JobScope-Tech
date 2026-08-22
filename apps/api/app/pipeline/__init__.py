"""Pipeline orchestration: collect → normalize → taxonomy → dedup → persist."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import (
    detect_seniority,
    detect_skills,
    detect_work_model,
    job_fingerprint,
    normalize_company_name,
    normalize_location,
    skill_slug,
)
from app.domain.types import ParsedJob
from app.models import CollectionRun, Company, Job, JobSkill, RawJob, Skill, Source
from app.pipeline.collectors import PARSERS, collect_source


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


SOURCE_META = {
    "fixture_board_a": (
        "Fixture Board A",
        "Demo source with structured ATS-like fields (seed fixture).",
    ),
    "fixture_board_b": (
        "Fixture Board B",
        "Demo source with noisier free-text fields (seed fixture).",
    ),
}


def ensure_sources(db: Session) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    for key, (name, description) in SOURCE_META.items():
        source = db.scalar(select(Source).where(Source.key == key))
        if source is None:
            source = Source(key=key, name=name, description=description)
            db.add(source)
            db.flush()
        sources[key] = source
    db.commit()
    return sources


def _get_or_create_company(db: Session, name: str) -> Company:
    normalized = normalize_company_name(name)
    company = db.scalar(select(Company).where(Company.normalized_name == normalized))
    if company is None:
        company = Company(name=name.strip(), normalized_name=normalized)
        db.add(company)
        db.flush()
    return company


def _get_or_create_skill(db: Session, name: str, category: str) -> Skill:
    slug = skill_slug(name)
    skill = db.scalar(select(Skill).where(Skill.slug == slug))
    if skill is None:
        skill = Skill(name=name, category=category, slug=slug)
        db.add(skill)
        db.flush()
    return skill


def persist_parsed_job(db: Session, parsed: ParsedJob, source: Source) -> tuple[str, Job | None]:
    """Returns (status, job) where status is created|skipped|duplicate."""
    # Raw audit row
    existing_raw = db.scalar(
        select(RawJob).where(
            RawJob.source_id == source.id,
            RawJob.external_id == parsed.external_id,
        )
    )
    if existing_raw is None:
        db.add(
            RawJob(
                source_id=source.id,
                external_id=parsed.external_id,
                payload_json=json.dumps(parsed.raw_payload, ensure_ascii=False),
            )
        )

    seniority = detect_seniority(parsed.title, parsed.seniority_hint, parsed.description)
    work_model = detect_work_model(
        parsed.work_model_hint, parsed.location, parsed.description, parsed.title
    )
    location = normalize_location(parsed.location)
    fingerprint = job_fingerprint(parsed.title, parsed.company, parsed.source_key)

    existing = db.scalar(select(Job).where(Job.fingerprint == fingerprint))
    if existing is not None:
        return "duplicate", existing

    company = _get_or_create_company(db, parsed.company)
    job = Job(
        source_id=source.id,
        company_id=company.id,
        external_id=parsed.external_id,
        title=parsed.title.strip(),
        seniority=seniority,
        work_model=work_model,
        location=location,
        original_url=parsed.original_url,
        description=parsed.description.strip(),
        fingerprint=fingerprint,
        published_at=parsed.published_at,
        collected_at=utc_now(),
    )
    db.add(job)
    db.flush()

    for skill_def in detect_skills(parsed.title, parsed.description):
        skill = _get_or_create_skill(db, skill_def.name, skill_def.category)
        db.add(JobSkill(job_id=job.id, skill_id=skill.id))

    return "created", job


def run_pipeline(db: Session, source_keys: list[str] | None = None) -> list[dict]:
    sources = ensure_sources(db)
    keys = source_keys or list(PARSERS.keys())
    results: list[dict] = []

    for key in keys:
        source = sources[key]
        run = CollectionRun(
            source_id=source.id,
            status="running",
            started_at=utc_now(),
            message=f"Collecting {key}",
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        created = skipped = collected = 0
        try:
            parsed_jobs = collect_source(key)
            collected = len(parsed_jobs)
            for parsed in parsed_jobs:
                status, _job = persist_parsed_job(db, parsed, source)
                if status == "created":
                    created += 1
                else:
                    skipped += 1
            run.status = "success"
            run.message = f"Collected {collected}; created {created}; skipped {skipped}"
        except Exception as exc:  # noqa: BLE001 — surface in run status for demo ops
            run.status = "failed"
            run.message = str(exc)
            db.commit()
            results.append(
                {
                    "source": key,
                    "status": "failed",
                    "message": str(exc),
                    "jobs_collected": 0,
                    "jobs_created": 0,
                    "jobs_skipped": 0,
                }
            )
            continue

        run.finished_at = utc_now()
        run.jobs_collected = collected
        run.jobs_created = created
        run.jobs_skipped = skipped
        db.commit()
        results.append(
            {
                "source": key,
                "status": run.status,
                "message": run.message,
                "jobs_collected": collected,
                "jobs_created": created,
                "jobs_skipped": skipped,
            }
        )

    return results
