"""Query services for API endpoints."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import CollectionRun, Company, Job, JobSkill, Skill, Source
from app.schemas import (
    JobDetail,
    JobListItem,
    JobsPage,
    PipelineRunOut,
    PipelineStatusResponse,
    SkillOut,
    StatsResponse,
)


def _job_to_list_item(job: Job) -> JobListItem:
    return JobListItem(
        id=job.id,
        title=job.title,
        company=job.company.name,
        seniority=job.seniority,
        work_model=job.work_model,
        location=job.location,
        source=job.source.key,
        original_url=job.original_url,
        skills=[link.skill.name for link in job.skill_links],
        published_at=job.published_at,
        collected_at=job.collected_at,
    )


def list_jobs(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    seniority: str | None = None,
    work_model: str | None = None,
    skill: str | None = None,
    q: str | None = None,
) -> JobsPage:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    stmt = (
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.source),
            selectinload(Job.skill_links).selectinload(JobSkill.skill),
        )
        .join(Company)
        .join(Source)
    )

    if seniority:
        stmt = stmt.where(Job.seniority == seniority)
    if work_model:
        stmt = stmt.where(Job.work_model == work_model)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((Job.title.ilike(like)) | (Company.name.ilike(like)))
    if skill:
        stmt = (
            stmt.join(JobSkill)
            .join(Skill)
            .where((Skill.slug == skill.lower()) | (Skill.name.ilike(skill)))
        )

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    rows = db.scalars(
        stmt.order_by(Job.collected_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    return JobsPage(
        items=[_job_to_list_item(job) for job in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_job(db: Session, job_id: int) -> JobDetail | None:
    job = db.scalar(
        select(Job)
        .where(Job.id == job_id)
        .options(
            selectinload(Job.company),
            selectinload(Job.source),
            selectinload(Job.skill_links).selectinload(JobSkill.skill),
        )
    )
    if job is None:
        return None
    base = _job_to_list_item(job)
    return JobDetail(
        **base.model_dump(),
        description=job.description,
        fingerprint=job.fingerprint,
        external_id=job.external_id,
    )


def get_stats(db: Session) -> StatsResponse:
    total_jobs = db.scalar(select(func.count(Job.id))) or 0
    unique_companies = db.scalar(select(func.count(Company.id))) or 0

    seniority_rows = db.execute(
        select(Job.seniority, func.count(Job.id)).group_by(Job.seniority)
    ).all()
    work_rows = db.execute(
        select(Job.work_model, func.count(Job.id)).group_by(Job.work_model)
    ).all()
    location_rows = db.execute(
        select(Job.location, func.count(Job.id))
        .group_by(Job.location)
        .order_by(func.count(Job.id).desc())
        .limit(8)
    ).all()

    skill_rows = db.execute(
        select(Skill, func.count(JobSkill.id).label("cnt"))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .group_by(Skill.id)
        .order_by(func.count(JobSkill.id).desc())
        .limit(12)
    ).all()

    top_skills = [
        SkillOut(
            id=skill.id,
            name=skill.name,
            category=skill.category,
            slug=skill.slug,
            count=cnt,
        )
        for skill, cnt in skill_rows
    ]

    return StatsResponse(
        total_jobs=total_jobs,
        unique_companies=unique_companies,
        top_skills=top_skills,
        seniority_distribution={k: v for k, v in seniority_rows},
        work_model_distribution={k: v for k, v in work_rows},
        top_locations={k: v for k, v in location_rows},
    )


def list_skills(db: Session) -> list[SkillOut]:
    rows = db.execute(
        select(Skill, func.count(JobSkill.id).label("cnt"))
        .outerjoin(JobSkill, JobSkill.skill_id == Skill.id)
        .group_by(Skill.id)
        .order_by(func.count(JobSkill.id).desc(), Skill.name.asc())
    ).all()
    return [
        SkillOut(id=s.id, name=s.name, category=s.category, slug=s.slug, count=cnt)
        for s, cnt in rows
    ]


def pipeline_status(db: Session) -> PipelineStatusResponse:
    sources = db.scalars(select(Source).order_by(Source.key)).all()
    runs = db.scalars(
        select(CollectionRun)
        .options(selectinload(CollectionRun.source))
        .order_by(CollectionRun.started_at.desc())
        .limit(10)
    ).all()

    recent = [
        PipelineRunOut(
            id=run.id,
            source=run.source.key,
            status=run.status,
            started_at=run.started_at,
            finished_at=run.finished_at,
            jobs_collected=run.jobs_collected,
            jobs_created=run.jobs_created,
            jobs_skipped=run.jobs_skipped,
            message=run.message,
        )
        for run in runs
    ]
    healthy = not any(r.status == "failed" for r in recent[:3]) if recent else True
    return PipelineStatusResponse(
        sources=[{"key": s.key, "name": s.name, "description": s.description} for s in sources],
        recent_runs=recent,
        healthy=healthy,
    )
