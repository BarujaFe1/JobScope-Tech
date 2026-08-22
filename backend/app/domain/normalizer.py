"""Domain: text normalization helpers for Brazilian tech job posts."""

from __future__ import annotations

import re
import unicodedata

SENIORITY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("intern", re.compile(r"\b(estagi[aá]rio|est[aá]gio|intern)\b", re.I)),
    ("junior", re.compile(r"\b(j[uú]nior|junior|jr\.?)\b", re.I)),
    ("mid", re.compile(r"\b(pleno|mid[- ]?level|mid)\b", re.I)),
    ("senior", re.compile(r"\b(s[eê]nior|senior|sr\.?)\b", re.I)),
    ("lead", re.compile(r"\b(tech\s*lead|lead|staff|principal)\b", re.I)),
]

WORK_MODEL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("remote", re.compile(r"\b(remoto|remote|home\s*office|100%\s*remoto)\b", re.I)),
    ("hybrid", re.compile(r"\b(h[ií]brido|hybrid)\b", re.I)),
    ("onsite", re.compile(r"\b(presencial|on[- ]?site|escrit[oó]rio)\b", re.I)),
]


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return collapse_whitespace(strip_accents(value).lower())


def normalize_company_name(value: str | None) -> str:
    text = normalize_text(value)
    text = re.sub(r"\b(ltda|s\.?a\.?|inc|corp|me|eireli)\b", "", text)
    return collapse_whitespace(text)


def detect_seniority(*parts: str | None) -> str:
    blob = " ".join(p for p in parts if p)
    for label, pattern in SENIORITY_PATTERNS:
        if pattern.search(blob):
            return label
    return "unspecified"


def detect_work_model(*parts: str | None) -> str:
    blob = " ".join(p for p in parts if p)
    for label, pattern in WORK_MODEL_PATTERNS:
        if pattern.search(blob):
            return label
    return "unspecified"


def normalize_location(value: str | None) -> str:
    if not value:
        return "Brasil"
    text = collapse_whitespace(value)
    # Common remote markers → Remoto / BR
    if re.search(r"remoto|remote|anywhere", text, re.I):
        return "Remoto / BR"
    return text
