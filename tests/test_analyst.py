"""Testes do módulo da analista (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.dashboard_service import get_effectiveness_stats, get_stuck_producers  # noqa: E402
from analyst.notification_generator import generate_simple_notification  # noqa: E402
from analyst.priority_queue import Case, prioritize_cases  # noqa: E402


def test_generate_simple_notification_personalized():
    result = generate_simple_notification(
        "Inconsistência no perímetro da RL - divergência de 2,3ha",
        {"name": "Seu Raimundo"},
    )

    assert "Seu Raimundo" in result["simple_text"]
    assert "Reserva Legal" in result["simple_text"]
    assert "CAR pendente" in result["sms_version"]
    assert len(result["whatsapp_buttons"]) == 3


def test_get_stuck_producers_prioritized():
    producers = get_stuck_producers("MT")

    assert len(producers) >= 1
    assert producers[0]["priority_level"] in ("critical", "high", "medium", "low")
    assert "priority_score" in producers[0]


def test_get_effectiveness_stats():
    stats = get_effectiveness_stats("MT")

    assert stats["total_notifications_sent"] > 0
    assert stats["translated_vs_technical"]["translated"]["first_try_success"] > 0.5
    assert stats["channel_effectiveness"]["whatsapp"] > stats["channel_effectiveness"]["email"]


def test_prioritize_cases_orders_by_score():
    cases = [
        Case(
            case_id="1",
            producer_name="A",
            producer_id="p1",
            municipality="X",
            property_size_ha=10,
            modulo_fiscal=3,
            issue_code="DOC_MISSING",
            days_since_notification=5,
            days_since_last_contact=5,
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
            property_size_ha=80,
            modulo_fiscal=6,
            issue_code="APP_RIVER_WIDTH",
            days_since_notification=20,
            days_since_last_contact=15,
            historical_fix_rate=0.5,
            channel_reached="email",
            biome="Cerrado",
            has_pending_fines=False,
            is_small_property=False,
        ),
    ]
    ordered = prioritize_cases(cases)

    assert ordered[0].case.days_since_notification == 20
