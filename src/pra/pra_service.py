"""
Serviço PRA — Programa de Regularização Ambiental (Art. 59).

Verifica elegibilidade e benefícios para propriedades com passivo ambiental
passível de regularização via PRA estadual.
"""

from __future__ import annotations

from datetime import date
from typing import Any, TypedDict

_CONSOLIDATION_CUTOFF = date(2008, 7, 22)

_PRA_BENEFITS = [
    "Suspensão de multas anteriores a 22/07/2008",
    "Não pode ser autuado durante cumprimento",
    "Acesso a crédito rural durante regularização",
    "Prazos diferenciados de recomposição",
]

_ADHESION_STEPS = [
    "Receba a notificação de passivo ambiental da OEMA",
    "Consulte o TerraPilot para entender o que precisa ser corrigido",
    "Acesse o portal do PRA do seu estado (via SICAR ou OEMA)",
    "Elabore o Termo de Compromisso com apoio técnico (CREA)",
    "Envie a adesão ao PRA e aguarde homologação",
    "Cumpra o cronograma de recomposição dentro do prazo",
]


class PraEligibilityResult(TypedDict):
    eligible: bool
    benefits: list[str]
    legal_ref: str
    adhesion_steps: list[str]
    deadline: str
    human_explanation: str
    cra_note: str | None


def _parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        year, month, day = (int(part) for part in value.split("-"))
        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def check_pra_eligibility(property_data: dict[str, Any]) -> PraEligibilityResult:
    """
    Verifica elegibilidade e benefícios do PRA (Art. 59).

    Args:
        property_data: Dados da propriedade com campos como ``has_environmental_passive``,
            ``notification_received``, ``deforestation_before_2008``, ``municipality``.

    Returns:
        Elegibilidade, benefícios, passos de adesão e prazo legal.
    """
    has_passive = property_data.get("has_environmental_passive", True)
    notification_received = property_data.get("notification_received", False)
    car_status = property_data.get("car_status", "pending")
    deforestation_date = _parse_optional_date(property_data.get("deforestation_date"))

    eligible = has_passive and car_status in ("pending", "in_retification", "notified")

    if notification_received:
        deadline = "180 dias após notificação"
    else:
        deadline = "180 dias após adesão ao PRA"

    if not eligible:
        explanation = (
            "No momento, sua propriedade não apresenta passivo ambiental passível "
            "de regularização via PRA. Continue mantendo o CAR em dia."
        )
        benefits: list[str] = []
    else:
        explanation = (
            "Sua propriedade pode se beneficiar do Programa de Regularização Ambiental. "
            "Ao aderir, você ganha prazos para corrigir, suspensão de multas antigas "
            "e mantém acesso ao crédito rural durante o cumprimento."
        )
        benefits = list(_PRA_BENEFITS)

    cra_note = None
    surplus_vegetation_ha = property_data.get("surplus_vegetation_ha", 0)
    if surplus_vegetation_ha and float(surplus_vegetation_ha) > 0:
        cra_note = (
            f"Você tem {float(surplus_vegetation_ha):g} ha de vegetação além do exigido — "
            "pode emitir Cota de Reserva Ambiental (CRA, Art. 44), um ativo financeiro negociável."
        )

    if deforestation_date and deforestation_date <= _CONSOLIDATION_CUTOFF:
        explanation += (
            " Como a ocupação é anterior a 22/07/2008, combine o PRA com os "
            "direitos adquiridos do Art. 61-A para reduzir a área de recomposição."
        )

    return PraEligibilityResult(
        eligible=eligible,
        benefits=benefits,
        legal_ref="Art. 59 da Lei 12.651/2012",
        adhesion_steps=_ADHESION_STEPS if eligible else [],
        deadline=deadline,
        human_explanation=explanation,
        cra_note=cra_note,
    )
