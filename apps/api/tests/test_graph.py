"""G6 golden scenario: graph excludes edges below minimum support."""

from app.services.graph import build_role_skill_graph


def _record(skills: list[str], role: str = "data_analyst"):
    return {"role": role, "skills": frozenset(skills)}


def _sample_records():
    # SQL+Python co-occur 3x -> edge kept at min_support=2
    # SQL+Excel co-occur 1x -> edge dropped at min_support=2
    return [
        _record(["SQL", "Python", "Excel"]),
        _record(["SQL", "Python"]),
        _record(["SQL", "Python"]),
        _record(["Tableau"]),
        _record(["Tableau"]),
    ]


def test_g6_edge_below_min_support_is_excluded() -> None:
    result = build_role_skill_graph(_sample_records(), min_support=2)
    edges = {(e.skill_a, e.skill_b): e for e in result.edges}
    assert ("SQL", "Python") in edges or ("Python", "SQL") in edges
    assert ("SQL", "Excel") not in edges and ("Excel", "SQL") not in edges


def test_g6_pair_at_threshold_is_included_with_metrics() -> None:
    result = build_role_skill_graph(_sample_records(), min_support=2)
    edge = next(
        e
        for e in result.edges
        if {e.skill_a, e.skill_b} == {"SQL", "Python"}
    )
    assert edge.support == 3
    assert abs(edge.jaccard - 3 / 3) < 1e-9  # union = {SQL, Python} appears in same 3 records


def test_g6_min_support_zero_still_requires_cooccurrence() -> None:
    result = build_role_skill_graph(_sample_records(), min_support=0)
    pairs = {frozenset((e.skill_a, e.skill_b)) for e in result.edges}
    assert frozenset(("SQL", "Excel")) in pairs


def test_node_frequencies_counted_per_role() -> None:
    result = build_role_skill_graph(_sample_records(), min_support=2)
    freqs = {n.skill: n.frequency for n in result.nodes}
    assert freqs["SQL"] == 3
    assert freqs["Tableau"] == 2
    assert freqs["Excel"] == 1


def test_role_filter_restricts_records() -> None:
    records = [
        _record(["SQL", "Python"], role="data_analyst"),
        _record(["Terraform", "AWS"], role="data_engineer"),
        _record(["Terraform", "AWS"], role="data_engineer"),
        _record(["Terraform", "AWS"], role="data_engineer"),
    ]
    result = build_role_skill_graph(records, role="data_engineer", min_support=2)
    skills = {n.skill for n in result.nodes}
    assert skills == {"Terraform", "AWS"}
    assert len(result.edges) == 1


def test_bundles_are_top_neighbors_by_support() -> None:
    result = build_role_skill_graph(_sample_records(), min_support=2)
    bundle = result.bundles_for("SQL")
    assert len(bundle) >= 1
    top = bundle[0]
    neighbor = top.skill_b if top.skill_a == "SQL" else top.skill_a
    assert neighbor == "Python"


def test_empty_input_returns_empty_graph() -> None:
    result = build_role_skill_graph([], min_support=2)
    assert result.nodes == [] and result.edges == []
