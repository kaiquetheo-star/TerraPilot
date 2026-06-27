"""Testes do assistente de decisão para casos complexos (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.decision_support import (  # noqa: E402
    ComplexCaseInput,
    assess_risks,
    build_case_summary,
    generate_options,
    get_legal_references,
    get_precedents,
    suggest_consultations,
    support_decision,
)


def _case(**overrides) -> ComplexCaseInput:
    defaults = {
        "case_id": "CAR-MT-001",
        "producer_name": "Seu Raimundo",
        "property_size_ha": 30.0,
        "municipality": "Alta Floresta",
        "state": "MT",
        "biome": "Amazonia",
        "issue_code": "APP_RIVER_WIDTH",
        "overlaps_uc": False,
        "uc_type": None,
        "overlaps_ti": False,
        "overlaps_quilombo": False,
        "overlaps_border": False,
        "has_pending_fines": False,
        "fine_count": 0,
        "consolidated_before_2008": False,
        "property_size_modulos": 2.5,
        "legal_issues": [],
    }
    defaults.update(overrides)
    return ComplexCaseInput(**defaults)


def test_build_case_summary_includes_overlaps_and_fines():
    summary = build_case_summary(
        _case(
            overlaps_uc=True,
            uc_type="protecao_integral",
            overlaps_ti=True,
            has_pending_fines=True,
            fine_count=2,
            consolidated_before_2008=True,
        )
    )

    assert "Seu Raimundo" in summary
    assert "Sobrepõe UC (protecao_integral)" in summary
    assert "Sobrepõe Terra Indígena" in summary
    assert "2 multa(s) pendente(s)" in summary
    assert "22/07/2008" in summary


def test_get_legal_references_art_61_a_for_consolidated_area():
    refs = get_legal_references(
        _case(
            consolidated_before_2008=True,
            has_pending_fines=True,
        )
    )

    articles = {r["article"] for r in refs}
    assert "Art. 29" in articles
    assert "Art. 61-A" in articles
    assert "Art. 67" in articles
    assert "Art. 59 §4º e §5º" in articles


def test_get_legal_references_uc_and_ti():
    refs = get_legal_references(
        _case(
            overlaps_uc=True,
            uc_type="protecao_integral",
            overlaps_ti=True,
        )
    )

    laws = {r["law"] for r in refs}
    assert "Lei 9.985/2000 (SNUC)" in laws
    assert "Constituição Federal" in laws


def test_assess_risks_high_for_uc_protecao_integral():
    risks = assess_risks(
        _case(
            overlaps_uc=True,
            uc_type="protecao_integral",
        )
    )

    assert risks["legal_risk"] == "high"
    assert risks["environmental_risk"] == "high"


def test_assess_risks_medium_for_small_family_farm():
    risks = assess_risks(_case(property_size_ha=25))

    assert risks["legal_risk"] == "low"
    assert risks["social_risk"] == "medium"


def test_generate_options_pra_for_pending_fines():
    options = generate_options(_case(has_pending_fines=True, fine_count=1))

    option_ids = {o.option_id for o in options}
    assert "pra_adhesion" in option_ids


def test_generate_options_consolidated_rights_art_61_a():
    options = generate_options(
        _case(
            issue_code="CONSOLIDATED_APP",
            consolidated_before_2008=True,
        )
    )

    consolidated = next(o for o in options if o.option_id == "consolidated_rights")
    assert "Art. 61-A" in consolidated.legal_basis
    assert "Art. 61-A" in consolidated.applicable_articles


def test_generate_options_small_property_art_67():
    options = generate_options(
        _case(
            issue_code="RL_PERCENTAGE",
            property_size_modulos=3,
        )
    )

    small = next(o for o in options if o.option_id == "small_property_rules")
    assert "Art. 67" in small.legal_basis


def test_generate_options_rl_compensation_art_66():
    options = generate_options(_case(issue_code="RL_PERCENTAGE", property_size_modulos=6))

    compensation = next(o for o in options if o.option_id == "rl_compensation")
    assert compensation.legal_basis == "Art. 66 da Lei 12.651/2012"


def test_suggest_consultations_for_complex_overlaps():
    consultations = suggest_consultations(
        _case(
            overlaps_uc=True,
            overlaps_ti=True,
            overlaps_quilombo=True,
            has_pending_fines=True,
            fine_count=6,
        )
    )

    assert "ICMBio (se UC federal) ou órgão estadual de UC" in consultations
    assert "FUNAI" in consultations
    assert "Fundação Palmares / INCRA" in consultations
    assert "Procuradoria do órgão ambiental" in consultations


def test_suggest_consultations_none_when_simple():
    consultations = suggest_consultations(_case())

    assert consultations == ["Nenhuma consulta externa necessária"]


def test_get_precedents_for_uc_and_consolidated():
    precedents = get_precedents(
        _case(
            overlaps_uc=True,
            consolidated_before_2008=True,
        )
    )

    assert len(precedents) == 2
    assert any("SFB 12345" in p["case"] for p in precedents)
    assert any("SFB 67890" in p["case"] for p in precedents)


def test_support_decision_full_structure():
    case = _case(
        overlaps_uc=True,
        uc_type="protecao_integral",
        overlaps_ti=True,
        has_pending_fines=True,
        fine_count=4,
        consolidated_before_2008=True,
        issue_code="RL_PERCENTAGE",
        property_size_modulos=3,
    )

    result = support_decision(case)

    assert result.case_id == "CAR-MT-001"
    assert "Seu Raimundo" in result.case_summary
    assert len(result.legal_references) >= 4
    assert result.risk_assessment["legal_risk"] == "high"
    assert len(result.options) >= 2
    assert len(result.precedents) >= 1
    assert "FUNAI" in result.recommended_consultation
