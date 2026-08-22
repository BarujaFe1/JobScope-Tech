"""Role normalization with transparent, ordered rules.

Every classification returns role + reason + the evidence span that triggered it,
so downstream consumers (snapshot, UI) can show *why* a job was classified.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

RoleName = Literal[
    "analytics_engineer",
    "data_analyst",
    "product_analyst",
    "data_scientist",
    "data_engineer",
    "other",
]


@dataclass(frozen=True)
class RoleResult:
    role: RoleName
    reason: str
    evidence: str


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


# Ordered rules: first match wins. Analytics Engineer before generic analyst rules.
_RULES: tuple[tuple[RoleName, str, tuple[str, ...]], ...] = (
    (
        "analytics_engineer",
        "title_or_text_contains_analytics_engineer",
        ("analytics engineer", "engenheiro de analytics"),
    ),
    (
        "product_analyst",
        "title_or_text_contains_product_analyst",
        ("product analyst", "analista de produto", "analista de produtos"),
    ),
    (
        "data_scientist",
        "title_or_text_contains_data_scientist",
        ("data scientist", "cientista de dados"),
    ),
    (
        "data_engineer",
        "title_or_text_contains_data_engineer",
        ("data engineer", "engenheiro de dados", "engenharia de dados"),
    ),
    (
        "data_analyst",
        "title_or_text_contains_data_analyst",
        ("data analyst", "analista de dados", "analista de bi", "bi analyst"),
    ),
)


def _search(terms: tuple[str, ...], haystack: str) -> re.Match[str] | None:
    for term in terms:
        match = re.search(rf"(?<!\w){re.escape(term)}(?!\w)", haystack)
        if match:
            return match
    return None


def classify_role(title: str, description: str = "") -> RoleResult:
    folded_title = _fold(title)
    folded_description = _fold(description)

    for role, reason, terms in _RULES:
        match = _search(terms, folded_title)
        if match:
            return RoleResult(role=role, reason=reason, evidence=match.group(0))

    for role, rule_reason, terms in _RULES:
        match = _search(terms, folded_description)
        if match:
            return RoleResult(
                role=role,
                reason=f"{rule_reason}_in_description",
                evidence=match.group(0),
            )

    return RoleResult(role="other", reason="no_rule_matched", evidence="")
