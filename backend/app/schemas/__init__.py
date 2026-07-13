"""Pydantic API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    env: str
    jobs_count: int


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    slug: str
    count: int | None = None


class JobListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    seniority: str
    work_model: str
    location: str
    source: str
    original_url: str
    skills: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    collected_at: datetime


class JobDetail(JobListItem):
    description: str
    fingerprint: str
    external_id: str


class JobsPage(BaseModel):
    items: list[JobListItem]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    total_jobs: int
    unique_companies: int
    top_skills: list[SkillOut]
    seniority_distribution: dict[str, int]
    work_model_distribution: dict[str, int]
    top_locations: dict[str, int]


class PipelineRunOut(BaseModel):
    id: int
    source: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    jobs_collected: int
    jobs_created: int
    jobs_skipped: int
    message: str | None


class PipelineStatusResponse(BaseModel):
    sources: list[dict]
    recent_runs: list[PipelineRunOut]
    healthy: bool
