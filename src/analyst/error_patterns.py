"""
Detecta padrões de erro para ajudar a Luana a agir preventivamente.
Resolve o gargalo: "Luana vê os mesmos erros repetidos sem dados agregados"
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel


class ErrorRecord(BaseModel):
    case_id: str
    issue_code: str
    producer_id: str
    municipality: str
    biome: str
    property_size_ha: float
    modulo_fiscal: float
    days_to_fix: int  # dias entre notificação e correção (ou 0 se não corrigiu)
    fixed: bool
    fix_attempt_count: int
    channel: str  # whatsapp, sms, email, in_person
    translated_notification_used: bool


class PatternInsight(BaseModel):
    pattern_type: str  # "top_error", "regional", "biome", "size_class", "channel_effectiveness"
    description: str
    evidence: dict[str, Any]
    recommendation: str
    confidence: float  # 0-1


def analyze_top_errors(records: list[ErrorRecord], top_n: int = 5) -> PatternInsight | None:
    """Identifica os N erros mais comuns."""
    if not records:
        return None

    counter = Counter(r.issue_code for r in records)
    top = counter.most_common(top_n)
    total = len(records)

    top_list = []
    for issue, count in top:
        pct = count / total
        issue_records = [r for r in records if r.issue_code == issue and r.fixed]
        avg_days = (
            sum(r.days_to_fix for r in issue_records) / len(issue_records)
            if issue_records
            else None
        )
        top_list.append(
            {
                "issue_code": issue,
                "count": count,
                "percentage": round(pct, 3),
                "avg_days_to_fix": round(avg_days, 1) if avg_days else None,
            }
        )

    top_issue = top_list[0]["issue_code"]
    top_pct = round(top_list[0]["percentage"] * 100, 1)

    return PatternInsight(
        pattern_type="top_error",
        description=f"'{top_issue}' é o erro mais comum ({top_pct}% dos casos)",
        evidence={"top_errors": top_list, "total_records": total},
        recommendation=_recommend_for_top_issue(top_issue, top_pct),
        confidence=0.9 if total >= 50 else 0.6,
    )


def _recommend_for_top_issue(issue_code: str, percentage: float) -> str:
    """Recomendação baseada no tipo de erro mais comum."""
    recommendations = {
        "APP_RIVER_WIDTH": (
            f"Criar guia específico de APP de rio (Art. 4º, I). "
            f"{percentage}% dos erros são desse tipo — um guia proativo "
            f"pode reduzir 60-70% do retrabalho."
        ),
        "RL_PERCENTAGE": (
            f"Criar calculadora de RL por bioma (Art. 12). "
            f"{percentage}% dos erros são percentuais errados."
        ),
        "CONSOLIDATED_APP": (
            f"Envio proativo de FAQ sobre Art. 61-A (áreas consolidadas). "
            f"Muitos produtores não conhecem seus direitos adquiridos."
        ),
        "DOC_MISSING": (
            f"Checklist de documentos obrigatórios antes de enviar retificação. "
            f"{percentage}% dos casos têm documentação incompleta."
        ),
        "PRA_PENDING": (
            f"Campanha sobre PRA (Art. 59): suspensão de multas + manutenção de crédito rural."
        ),
    }
    return recommendations.get(issue_code, f"Criar material educativo específico para '{issue_code}'.")


def analyze_regional_patterns(records: list[ErrorRecord]) -> list[PatternInsight]:
    """Identifica municípios com concentração anômala de erros."""
    if len(records) < 20:
        return []

    by_municipality: dict[str, list[ErrorRecord]] = defaultdict(list)
    for r in records:
        by_municipality[r.municipality].append(r)

    insights = []
    avg_errors_per_muni = len(records) / len(by_municipality)

    for muni, muni_records in by_municipality.items():
        if len(muni_records) > avg_errors_per_muni * 3 and len(muni_records) >= 10:
            counter = Counter(r.issue_code for r in muni_records)
            top_issue = counter.most_common(1)[0][0]

            insights.append(
                PatternInsight(
                    pattern_type="regional",
                    description=(
                        f"{muni} tem {len(muni_records)} casos — "
                        f"{len(muni_records) / avg_errors_per_muni:.1f}x acima da média"
                    ),
                    evidence={
                        "municipality": muni,
                        "count": len(muni_records),
                        "multiplier": round(len(muni_records) / avg_errors_per_muni, 1),
                        "top_issue": top_issue,
                    },
                    recommendation=(
                        f"Visita técnica ou ação coletiva em {muni} — "
                        f"erro concentrado em '{top_issue}'."
                    ),
                    confidence=0.8,
                )
            )

    return sorted(insights, key=lambda x: x.evidence["multiplier"], reverse=True)


def analyze_biome_patterns(records: list[ErrorRecord]) -> list[PatternInsight]:
    """Identifica erros característicos por bioma."""
    by_biome: dict[str, list[ErrorRecord]] = defaultdict(list)
    for r in records:
        by_biome[r.biome].append(r)

    insights = []
    for biome, biome_records in by_biome.items():
        if len(biome_records) < 5:
            continue
        counter = Counter(r.issue_code for r in biome_records)
        top_issue, top_count = counter.most_common(1)[0]
        pct = top_count / len(biome_records)

        if pct > 0.4:
            insights.append(
                PatternInsight(
                    pattern_type="biome",
                    description=(
                        f"No bioma {biome}, '{top_issue}' representa {pct * 100:.0f}% dos erros"
                    ),
                    evidence={
                        "biome": biome,
                        "top_issue": top_issue,
                        "percentage": round(pct, 3),
                        "count": top_count,
                    },
                    recommendation=f"Material educativo específico para {biome} focado em '{top_issue}'.",
                    confidence=0.85,
                )
            )

    return insights


def analyze_channel_effectiveness(records: list[ErrorRecord]) -> PatternInsight | None:
    """Compara eficácia dos canais de comunicação."""
    by_channel: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "fixed": 0, "days_sum": 0})

    for r in records:
        by_channel[r.channel]["total"] += 1
        if r.fixed:
            by_channel[r.channel]["fixed"] += 1
            by_channel[r.channel]["days_sum"] += r.days_to_fix

    effectiveness = {}
    for channel, data in by_channel.items():
        if data["total"] < 3:
            continue
        fix_rate = data["fixed"] / data["total"]
        avg_days = data["days_sum"] / data["fixed"] if data["fixed"] > 0 else None
        effectiveness[channel] = {
            "fix_rate": round(fix_rate, 3),
            "avg_days_to_fix": round(avg_days, 1) if avg_days else None,
            "sample_size": data["total"],
        }

    if not effectiveness:
        return None

    best_channel = max(effectiveness.keys(), key=lambda c: effectiveness[c]["fix_rate"])

    return PatternInsight(
        pattern_type="channel_effectiveness",
        description=(
            f"Canal '{best_channel}' tem maior taxa de correção "
            f"({effectiveness[best_channel]['fix_rate'] * 100:.0f}%)"
        ),
        evidence={"by_channel": effectiveness},
        recommendation=f"Priorizar '{best_channel}' para comunicações novas.",
        confidence=0.75,
    )


def analyze_translation_effectiveness(records: list[ErrorRecord]) -> PatternInsight | None:
    """Compara casos com vs sem notificação traduzida."""
    translated = [r for r in records if r.translated_notification_used and r.fixed]
    not_translated = [r for r in records if not r.translated_notification_used and r.fixed]

    if len(translated) < 5 or len(not_translated) < 5:
        return None

    avg_translated = sum(r.days_to_fix for r in translated) / len(translated)
    avg_not_translated = sum(r.days_to_fix for r in not_translated) / len(not_translated)

    improvement = (avg_not_translated - avg_translated) / avg_not_translated

    return PatternInsight(
        pattern_type="translation_effectiveness",
        description=(
            f"Notificações traduzidas reduzem tempo de correção em "
            f"{improvement * 100:.0f}% ({avg_not_translated:.1f} → {avg_translated:.1f} dias)"
        ),
        evidence={
            "avg_days_translated": round(avg_translated, 1),
            "avg_days_not_translated": round(avg_not_translated, 1),
            "improvement_percent": round(improvement * 100, 1),
            "sample_translated": len(translated),
            "sample_not_translated": len(not_translated),
        },
        recommendation="Usar tradução em todas as notificações — evidência forte de eficácia.",
        confidence=0.85,
    )


def detect_all_patterns(records: list[ErrorRecord]) -> dict[str, Any]:
    """Executa todas as análises e retorna insights consolidados."""
    insights: list[PatternInsight] = []

    top = analyze_top_errors(records)
    if top:
        insights.append(top)

    insights.extend(analyze_regional_patterns(records))
    insights.extend(analyze_biome_patterns(records))

    channel = analyze_channel_effectiveness(records)
    if channel:
        insights.append(channel)

    translation = analyze_translation_effectiveness(records)
    if translation:
        insights.append(translation)

    return {
        "total_records_analyzed": len(records),
        "insights_count": len(insights),
        "insights": [i.model_dump() for i in insights],
        "generated_at": datetime.now(UTC).isoformat() if records else None,
    }
