"""Deterministic fingerprint for pragmatic deduplication."""

from __future__ import annotations

import hashlib

from app.domain.normalizer import normalize_company_name, normalize_text


def job_fingerprint(title: str, company: str, source_key: str = "") -> str:
    """
    Build a stable fingerprint from normalized title + company.

    Source is intentionally excluded from the hash payload so the same role
    posted on two boards can be recognized as a duplicate. source_key is kept
    in the signature for future multi-strategy dedup without breaking callers.
    """
    _ = source_key
    payload = f"{normalize_text(title)}|{normalize_company_name(company)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
