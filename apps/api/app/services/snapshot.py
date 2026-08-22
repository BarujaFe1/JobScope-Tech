"""Snapshot storage: dedup + derived records for one capture run.

G3 contract:
- same (source, source_job_id) in one snapshot -> keep latest captured_at;
- identical normalized text_hash across sources -> collapse into one record
  and preserve the dropped origin(s) in `duplicate_of`.
"""

from __future__ import annotations

from app.contracts import DedupStats, DerivedJob, NormalizedJob


def build_derived_records(
    jobs: list[NormalizedJob],
) -> tuple[list[DerivedJob], DedupStats]:
    stats = DedupStats(total_input=len(jobs))

    latest_by_key: dict[tuple[str, str], NormalizedJob] = {}
    for job in jobs:
        key = (job.source, job.source_job_id)
        existing = latest_by_key.get(key)
        if existing is None or job.captured_at > existing.captured_at:
            latest_by_key[key] = job
            if existing is not None:
                stats.same_key_collapsed += 1

    survivors: dict[str, DerivedJob] = {}
    order: list[str] = []
    for job in latest_by_key.values():
        if job.text_hash in survivors:
            survivors[job.text_hash].duplicate_of.append(f"{job.source}:{job.source_job_id}")
            stats.cross_source_hash_collapsed += 1
            continue
        derived = DerivedJob(
            **job.model_dump(),
            duplicate_of=[],
        )
        survivors[job.text_hash] = derived
        order.append(job.text_hash)

    return [survivors[h] for h in order], stats
