"""
Matriz "Pode / Não Pode" do TerraPilot.

Deixa explícito o papel do sistema em relação ao SICAR, ao analista e ao técnico.
"""

from __future__ import annotations

from typing import Any, TypedDict


class CapabilityItem(TypedDict):
    feature: str
    legal_basis: str


class LimitationItem(TypedDict):
    feature: str
    reason: str


class CapabilityMatrix(TypedDict):
    does: list[CapabilityItem]
    does_not: list[LimitationItem]


CAPABILITY_MATRIX: CapabilityMatrix = {
    "does": [
        {"feature": "Traduz notificações do SICAR", "legal_basis": "Lei 12.651"},
        {"feature": "Valida regras da Lei 12.651", "legal_basis": "Art. 4º, 12, 61-A"},
        {"feature": "Guia passo-a-passo visual", "legal_basis": "—"},
        {"feature": "Explica direitos adquiridos", "legal_basis": "Art. 61-A, 67"},
        {"feature": "Pré-identifica APP/RL", "legal_basis": "Bases abertas"},
        {"feature": "Conecta com PRA", "legal_basis": "Art. 59"},
    ],
    "does_not": [
        {"feature": "Substitui o analista", "reason": "Luana decide (implicações legais)"},
        {"feature": "Analisa imagens de satélite", "reason": "Foco em regras, não visão"},
        {"feature": "Emite CAR oficial", "reason": "SICAR é sistema oficial"},
        {"feature": "Substitui técnico", "reason": "Georreferenciamento requer CREA"},
        {"feature": "Garante aprovação", "reason": "Decisão é do órgão estadual"},
    ],
}


def get_capability_matrix() -> dict[str, Any]:
    """Retorna a matriz completa para API e PWA."""
    return {
        **CAPABILITY_MATRIX,
        "summary": (
            "O TerraPilot orienta o produtor e facilita o trabalho da analista — "
            "mas quem decide, emite o CAR e faz georreferenciamento é o governo e o técnico."
        ),
    }
