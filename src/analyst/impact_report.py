"""
Relatório de impacto do trabalho da analista Luana.
Resolve: "Luana não vê o impacto do próprio trabalho"
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnalystAction(BaseModel):
    analyst_id: str
    case_id: str
    producer_id: str
    producer_name: str
    action_type: str  # "notification_sent", "call_made", "visit", "approved", "rejected"
    issue_code: str
    channel: str
    timestamp: datetime
    days_to_fix: int  # dias entre ação e correção (se aplicável)
    fixed: bool
    property_size_ha: float
    credit_rural_value_brl: float  # valor estimado do crédito rural liberado


class AnalystImpact(BaseModel):
    analyst_id: str
    period_start: str
    period_end: str
    metrics: dict[str, Any]
    success_stories: list[dict[str, Any]]
    environmental_impact: dict[str, Any]
    economic_impact: dict[str, Any]
    peer_comparison: dict[str, Any]  # comparação saudável com média


# Valores médios estimados para cálculo de impacto
# Baseado em dados públicos do Plano Safra
CREDIT_RURAL_AVG_PER_HA = 3500  # R$/ha em média
CO2_SEQUESTERED_PER_HA_RL = 15  # toneladas CO2/ano por ha de RL recuperada
WATER_PROTECTED_PER_HA_APP = 500  # m³/ano por ha de APP


def calculate_metrics(actions: list[AnalystAction]) -> dict[str, Any]:
    """Métricas consolidadas do período."""
    if not actions:
        return {}

    notifications_sent = [a for a in actions if a.action_type == "notification_sent"]
    approved = [a for a in actions if a.action_type == "approved"]
    calls_made = [a for a in actions if a.action_type == "call_made"]

    fixed_cases = [a for a in actions if a.fixed]
    avg_days_to_fix = (
        sum(a.days_to_fix for a in fixed_cases if a.days_to_fix) / len(fixed_cases)
        if fixed_cases
        else 0
    )

    first_try_rate = len(fixed_cases) / len(notifications_sent) if notifications_sent else 0

    return {
        "cases_analyzed": len({a.case_id for a in actions}),
        "producers_helped": len({a.producer_id for a in actions}),
        "notifications_sent": len(notifications_sent),
        "calls_made": len(calls_made),
        "cases_approved": len(approved),
        "first_try_success_rate": round(first_try_rate, 3),
        "avg_days_to_fix": round(avg_days_to_fix, 1),
        "total_working_days_in_period": _estimate_working_days(actions),
    }


def _estimate_working_days(actions: list[AnalystAction]) -> int:
    if not actions:
        return 0
    dates = sorted({a.timestamp.date() for a in actions})
    return len(dates)


def calculate_environmental_impact(actions: list[AnalystAction]) -> dict[str, Any]:
    """Impacto ambiental gerado pelo trabalho da analista."""
    approved = [a for a in actions if a.action_type == "approved"]

    total_ha_regularized = sum(a.property_size_ha for a in approved)
    estimated_app_rl_ha = total_ha_regularized * 0.2

    return {
        "total_ha_regularized": round(total_ha_regularized, 1),
        "estimated_app_rl_ha": round(estimated_app_rl_ha, 1),
        "co2_sequestered_tons_year": round(estimated_app_rl_ha * CO2_SEQUESTERED_PER_HA_RL, 1),
        "water_protected_m3_year": round(estimated_app_rl_ha * WATER_PROTECTED_PER_HA_APP, 0),
        "equivalent_trees_planted": round(estimated_app_rl_ha * 150, 0),
        "narrative": (
            f"Seu trabalho regularizou {total_ha_regularized:.0f} hectares. "
            f"Isso equivale a plantar {estimated_app_rl_ha * 150:.0f} árvores "
            f"e sequestrar {estimated_app_rl_ha * CO2_SEQUESTERED_PER_HA_RL:.0f} toneladas "
            f"de CO2 por ano."
        ),
    }


def calculate_economic_impact(actions: list[AnalystAction]) -> dict[str, Any]:
    """Impacto econômico gerado para os produtores."""
    approved = [a for a in actions if a.action_type == "approved"]

    total_credit_value = sum(
        a.credit_rural_value_brl or (a.property_size_ha * CREDIT_RURAL_AVG_PER_HA)
        for a in approved
    )

    days_saved = sum(max(0, 14 - (a.days_to_fix or 14)) for a in approved)
    producer_time_value = days_saved * 150

    return {
        "credit_rural_unlocked_brl": round(total_credit_value, 2),
        "producer_time_saved_days": days_saved,
        "producer_time_value_brl": round(producer_time_value, 2),
        "avg_credit_per_producer": round(total_credit_value / len(approved), 2) if approved else 0,
        "narrative": (
            f"Você ajudou a destravar R$ {total_credit_value:,.0f} em crédito rural "
            f"para {len(approved)} produtores."
        ),
    }


def extract_success_stories(actions: list[AnalystAction], top_n: int = 3) -> list[dict[str, Any]]:
    """Histórias de sucesso para motivar a analista."""
    approved = [a for a in actions if a.action_type == "approved"]
    sorted_by_speed = sorted(approved, key=lambda a: a.days_to_fix or 999)

    stories = []
    for action in sorted_by_speed[:top_n]:
        stories.append(
            {
                "producer_name": action.producer_name,
                "issue_code": action.issue_code,
                "days_to_fix": action.days_to_fix,
                "property_size_ha": action.property_size_ha,
                "channel": action.channel,
                "narrative": (
                    f"{action.producer_name} corrigiu em {action.days_to_fix} dias "
                    f"após contato via {action.channel}."
                ),
            }
        )
    return stories


def generate_peer_comparison(
    actions: list[AnalystAction],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    """Comparação com média de outras analistas (benchmark externo)."""
    metrics = calculate_metrics(actions)

    if not metrics or not benchmark:
        return {}

    comparisons = {}
    for key in ["first_try_success_rate", "avg_days_to_fix"]:
        if key in metrics and key in benchmark:
            analyst_value = metrics[key]
            benchmark_value = benchmark[key]

            if key == "avg_days_to_fix":
                delta = benchmark_value - analyst_value
                better = delta > 0
            else:
                delta = analyst_value - benchmark_value
                better = delta > 0

            comparisons[key] = {
                "your_value": analyst_value,
                "benchmark": benchmark_value,
                "delta": round(delta, 3),
                "better_than_average": better,
            }

    return comparisons


def generate_impact_report(
    analyst_id: str,
    actions: list[AnalystAction],
    benchmark: dict[str, Any] | None = None,
) -> AnalystImpact:
    """Gera relatório completo de impacto."""
    if not actions:
        return AnalystImpact(
            analyst_id=analyst_id,
            period_start="",
            period_end="",
            metrics={},
            success_stories=[],
            environmental_impact={},
            economic_impact={},
            peer_comparison={},
        )

    timestamps = sorted(a.timestamp for a in actions)

    return AnalystImpact(
        analyst_id=analyst_id,
        period_start=timestamps[0].isoformat(),
        period_end=timestamps[-1].isoformat(),
        metrics=calculate_metrics(actions),
        success_stories=extract_success_stories(actions),
        environmental_impact=calculate_environmental_impact(actions),
        economic_impact=calculate_economic_impact(actions),
        peer_comparison=generate_peer_comparison(actions, benchmark or {}),
    )
