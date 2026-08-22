"""G4/G5 golden scenarios: alias normalization with evidence; no LLM required."""

from pathlib import Path

import yaml

from app.services.skills import SkillDictionary, load_skill_dictionary

SKILLS_YML = """
version: test-1
skills:
  SQL: [sql]
  Python: [python]
  dbt: [dbt, dbt core]
  DuckDB: [duckdb]
  PostgreSQL: [postgres, postgresql]
  Experimentation: [a/b test, a/b testing, experimentation, experiment design]
"""


def _dict_from(yml_text: str) -> SkillDictionary:
    raw = yaml.safe_load(yml_text)
    path = Path(__file__).parent / "_tmp_skills_test.yml"
    path.write_text(yml_text, encoding="utf-8")
    try:
        return load_skill_dictionary(path)
    finally:
        path.unlink(missing_ok=True)


def test_g4_postgresql_alias_normalizes_with_evidence() -> None:
    dictionary = _dict_from(SKILLS_YML)
    found = dictionary.extract("Experiência com POSTGRESQL e modelagem de dados.")
    assert len(found) == 1
    ev = found[0]
    assert ev.skill == "PostgreSQL"
    assert ev.method == "dictionary"
    assert ev.confidence == 1.0
    assert "postgresql" in ev.evidence.lower()


def test_g4_multiple_skills_and_alias_forms() -> None:
    dictionary = _dict_from(SKILLS_YML)
    found = dictionary.extract(
        "Vaga: dbt core + python; banco postgres. Desejável duckdb."
    )
    names = {f.skill for f in found}
    assert names == {"dbt", "Python", "PostgreSQL", "DuckDB"}
    for f in found:
        assert f.evidence
        assert f.method == "dictionary"


def test_g5_dictionary_works_without_llm_key(monkeypatch) -> None:
    # Simulate an environment with NO LLM credentials at all.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    dictionary = _dict_from(SKILLS_YML)
    found = dictionary.extract("Precisamos de alguém forte em SQL e A/B testing.")
    names = {f.skill for f in found}
    assert {"SQL", "Experimentation"} <= names
    assert all(f.method == "dictionary" for f in found)


def test_word_boundary_prevents_substring_false_positive() -> None:
    dictionary = _dict_from(SKILLS_YML)
    # 'go' inside 'golang' must not double-count; nonsense words must not match SQL
    found = dictionary.extract("nosql é diferente de sql; golang não é go puro aqui.")
    names = [f.skill for f in found if f.skill == "Go"]
    assert names == []
    sql_hits = [f for f in found if f.skill == "SQL"]
    assert len(sql_hits) == 1


def test_load_real_repo_dictionary() -> None:
    dictionary = load_skill_dictionary()  # default repo path
    assert dictionary.version
    assert len(dictionary.skills) >= 10
