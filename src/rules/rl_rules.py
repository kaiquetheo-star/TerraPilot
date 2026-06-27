"""
Regras de Reserva Legal — Art. 12 da Lei 12.651/2012.

Valida se a área declarada de RL atende ao percentual mínimo legal por bioma.
"""

from __future__ import annotations

from typing import TypedDict


class RlValidationResult(TypedDict):
    issue_code: str
    min_width_m: int | None
    legal_ref: str
    human_explanation: str
    fix_steps: list[str]
    visual_example: str
    required_rl_ha: float
    declared_rl_ha: float
    deficit_ha: float
    is_compliant: bool


def validate_rl_area(
    property_area_ha: float,
    declared_rl_ha: float,
    rl_percent_legal: int,
    *,
    biome: str = "",
) -> RlValidationResult:
    """
    Verifica se a Reserva Legal declarada atende ao percentual mínimo do bioma.

    Args:
        property_area_ha: Área total do imóvel em hectares.
        declared_rl_ha: Área de RL declarada no CAR em hectares.
        rl_percent_legal: Percentual mínimo de RL (ex.: 80 na Amazônia Legal).
        biome: Nome do bioma para mensagens ao produtor.
    """
    if property_area_ha <= 0:
        raise ValueError("A área do imóvel deve ser maior que zero.")
    if declared_rl_ha < 0:
        raise ValueError("A área de RL declarada não pode ser negativa.")
    if not 0 < rl_percent_legal <= 100:
        raise ValueError("O percentual legal de RL deve estar entre 1 e 100.")

    required_rl_ha = round(property_area_ha * (rl_percent_legal / 100), 2)
    deficit_ha = round(max(0.0, required_rl_ha - declared_rl_ha), 2)
    is_compliant = deficit_ha == 0

    legal_ref = "Art. 12 da Lei 12.651/2012"
    biome_label = f" no bioma {biome}" if biome else ""

    if is_compliant:
        human_explanation = (
            f"Sua Reserva Legal de {declared_rl_ha:g} hectares atende ao mínimo de "
            f"{rl_percent_legal}% ({required_rl_ha:g} ha){biome_label}. "
            "Continue mantendo essa área com vegetação nativa."
        )
        fix_steps = [
            "Nenhuma correção necessária na Reserva Legal.",
            "Revise no SICAR se o desenho do polígono coincide com a área no campo.",
            "Salve e sincronize quando estiver satisfeito com o mapa.",
        ]
        visual_example = (
            "A área verde de Reserva Legal no mapa cobre pelo menos "
            f"{required_rl_ha:g} hectares — como a lei exige."
        )
        issue_code = "RL_COMPLIANT"
    else:
        human_explanation = (
            f"A Reserva Legal que você marcou tem {declared_rl_ha:g} hectares, "
            f"mas a lei pede pelo menos {required_rl_ha:g} hectares ({rl_percent_legal}% "
            f"do imóvel){biome_label}. Faltam cerca de {deficit_ha:g} hectares."
        )
        fix_steps = [
            "Abra o SICAR Offline e localize a camada Reserva Legal (RL).",
            "Clique em Editar e amplie a área verde até cobrir os hectares corretos.",
            f"Ajuste o polígono até atingir pelo menos {required_rl_ha:g} hectares.",
            "Salve o desenho e sincronize quando tiver internet.",
        ]
        visual_example = (
            f"Imagine um pedaço da propriedade com mata nativa: faltam "
            f"{deficit_ha:g} hectares para completar a Reserva Legal exigida."
        )
        issue_code = "RL_PERIMETER_DIVERGENCE"

    return RlValidationResult(
        issue_code=issue_code,
        min_width_m=None,
        legal_ref=legal_ref,
        human_explanation=human_explanation,
        fix_steps=fix_steps,
        visual_example=visual_example,
        required_rl_ha=required_rl_ha,
        declared_rl_ha=declared_rl_ha,
        deficit_ha=deficit_ha,
        is_compliant=is_compliant,
    )
