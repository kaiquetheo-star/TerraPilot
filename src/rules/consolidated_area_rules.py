"""
Regras de áreas consolidadas — Art. 61-A da Lei 12.651/2012.

Verifica direitos adquiridos por ocupação consolidada até 22/07/2008.
As faixas de APP são mais brandas que o Art. 4º padrão, conforme o
tamanho da propriedade em módulos fiscais.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, TypedDict

from .app_rules import calculate_app_width

_CONSOLIDATION_CUTOFF = date(2008, 7, 22)

# (limite_superior_modulos, largura_app_consolidada_m) — Art. 61-A §§ 1-3
_MODULE_APP_WIDTHS: tuple[tuple[float, int], ...] = (
    (1, 5),
    (2, 8),
    (4, 15),
)

_FEATURE_LABELS = {
    "river": "curso d'água",
    "spring": "nascente",
    "lake": "lago ou lagoa natural",
    "vereda": "vereda",
}

FeatureType = Literal["river", "spring", "lake", "vereda"]


class RuleSnapshot(TypedDict):
    min_width_m: int
    legal_ref: str
    human_explanation: str


class ConsolidatedRightsResult(TypedDict):
    issue_code: str
    qualifies: bool
    deforestation_date: str
    cutoff_date: str
    property_size_modulos: float
    feature_type: str
    standard_rule: RuleSnapshot
    consolidated_rule: RuleSnapshot
    savings_m: int
    human_explanation: str
    fix_steps: list[str]
    visual_example: str


def _parse_date(value: str) -> date:
    try:
        year, month, day = (int(part) for part in value.split("-"))
        return date(year, month, day)
    except (ValueError, TypeError) as exc:
        raise ValueError("deforestation_date deve estar no formato YYYY-MM-DD.") from exc


def _consolidated_width_for_modules(property_size_modulos: float) -> int:
    if property_size_modulos <= 0:
        raise ValueError("property_size_modulos deve ser maior que zero.")

    for upper_bound, app_width in _MODULE_APP_WIDTHS:
        if property_size_modulos <= upper_bound:
            return app_width

    return 30


def _feature_adjusted_width(
    base_width: int,
    feature_type: str,
    river_width_m: float,
) -> int:
    if feature_type == "spring":
        return min(base_width, 8)
    if feature_type == "lake":
        return max(base_width, 15)
    if feature_type == "vereda":
        return max(base_width, 15)
    if feature_type == "river":
        standard = calculate_app_width(river_width_m)
        return min(base_width, standard["min_width_m"])
    raise ValueError(
        f"feature_type inválido: {feature_type}. "
        "Use: river, spring, lake ou vereda."
    )


def _module_bracket_label(property_size_modulos: float) -> str:
    if property_size_modulos <= 1:
        return "até 1 módulo fiscal"
    if property_size_modulos <= 2:
        return "de 1 a 2 módulos fiscais"
    if property_size_modulos <= 4:
        return "de 2 a 4 módulos fiscais"
    return "acima de 4 módulos fiscais"


def check_consolidated_rights(
    deforestation_date: str,
    property_size_modulos: float,
    river_width_m: float,
    feature_type: str,
) -> ConsolidatedRightsResult:
    """
    Verifica direitos adquiridos por áreas consolidadas antes de 22/07/2008.

    Retorna comparativo entre regra padrão (Art. 4º) e regra branda (Art. 61-A).
    """
    occupation_date = _parse_date(deforestation_date)
    qualifies = occupation_date <= _CONSOLIDATION_CUTOFF

    if river_width_m <= 0 and feature_type == "river":
        raise ValueError("river_width_m deve ser maior que zero para cursos d'água.")

    feature_label = _FEATURE_LABELS.get(feature_type)
    if not feature_label:
        raise ValueError(
            f"feature_type inválido: {feature_type}. "
            "Use: river, spring, lake ou vereda."
        )

    if feature_type == "river":
        standard = calculate_app_width(river_width_m)
        standard_width = standard["min_width_m"]
        standard_ref = standard["legal_ref"]
        standard_explanation = standard["human_explanation"]
    else:
        standard_width = 30 if feature_type in ("spring", "vereda") else 50
        standard_ref = "Art. 4º da Lei 12.651/2012"
        standard_explanation = (
            f"Para {feature_label}, a regra geral do Código Florestal exige "
            f"faixa de proteção de pelo menos {standard_width} metros."
        )

    base_consolidated = _consolidated_width_for_modules(property_size_modulos)
    consolidated_width = _feature_adjusted_width(base_consolidated, feature_type, river_width_m)
    bracket = _module_bracket_label(property_size_modulos)

    if not qualifies:
        consolidated_width = standard_width
        consolidated_ref = standard_ref
        consolidated_explanation = (
            f"A ocupação em {deforestation_date} é posterior a 22/07/2008. "
            "Não se aplica o Art. 61-A — use a regra padrão do Art. 4º."
        )
        savings = 0
        qualifies_message = (
            "Sua propriedade não se enquadra em área consolidada antes de julho/2008. "
            f"A regra padrão exige {standard_width}m de APP."
        )
    else:
        consolidated_ref = "Art. 61-A, §§ 1 a 7 da Lei 12.651/2012"
        consolidated_explanation = (
            f"Como a ocupação foi consolidada antes de 22/07/2008 e sua propriedade tem "
            f"{bracket}, a lei permite APP de {consolidated_width}m no {feature_label} — "
            f"em vez dos {standard_width}m da regra geral."
        )
        savings = max(0, standard_width - consolidated_width)
        qualifies_message = (
            f"Boa notícia: sua propriedade pode ter direito adquirido (Art. 61-A). "
            f"A faixa de APP no {feature_label} pode ser de {consolidated_width}m "
            f"({savings}m a menos que a regra padrão de {standard_width}m)."
        )

    fix_steps = [
        "Confirme no INCRA ou na escritura a data de ocupação da área.",
        "Abra o SICAR e marque a área como consolidada (se aplicável).",
        (
            f"Desenhe a APP do {feature_label} com {consolidated_width}m "
            f"({'regra Art. 61-A' if qualifies else 'regra padrão Art. 4º'})."
        ),
        "Guarde fotos ou documentos que comprovem a ocupação anterior a 2008.",
        "Sincronize e aguarde análise da OEMA — a Luana confirma o enquadramento.",
    ]

    visual_example = (
        f"Imagine o {feature_label} no centro: de cada lado, uma faixa de "
        f"{consolidated_width} metros sem plantio intenso ou construção nova. "
        f"Isso é o mínimo {'do Art. 61-A' if qualifies else 'do Art. 4º'}."
    )

    return ConsolidatedRightsResult(
        issue_code="CONSOLIDATED_AREA_61A",
        qualifies=qualifies,
        deforestation_date=deforestation_date,
        cutoff_date=_CONSOLIDATION_CUTOFF.isoformat(),
        property_size_modulos=property_size_modulos,
        feature_type=feature_type,
        standard_rule=RuleSnapshot(
            min_width_m=standard_width,
            legal_ref=standard_ref,
            human_explanation=standard_explanation,
        ),
        consolidated_rule=RuleSnapshot(
            min_width_m=consolidated_width,
            legal_ref=consolidated_ref,
            human_explanation=consolidated_explanation,
        ),
        savings_m=savings,
        human_explanation=qualifies_message,
        fix_steps=fix_steps,
        visual_example=visual_example,
    )
