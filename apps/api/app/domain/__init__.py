"""Domain package."""

from app.domain.dedup import job_fingerprint
from app.domain.normalizer import (
    detect_seniority,
    detect_work_model,
    normalize_company_name,
    normalize_location,
    normalize_text,
)
from app.domain.taxonomy import SKILL_CATALOG, detect_skills, skill_slug
from app.domain.types import ParsedJob

__all__ = [
    "ParsedJob",
    "SKILL_CATALOG",
    "detect_seniority",
    "detect_skills",
    "detect_work_model",
    "job_fingerprint",
    "normalize_company_name",
    "normalize_location",
    "normalize_text",
    "skill_slug",
]
