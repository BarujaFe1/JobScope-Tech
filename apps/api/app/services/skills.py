"""Skill extraction via a versioned dictionary with aliases and evidence spans.

G4: alias surface forms normalize to the canonical skill WITH evidence.
G5: this extractor is pure dictionary — no LLM key required, ever.
Optional LLM enrichment is a documented future hook, never a dependency.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import yaml

RepoRoot = Path(__file__).resolve().parents[4]
DEFAULT_SKILLS_PATH = RepoRoot / "data" / "config" / "skills.yml"

EvidenceWindow = 60


class _Pattern(NamedTuple):
    canonical: str
    regex: re.Pattern[str]


class SkillDictionary:
    def __init__(self, version: str, skills: dict[str, list[str]]) -> None:
        self.version = version
        self.skills = skills
        self._patterns = self._compile(skills)

    @staticmethod
    def _compile(skills: dict[str, list[str]]) -> list[_Pattern]:
        patterns: list[_Pattern] = []
        for canonical, aliases in skills.items():
            terms = {canonical.lower(), *(a.lower() for a in aliases)}
            # longest first so specific forms win before short generic ones
            for term in sorted((t for t in terms if t), key=len, reverse=True):
                escaped = re.escape(term)
                regex = re.compile(rf"(?<![\w#]){escaped}(?![\w+])", re.IGNORECASE)
                patterns.append(_Pattern(canonical, regex))
        return patterns

    def extract(self, text: str) -> list:
        from app.contracts import SkillEvidence  # local import avoids cycle

        found: dict[str, SkillEvidence] = {}
        for pattern in self._patterns:
            match = pattern.regex.search(text)
            if not match or pattern.canonical.lower() == "r":
                continue
            if pattern.canonical in found:
                continue
            start = max(0, match.start() - EvidenceWindow)
            end = min(len(text), match.end() + EvidenceWindow)
            snippet = text[start:end].strip()
            snippet = ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")
            found[pattern.canonical] = SkillEvidence(
                skill=pattern.canonical,
                confidence=1.0,
                evidence=snippet,
                method="dictionary",
            )
        return sorted(found.values(), key=lambda e: e.skill.lower())


def load_skill_dictionary(path: Path | str | None = None) -> SkillDictionary:
    skills_path = Path(path) if path else DEFAULT_SKILLS_PATH
    raw = yaml.safe_load(skills_path.read_text(encoding="utf-8")) or {}
    skills = raw.get("skills")
    if not isinstance(skills, dict) or not skills:
        raise ValueError(f"{skills_path} must define a non-empty 'skills' mapping")
    return SkillDictionary(version=str(raw.get("version", "unversioned")), skills=skills)
