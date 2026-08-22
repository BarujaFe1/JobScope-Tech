"""FastAPI route modules."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Job
from app.pipeline import run_pipeline
from app.schemas import (
    HealthResponse,
    JobDetail,
    JobsPage,
    PipelineStatusResponse,
    SkillOut,
    StatsResponse,
)
from app.services import queries

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    settings = get_settings()
    count = db.scalar(select(func.count(Job.id))) or 0
    return HealthResponse(
        status="ok",
        demo_mode=settings.jobscope_demo_mode,
        env=settings.jobscope_env,
        jobs_count=count,
    )


@router.get("/jobs", response_model=JobsPage)
def jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    seniority: str | None = None,
    work_model: str | None = None,
    skill: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> JobsPage:
    return queries.list_jobs(
        db,
        page=page,
        page_size=page_size,
        seniority=seniority,
        work_model=work_model,
        skill=skill,
        q=q,
    )


@router.get("/jobs/{job_id}", response_model=JobDetail)
def job_detail(job_id: int, db: Session = Depends(get_db)) -> JobDetail:
    job = queries.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)) -> StatsResponse:
    return queries.get_stats(db)


@router.get("/skills", response_model=list[SkillOut])
def skills(db: Session = Depends(get_db)) -> list[SkillOut]:
    return queries.list_skills(db)


@router.get("/pipeline/status", response_model=PipelineStatusResponse)
def pipeline_status(db: Session = Depends(get_db)) -> PipelineStatusResponse:
    return queries.pipeline_status(db)


@router.post("/pipeline/run")
def pipeline_run(db: Session = Depends(get_db)) -> dict:
    """Re-run fixture collectors (idempotent via dedup fingerprints)."""
    results = run_pipeline(db)
    return {"results": results}
