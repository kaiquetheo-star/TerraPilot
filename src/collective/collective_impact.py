"""
Impacto coletivo — mostra como a regularização individual beneficia o coletivo.

Conecta a ação do produtor com metas municipais, bacias hidrográficas e carbono.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "collective" / "impact_profiles.json"

_DEFAULT_WATERSHEDS = {
    "2914703": "Bacia do Rio Paraguaçu",
    "5105903": "Bacia do Alto Paraguai",
    "5211909": "Bacia do Rio Paranaíba",
}


class CollectiveImpactResult(TypedDict):
    property_id: str
    producer_name: str
    municipality: str
    watershed_contribution: str
    municipal_goal_progress: str
    carbon_sequestered: str
    narrative: str
    collective_benefits: list[str]


@lru_cache(maxsize=1)
def _load_profiles() -> dict[str, Any]:
    if not _DATA_PATH.exists():
        return {"properties": {}}
    with _DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def calculate_collective_impact(property_id: str) -> CollectiveImpactResult:
    """
    Mostra impacto da regularização individual no coletivo.

    Usa dados agregados públicos (amostra offline) — sem expor PII de terceiros.
    """
    if not property_id.strip():
        raise ValueError("property_id não pode ser vazio.")

    data = _load_profiles()
    properties = data.get("properties", {})
    profile = properties.get(property_id)

    if not profile:
        profile = {
            "producer_name": "Produtor",
            "municipality": "sua região",
            "municipality_code": "2914703",
            "watershed_ha": 12,
            "municipal_progress_pct": 67,
            "carbon_tons_per_year": 480,
        }

    municipality = profile.get("municipality", "sua região")
    municipality_code = profile.get("municipality_code", "2914703")
    watershed_name = profile.get(
        "watershed_name",
        _DEFAULT_WATERSHEDS.get(municipality_code, "bacia hidrográfica local"),
    )
    watershed_ha = profile.get("watershed_ha", 12)
    progress_pct = profile.get("municipal_progress_pct", 67)
    carbon = profile.get("carbon_tons_per_year", 480)
    name = profile.get("producer_name", "Produtor")

    watershed_contribution = (
        f"Você ajuda a preservar {watershed_ha}ha da {watershed_name}"
    )
    municipal_goal_progress = (
        f"Seu município está em {progress_pct}% da meta de regularização"
    )
    carbon_sequestered = f"~{carbon} toneladas de CO₂/ano"
    narrative = (
        f"{name} regularizando = {municipality} inteira acessando crédito verde"
    )

    collective_benefits = [
        "Proteção de mananciais que abastecem a região",
        "Destravamento de crédito rural coletivo para cooperativas",
        "Redução de pressão fiscalizatória sobre a comunidade",
        "Acesso a programas de pagamento por serviços ambientais (PSA)",
    ]

    return CollectiveImpactResult(
        property_id=property_id,
        producer_name=name,
        municipality=municipality,
        watershed_contribution=watershed_contribution,
        municipal_goal_progress=municipal_goal_progress,
        carbon_sequestered=carbon_sequestered,
        narrative=narrative,
        collective_benefits=collective_benefits,
    )
