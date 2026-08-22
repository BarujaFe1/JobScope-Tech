"""Pragmatic skill taxonomy: dictionary + aliases (no LLM)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.normalizer import normalize_text


@dataclass(frozen=True)
class SkillDef:
    name: str
    category: str
    aliases: tuple[str, ...] = ()


SKILL_CATALOG: tuple[SkillDef, ...] = (
    SkillDef("Python", "languages", ("python3", "py")),
    SkillDef("JavaScript", "languages", ("js", "javascript")),
    SkillDef("TypeScript", "languages", ("ts", "typescript")),
    SkillDef("Java", "languages", ("java")),
    SkillDef("Go", "languages", ("golang", "go")),
    SkillDef("SQL", "languages", ("sql")),
    SkillDef("FastAPI", "frameworks", ("fastapi")),
    SkillDef("Django", "frameworks", ("django")),
    SkillDef("React", "frameworks", ("react.js", "reactjs", "react")),
    SkillDef("Next.js", "frameworks", ("nextjs", "next.js", "next")),
    SkillDef("Node.js", "frameworks", ("nodejs", "node.js", "node")),
    SkillDef("Spark", "data", ("apache spark", "pyspark", "spark")),
    SkillDef("Airflow", "data", ("apache airflow", "airflow")),
    SkillDef("dbt", "data", ("dbt")),
    SkillDef("Pandas", "data", ("pandas")),
    SkillDef("AWS", "cloud_infra", ("amazon web services", "aws")),
    SkillDef("GCP", "cloud_infra", ("google cloud", "gcp")),
    SkillDef("Docker", "cloud_infra", ("docker")),
    SkillDef("Kubernetes", "cloud_infra", ("k8s", "kubernetes")),
    SkillDef("PostgreSQL", "databases", ("postgres", "postgresql", "psql")),
    SkillDef("MongoDB", "databases", ("mongo", "mongodb")),
    SkillDef("Redis", "databases", ("redis")),
)


def skill_slug(name: str) -> str:
    return normalize_text(name).replace(" ", "-").replace(".", "")


def _alias_patterns() -> list[tuple[SkillDef, re.Pattern[str]]]:
    patterns: list[tuple[SkillDef, re.Pattern[str]]] = []
    for skill in SKILL_CATALOG:
        terms = (skill.name, *skill.aliases)
        # Longer aliases first to prefer specific matches
        ordered = sorted({normalize_text(t) for t in terms}, key=len, reverse=True)
        for term in ordered:
            if not term:
                continue
            escaped = re.escape(term)
            patterns.append((skill, re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.I)))
    return patterns


_PATTERNS = _alias_patterns()


def detect_skills(*parts: str | None) -> list[SkillDef]:
    blob = normalize_text(" ".join(p for p in parts if p))
    found: dict[str, SkillDef] = {}
    for skill, pattern in _PATTERNS:
        if skill.name in found:
            continue
        if pattern.search(blob):
            found[skill.name] = skill
    return sorted(found.values(), key=lambda s: s.name.lower())
