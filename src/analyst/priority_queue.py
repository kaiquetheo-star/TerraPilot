"""
Fila de prioridade inteligente para a analista Luana.
Resolve o gargalo: "Luana analisa 200 CARs por mês e não sabe qual priorizar"
Baseado no briefing do haCARthon - persona Luana.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import BaseModel


class Case(BaseModel):
    case_id: str
    producer_name: str
    producer_id: str
    municipality: str
    property_size_ha: float
    modulo_fiscal: float  # tamanho em módulos fiscais
    issue_code: str  # ex: APP_RIVER_WIDTH, RL_PERCENTAGE
    days_since_notification: int
    days_since_last_contact: int
    historical_fix_rate: float  # 0.0 a 1.0 — % de vezes que esse produtor corrigiu na 1ª tentativa
    channel_reached: str  # whatsapp, sms, email, none
    biome: str
    has_pending_fines: bool
    is_small_property: bool  # <= 4 módulos fiscais (Art. 3º, V)


class PrioritizedCase(BaseModel):
    case: Case
    priority_score: float
    priority_level: str  # "critical", "high", "medium", "low"
    reasons: list[str]
    recommended_action: str
    legal_context: str  # artigo da Lei 12.651 aplicável


# Pesos calibrados com base em impacto ambiental real
SEVERITY_WEIGHTS = {
    # APPs têm peso alto (Art. 4º — proteção de recursos hídricos)
    "APP_RIVER_WIDTH": 9,
    "APP_SPRING_RADIUS": 10,  # nascente é crítica (Art. 4º, IV)
    "APP_LAKE_MARGIN": 8,
    "APP_VEREDA": 9,  # vereda (Art. 4º, XI) — ecossistema frágil
    "APP_MANGROVE": 10,  # manguezal (Art. 4º, VII) — proteção total
    "APP_RESTINGA": 9,
    "APP_HILLTOP": 7,
    "APP_SLOPE_45": 8,  # encosta >45º (Art. 4º, V) — risco geológico
    # Reserva Legal (Art. 12)
    "RL_PERCENTAGE": 8,
    "RL_LOCATION": 6,
    "RL_OVERLAP_UC": 10,  # sobrepõe UC — altíssimo
    "RL_OVERLAP_TI": 10,  # sobrepõe Terra Indígena
    # Áreas consolidadas (Art. 61-A) — menor peso (direito adquirido)
    "CONSOLIDATED_APP": 4,
    "CONSOLIDATED_RL": 4,
    # Documentação
    "DOC_MISSING": 3,
    "DOC_INCONSISTENT": 5,
    # PRA (Art. 59)
    "PRA_PENDING": 6,
}


def calculate_severity_score(issue_code: str) -> float:
    """Retorna 0-10 baseado no impacto ambiental/legal do erro."""
    return SEVERITY_WEIGHTS.get(issue_code, 5)


def calculate_time_pressure(
    days_since_notification: int,
    days_since_last_contact: int,
) -> float:
    """
    Pressão temporal: quanto mais tempo sem resposta, maior urgência.
    0-10. Pico em 15-30 dias (janela crítica de correção).
    """
    _ = days_since_last_contact  # reservado para refinamento futuro
    if days_since_notification > 30:
        return 10.0  # abandonou — precisa de intervenção ativa
    if days_since_notification > 15:
        return 8.0
    if days_since_notification > 7:
        return 6.0
    if days_since_notification > 3:
        return 4.0
    return 2.0


def calculate_producer_engagement(
    historical_fix_rate: float,
    channel_reached: str,
) -> float:
    """
    Produtor engajado = correção rápida esperada = prioridade alta.
    Produtor travado = precisa de abordagem diferente.
    """
    score = historical_fix_rate * 5  # 0-5

    if channel_reached == "whatsapp":
        score += 3  # canal mais eficaz (briefing: produtor usa WhatsApp)
    elif channel_reached == "sms":
        score += 1
    elif channel_reached == "email":
        score += 0.5

    return min(score, 10)


def calculate_environmental_impact(
    property_size_ha: float,
    biome: str,
    has_pending_fines: bool,
) -> float:
    """
    Impacto ambiental absoluto da regularização.
    Propriedade grande + bioma crítico = alto impacto.
    """
    size_score = min(property_size_ha / 100, 5)  # 0-5

    biome_weight = {
        "Amazonia": 5,
        "Cerrado": 4,
        "Mata Atlantica": 5,
        "Caatinga": 3,
        "Pampa": 3,
        "Pantanal": 5,
    }.get(biome, 3)

    fine_bonus = 2 if has_pending_fines else 0

    return min(size_score + biome_weight + fine_bonus, 10)


def calculate_priority_score(case: Case) -> float:
    """
    Score final ponderado (0-100).
    Pesos: severidade (40%) + tempo (25%) + engajamento (15%) + impacto (20%)
    """
    severity = calculate_severity_score(case.issue_code) * 4  # 40%
    time_p = calculate_time_pressure(
        case.days_since_notification,
        case.days_since_last_contact,
    ) * 2.5  # 25%
    engagement = calculate_producer_engagement(
        case.historical_fix_rate,
        case.channel_reached,
    ) * 1.5  # 15%
    impact = calculate_environmental_impact(
        case.property_size_ha,
        case.biome,
        case.has_pending_fines,
    ) * 2  # 20%

    return round(severity + time_p + engagement + impact, 2)


def get_priority_level(score: float) -> str:
    if score >= 75:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def generate_reasons(case: Case) -> list[str]:
    """Gera razões legíveis em português para a Luana."""
    reasons = []

    if case.days_since_notification > 15:
        reasons.append(f"Sem resposta há {case.days_since_notification} dias")

    severity = calculate_severity_score(case.issue_code)
    if severity >= 8:
        reasons.append("Erro de alto impacto ambiental")

    if case.has_pending_fines:
        reasons.append("Possui multas pendentes")

    if case.is_small_property:
        reasons.append("Pequena propriedade — regras simplificadas (Art. 67)")

    if case.biome in ["Amazonia", "Mata Atlantica", "Pantanal"]:
        reasons.append(f"Bioma prioritário: {case.biome}")

    if case.historical_fix_rate >= 0.7:
        reasons.append("Produtor costuma corrigir rapidamente")

    if case.channel_reached == "whatsapp":
        reasons.append("Canal WhatsApp ativo — alta probabilidade de resposta")

    return reasons


def recommend_action(case: Case, score: float) -> str:
    """Recomendação de ação baseada no perfil do caso."""
    if score >= 75:
        if case.days_since_notification > 30:
            return "Ligar diretamente + agendar visita técnica (se disponível)"
        return "Enviar áudio explicativo via WhatsApp + follow-up em 48h"

    if score >= 55:
        if case.channel_reached == "whatsapp":
            return "Enviar notificação traduzida via WhatsApp"
        return "Enviar SMS + ligação em 3 dias"

    if score >= 35:
        return "Aguardar resposta — enviar lembrete em 7 dias"

    return "Baixa prioridade — monitoramento passivo"


def get_legal_context(case: Case) -> str:
    """Contexto legal relevante para a analista."""
    legal_map = {
        "APP_RIVER_WIDTH": "Art. 4º, I — faixa marginal de cursos d'água",
        "APP_SPRING_RADIUS": "Art. 4º, IV — raio de 50m em nascentes perenes",
        "APP_MANGROVE": "Art. 4º, VII — manguezais em toda extensão",
        "APP_VEREDA": "Art. 4º, XI — 50m a partir do espaço brejoso",
        "APP_SLOPE_45": "Art. 4º, V — encostas >45º (100% declive)",
        "RL_PERCENTAGE": "Art. 12 — percentuais mínimos de RL por bioma",
        "RL_OVERLAP_UC": "Art. 14, III — corredores ecológicos com UC",
        "CONSOLIDATED_APP": "Art. 61-A — áreas consolidadas antes de 22/07/2008",
        "CONSOLIDATED_RL": "Art. 67 — pequenas propriedades (≤4 módulos fiscais)",
        "PRA_PENDING": "Art. 59 — Programa de Regularização Ambiental",
    }
    return legal_map.get(case.issue_code, "Lei 12.651/2012")


def prioritize_cases(cases: list[Case]) -> list[PrioritizedCase]:
    """
    Recebe lista de casos e retorna ordenados por prioridade decrescente.
    """
    results = []
    for case in cases:
        score = calculate_priority_score(case)
        results.append(
            PrioritizedCase(
                case=case,
                priority_score=score,
                priority_level=get_priority_level(score),
                reasons=generate_reasons(case),
                recommended_action=recommend_action(case, score),
                legal_context=get_legal_context(case),
            )
        )
    return sorted(results, key=lambda x: x.priority_score, reverse=True)


def get_queue_summary(cases: list[PrioritizedCase]) -> dict[str, Any]:
    """Resumo da fila para a Luana ver em um olhar."""
    by_level = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for c in cases:
        by_level[c.priority_level] += 1

    total = len(cases)
    return {
        "total_cases": total,
        "by_priority_level": by_level,
        "avg_score": round(sum(c.priority_score for c in cases) / total, 2) if total else 0,
        "top_action_needed": cases[0].recommended_action if cases else None,
        "oldest_case_days": max((c.case.days_since_notification for c in cases), default=0),
        "most_common_issue": _most_common_issue(cases),
    }


def _most_common_issue(cases: list[PrioritizedCase]) -> dict[str, int]:
    counts = Counter(c.case.issue_code for c in cases)
    if not counts:
        return {}
    top = counts.most_common(1)[0]
    return {"issue_code": top[0], "count": top[1]}
