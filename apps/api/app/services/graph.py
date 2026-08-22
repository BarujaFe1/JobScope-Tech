"""Skill co-occurrence graph per role.

G6 contract: an edge exists only if the pair co-occurs in at least `min_support`
records within the selected role slice. Metrics: support + Jaccard.
Bundles: top co-occurring neighbors per skill (market bundles).
"""

from __future__ import annotations

from typing import NamedTuple

MIN_SUPPORT_DEFAULT = 2
BUNDLE_SIZE_DEFAULT = 5


class GraphNode(NamedTuple):
    skill: str
    frequency: int


class GraphEdge(NamedTuple):
    skill_a: str
    skill_b: str
    support: int
    jaccard: float


class RoleSkillGraph(NamedTuple):
    role: str | None
    min_support: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]

    def bundles_for(self, skill: str, size: int = BUNDLE_SIZE_DEFAULT) -> list[GraphEdge]:
        neighbors = [
            e for e in self.edges if e.skill_a == skill or e.skill_b == skill
        ]
        return sorted(
            neighbors,
            key=lambda e: (-e.support, e.jaccard),
        )[:size]


def build_role_skill_graph(
    records: list[dict],
    role: str | None = None,
    min_support: int = MIN_SUPPORT_DEFAULT,
) -> RoleSkillGraph:
    selected = [r for r in records if role is None or r["role"] == role]

    frequency: dict[str, int] = {}
    pair_support: dict[frozenset[str], int] = {}
    union_count: dict[frozenset[str], int] = {}

    for record in selected:
        skills = frozenset(record["skills"])
        for skill in skills:
            frequency[skill] = frequency.get(skill, 0) + 1
        ordered = sorted(skills)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 :]:
                pair = frozenset((a, b))
                pair_support[pair] = pair_support.get(pair, 0) + 1

    # union count per pair: freq(a) + freq(b) - support(a,b) within the same slice
    for pair, support in pair_support.items():
        a, b = tuple(pair)
        union_count[pair] = frequency[a] + frequency[b] - support

    nodes = sorted(
        (GraphNode(skill=s, frequency=f) for s, f in frequency.items()),
        key=lambda n: (-n.frequency, n.skill),
    )
    edges = [
        GraphEdge(
            skill_a=a,
            skill_b=b,
            support=support,
            jaccard=support / union_count[pair] if union_count[pair] else 0.0,
        )
        for pair, support in pair_support.items()
        if support >= min_support
        for a, b in [tuple(pair)]
    ]
    edges.sort(key=lambda e: (-e.support, e.skill_a, e.skill_b))

    return RoleSkillGraph(role=role, min_support=min_support, nodes=nodes, edges=edges)
