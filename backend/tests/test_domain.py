"""Unit tests for domain normalization, taxonomy and dedup."""

from app.domain.dedup import job_fingerprint
from app.domain.normalizer import (
    detect_seniority,
    detect_work_model,
    normalize_company_name,
    normalize_location,
)
from app.domain.taxonomy import detect_skills


def test_detect_seniority_portuguese_and_english():
    assert detect_seniority("Engenheiro de Dados Sênior") == "senior"
    assert detect_seniority("Dev Backend Pleno") == "mid"
    assert detect_seniority("Estágio em Java") == "intern"
    assert detect_seniority("Frontend Developer Junior") == "junior"
    assert detect_seniority("Tech Lead Platform") == "lead"


def test_detect_work_model():
    assert detect_work_model("100% remoto") == "remote"
    assert detect_work_model("Modelo híbrido em SP") == "hybrid"
    assert detect_work_model("Presencial no escritório") == "onsite"


def test_normalize_company_and_location():
    assert normalize_company_name("NuvemPay Tecnologia Ltda") == "nuvempay tecnologia"
    assert normalize_location("Remoto") == "Remoto / BR"
    assert normalize_location("Curitiba, PR") == "Curitiba, PR"


def test_skill_detection_from_noisy_text():
    skills = detect_skills(
        "Python FastAPI",
        "Experiência com PostgreSQL, Docker e AWS. React é diferencial.",
    )
    names = {s.name for s in skills}
    assert "Python" in names
    assert "FastAPI" in names
    assert "PostgreSQL" in names
    assert "Docker" in names
    assert "AWS" in names
    assert "React" in names


def test_fingerprint_dedup_ignores_legal_suffix_and_case():
    a = job_fingerprint("Desenvolvedor Backend Python Pleno", "NuvemPay Tecnologia Ltda")
    b = job_fingerprint("desenvolvedor backend python pleno", "NuvemPay Tecnologia")
    assert a == b
