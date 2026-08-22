"""Signal pipeline: derived records -> public aggregate snapshot (no full text).

Publication policy:
- aggregates only (frequencies, graph edges, bundles, gap statuses);
- skill evidence limited to short snippets + source URL;
- explicit provenance, versions and sample disclaimer.
"""

from __future__ import annotations

from typing import Any

from app.contracts import DerivedJob
from app.services.graph import BUNDLE_SIZE_DEFAULT, build_role_skill_graph
from app.services.portfolio_gap import (
    DEMAND_THRESHOLD_DEFAULT,
    PortfolioEvidence,
    analyze_portfolio_gap,
)
from app.services.roles import classify_role
from app.services.skills import SkillDictionary

SNIPPET_MAX_CHARS = 200
MIN_SUPPORT_DEFAULT = 2
METHODOLOGY_VERSION = "1.0.0"
DISCLAIMER = (
    "Amostra composta apenas pelos boards habilitados em data/config/sources.yml; "
    "não representa todo o mercado brasileiro. Skills extraídas por dicionário "
    "versionado com evidência textual e link para a vaga original."
)


def _snippet(text: str, around: str) -> str:
    lowered = text.lower()
    idx = lowered.find(around.lower())
    start = max(0, idx - 40) if idx >= 0 else 0
    end = min(len(text), start + SNIPPET_MAX_CHARS)
    snippet = text[start:end].strip()
    return ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")


def build_market_snapshot(
    records: list[DerivedJob],
    dictionary: SkillDictionary,
    generated_at: str,
    sources_provenance: list[dict[str, Any]] | None = None,
    demand_threshold: int = DEMAND_THRESHOLD_DEFAULT,
    min_support: int = MIN_SUPPORT_DEFAULT,
    evidence: PortfolioEvidence | None = None,
    bundle_size: int = BUNDLE_SIZE_DEFAULT,
) -> dict[str, Any]:
    annotated: list[dict[str, Any]] = []
    skill_examples: dict[tuple[str, str], dict[str, Any]] = {}
    role_counts: dict[str, int] = {}

    for record in records:
        role_result = classify_role(record.title, record.description_text)
        found = dictionary.extract(record.description_text)
        annotated.append(
            {
                "role": role_result.role,
                "skills": frozenset(e.skill for e in found),
            }
        )
        role_counts[role_result.role] = role_counts.get(role_result.role, 0) + 1
        for ev in found:
            key = (ev.skill, record.source_job_id)
            if key not in skill_examples and ev.evidence:
                skill_examples[key] = {
                    "skill": ev.skill,
                    "snippet": _snippet(record.description_text, ev.skill)[:SNIPPET_MAX_CHARS],
                    "source_url": record.source_url,
                    "company": record.company,
                }

    frequencies: dict[str, dict[str, int]] = {}
    graphs_block: dict[str, Any] = {}

    slices = {None: annotated}
    slices.update({r["role"]: [a for a in annotated if a["role"] == r["role"]] for r in annotated})

    for slice_name, slice_records in slices.items():
        slice_key = slice_name or "_all"
        freq: dict[str, int] = {}
        for item in slice_records:
            for skill in item["skills"]:
                freq[skill] = freq.get(skill, 0) + 1
        frequencies[slice_key] = freq

        graph = build_role_skill_graph(slice_records, min_support=min_support)
        bundles: dict[str, list[str]] = {}
        for node in graph.nodes:
            bundle_edges = graph.bundles_for(node.skill, size=bundle_size)
            neighbors = [
                (e.skill_b if e.skill_a == node.skill else e.skill_a)
                for e in bundle_edges
            ]
            if neighbors:
                bundles[node.skill] = neighbors

        graphs_block[slice_key] = {
            "min_support": min_support,
            "nodes": [node._asdict() for node in graph.nodes],
            "edges": [edge._asdict() for edge in graph.edges],
            "bundles": bundles,
        }

    roles_summary = [
        {"role": role, "jobs": count}
        for role, count in sorted(role_counts.items(), key=lambda kv: -kv[1])
    ]

    market_freq = frequencies.get("_all", {})
    gap_rows: list[dict[str, Any]] = []
    if evidence is not None:
        report = analyze_portfolio_gap(
            market_frequencies=market_freq,
            evidence=evidence,
            demand_threshold=demand_threshold,
        )
        gap_rows = [row.model_dump() for row in report.rows]

    return {
        "meta": {
            "generated_at": generated_at,
            "methodology_version": METHODOLOGY_VERSION,
            "skills_dictionary_version": dictionary.version,
            "sample_size": len(records),
            "sources": sources_provenance or [],
            "demand_threshold": demand_threshold,
            "min_support": min_support,
            "disclaimer": DISCLAIMER,
        },
        "roles": roles_summary,
        "skill_frequencies": frequencies,
        "graphs": graphs_block,
        "evidence_examples": list(skill_examples.values())[:100],
        "gap": {"demand_threshold": demand_threshold, "rows": gap_rows},
    }
