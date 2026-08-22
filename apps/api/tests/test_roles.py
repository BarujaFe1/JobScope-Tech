"""Role normalization: transparent rules with recorded reason/evidence."""

import pytest

from app.services.roles import classify_role


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Analytics Engineer", "analytics_engineer"),
        ("Senior Analytics Engineer", "analytics_engineer"),
        ("Analytics Engineer II (Remote)", "analytics_engineer"),
        ("Data Analyst", "data_analyst"),
        ("Analista de Dados Jr", "data_analyst"),
        ("Product Analyst", "product_analyst"),
        ("Analista de Produto Sênior", "product_analyst"),
        ("Data Scientist", "data_scientist"),
        ("Cientista de Dados", "data_scientist"),
        ("Data Engineer", "data_engineer"),
        ("Engenheiro de Dados Pleno", "data_engineer"),
        ("Tech Lead Data Platform", "other"),
        ("Marketing Analyst", "other"),
    ],
)
def test_title_classification_rules(title: str, expected: str) -> None:
    result = classify_role(title)
    assert result.role == expected


def test_result_carries_reason_and_evidence() -> None:
    result = classify_role("Senior Analytics Engineer")
    assert result.reason
    assert "analytics engineer" in result.evidence.lower()


def test_other_role_has_explicit_reason() -> None:
    result = classify_role("Chief Happiness Officer")
    assert result.role == "other"
    assert result.reason == "no_rule_matched"


def test_priority_analytics_engineer_beats_generic_data_terms() -> None:
    # 'Analytics Engineer' must not be swallowed by the broader 'analyst/data' rules
    result = classify_role("Analytics Engineer - Data Team")
    assert result.role == "analytics_engineer"


def test_description_hint_used_when_title_ambiguous() -> None:
    result = classify_role("Vaga Tech", description="Você atuará como Data Engineer...")
    assert result.role == "data_engineer"


def test_empty_title_falls_back_to_other() -> None:
    assert classify_role("").role == "other"
