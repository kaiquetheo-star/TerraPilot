"""
Dashboard da analista — produtores travados e estatísticas de eficácia.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .priority_queue import Case, get_queue_summary, prioritize_cases


class EffectivenessStats(TypedDict):
    total_notifications_sent: int
    translated_vs_technical: dict[str, dict[str, float]]
    channel_effectiveness: dict[str, float]


# Dados de demonstração — substituir por consulta ao banco em produção
_DEMO_CASES: list[Case] = [
    Case(
        case_id="CAR-MT-001",
        producer_name="Seu Raimundo",
        producer_id="123",
        municipality="Alta Floresta - MT",
        property_size_ha=30,
        modulo_fiscal=2.5,
        issue_code="APP_RIVER_WIDTH",
        days_since_notification=15,
        days_since_last_contact=10,
        historical_fix_rate=0.8,
        channel_reached="whatsapp",
        biome="Amazonia",
        has_pending_fines=False,
        is_small_property=True,
    ),
    Case(
        case_id="CAR-MT-002",
        producer_name="Dona Maria",
        producer_id="456",
        municipality="Sinop - MT",
        property_size_ha=12,
        modulo_fiscal=1.2,
        issue_code="RL_PERCENTAGE",
        days_since_notification=8,
        days_since_last_contact=5,
        historical_fix_rate=0.5,
        channel_reached="sms",
        biome="Amazonia",
        has_pending_fines=False,
        is_small_property=True,
    ),
    Case(
        case_id="CAR-MT-003",
        producer_name="João da Silva",
        producer_id="789",
        municipality="Lucas do Rio Verde - MT",
        property_size_ha=85,
        modulo_fiscal=6.8,
        issue_code="RL_OVERLAP_UC",
        days_since_notification=22,
        days_since_last_contact=18,
        historical_fix_rate=0.2,
        channel_reached="email",
        biome="Amazonia",
        has_pending_fines=True,
        is_small_property=False,
    ),
]


def get_stuck_producers(oema_id: str) -> list[dict[str, Any]]:
    """
    Retorna produtores que não fizeram retificação há X dias.

    Prioriza por: tempo sem resposta + gravidade + engajamento + impacto ambiental.
    """
    _ = oema_id  # reservado para filtro por OEMA em produção
    return [pc.model_dump() for pc in prioritize_cases(_DEMO_CASES)]


def get_stuck_producers_summary(oema_id: str) -> dict[str, Any]:
    """Resumo da fila de casos travados para visão rápida da analista."""
    _ = oema_id
    prioritized = prioritize_cases(_DEMO_CASES)
    return get_queue_summary(prioritized)


def get_effectiveness_stats(oema_id: str) -> EffectivenessStats:
    """Estatísticas de eficácia das notificações traduzidas."""
    _ = oema_id
    return EffectivenessStats(
        total_notifications_sent=1247,
        translated_vs_technical={
            "translated": {"first_try_success": 0.85, "avg_days_to_fix": 3.2},
            "technical": {"first_try_success": 0.23, "avg_days_to_fix": 18.7},
        },
        channel_effectiveness={
            "whatsapp": 0.78,
            "sms": 0.45,
            "email": 0.12,
        },
    )
