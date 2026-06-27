"""Testes da fila de prioridade inteligente (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.priority_queue import (  # noqa: E402
    Case,
    calculate_severity_score,
    calculate_time_pressure,
    get_priority_level,
    prioritize_cases,
)


def test_severity_app_spring_highest():
    """Nascente tem severidade máxima (Art. 4º, IV)."""
    assert calculate_severity_score("APP_SPRING_RADIUS") == 10


def test_severity_mangrove_highest():
    """Manguezal protegido integralmente (Art. 4º, VII)."""
    assert calculate_severity_score("APP_MANGROVE") == 10


def test_severity_documentation_lower():
    """Erros documentais têm severidade menor que ambientais."""
    assert calculate_severity_score("DOC_MISSING") < calculate_severity_score("APP_RIVER_WIDTH")


def test_time_pressure_peaks_at_30_days():
    """Pressão temporal aumenta com abandono."""
    assert calculate_time_pressure(35, 35) == 10.0
    assert calculate_time_pressure(5, 5) < calculate_time_pressure(20, 20)


def test_get_priority_level_thresholds():
    assert get_priority_level(80) == "critical"
    assert get_priority_level(60) == "high"
    assert get_priority_level(40) == "medium"
    assert get_priority_level(20) == "low"


def test_prioritize_orders_by_score():
    cases = [
        Case(
            case_id="1",
            producer_name="A",
            producer_id="p1",
            municipality="X",
            property_size_ha=10,
            modulo_fiscal=3,
            issue_code="DOC_MISSING",
            days_since_notification=2,
            days_since_last_contact=2,
            historical_fix_rate=0.5,
            channel_reached="email",
            biome="Cerrado",
            has_pending_fines=False,
            is_small_property=True,
        ),
        Case(
            case_id="2",
            producer_name="B",
            producer_id="p2",
            municipality="X",
            property_size_ha=500,
            modulo_fiscal=15,
            issue_code="APP_MANGROVE",
            days_since_notification=20,
            days_since_last_contact=15,
            historical_fix_rate=0.8,
            channel_reached="whatsapp",
            biome="Mata Atlantica",
            has_pending_fines=True,
            is_small_property=False,
        ),
    ]
    result = prioritize_cases(cases)
    assert result[0].case.case_id == "2"  # manguezal + bioma crítico + multa
    assert result[0].priority_level in ["critical", "high"]


def test_small_property_flagged_in_reasons():
    cases = [
        Case(
            case_id="1",
            producer_name="Raimundo",
            producer_id="p1",
            municipality="Itaberaba-BA",
            property_size_ha=30,
            modulo_fiscal=1,
            issue_code="APP_RIVER_WIDTH",
            days_since_notification=5,
            days_since_last_contact=3,
            historical_fix_rate=0.6,
            channel_reached="whatsapp",
            biome="Caatinga",
            has_pending_fines=False,
            is_small_property=True,
        ),
    ]
    result = prioritize_cases(cases)
    assert any("Pequena propriedade" in r for r in result[0].reasons)


def test_legal_context_references_law():
    cases = [
        Case(
            case_id="1",
            producer_name="X",
            producer_id="p1",
            municipality="Y",
            property_size_ha=100,
            modulo_fiscal=3,
            issue_code="RL_PERCENTAGE",
            days_since_notification=5,
            days_since_last_contact=3,
            historical_fix_rate=0.7,
            channel_reached="whatsapp",
            biome="Cerrado",
            has_pending_fines=False,
            is_small_property=True,
        ),
    ]
    result = prioritize_cases(cases)
    assert "Art. 12" in result[0].legal_context
