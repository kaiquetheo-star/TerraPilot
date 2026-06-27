"""
Validador de pré-preenchimento do SICAR.

Valida e explica sugestões do módulo pré-preenchido do SICAR — nunca aplica
automaticamente. Sempre retorna requires_confirmation=True para o produtor
confirmar no mapa.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict

from rules.app_rules import calculate_app_width
from rules.rl_rules import validate_rl_area

from .geo_utils import feature_distance_km, polygon_area_ha


class MunicipalityInfo(TypedDict):
    ibge_code: str
    name: str
    state: str
    modulo_fiscal_ha: float
    biome: str
    rl_percent_legal: int
    source: str


class PolygonSuggestion(TypedDict):
    id: str
    suggestion_type: str
    label: str
    source: str
    geometry: dict[str, Any]
    distance_km: float
    area_ha: float | None
    confidence: str


class PrefillResult(TypedDict):
    municipality: MunicipalityInfo
    latitude: float
    longitude: float
    radius_km: float
    suggestions: list[PolygonSuggestion]
    requires_confirmation: bool
    human_message: str
    data_sources: list[str]


class SicarValidationResult(TypedDict):
    sicar_suggested: str
    validation_status: Literal["correct", "incorrect", "needs_review"]
    legal_ref: str
    human_explanation: str
    visual_example: str
    requires_confirmation: bool
    fix_steps: list[str]


_DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "prefill"

_SOURCE_LABELS = {
    "hydrography": "SNIRH / ANA — Hidrografia",
    "land_cover": "MapBiomas — Uso e cobertura do solo",
    "car_reference": "Portal de Consulta Pública do CAR",
}


@lru_cache(maxsize=1)
def _load_municipalities(path: str | None = None) -> dict[str, Any]:
    file_path = Path(path) if path else _DATA_ROOT / "municipalities_ibge.json"
    with file_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_geojson(filename: str) -> dict[str, Any]:
    file_path = _DATA_ROOT / "samples" / filename
    with file_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_municipality_key(municipality: str) -> str:
    return municipality.strip().lower()


def _find_municipality(
    municipality: str,
    municipalities: dict[str, Any],
) -> tuple[str, dict[str, Any]] | None:
    query = _normalize_municipality_key(municipality)

    for code, info in municipalities.items():
        if query == code or query == info["name"].lower():
            return code, info

    for code, info in municipalities.items():
        if query in info["name"].lower():
            return code, info

    return None


def get_municipality_info(
    municipality: str,
    *,
    municipalities_path: str | None = None,
) -> MunicipalityInfo:
    """Retorna dados IBGE do município (módulo fiscal, bioma, RL legal)."""
    municipalities = _load_municipalities(municipalities_path)
    match = _find_municipality(municipality, municipalities)

    if not match:
        raise KeyError(f"Município não encontrado na base local: {municipality}")

    _, info = match
    return MunicipalityInfo(**info)


def _confidence_from_distance(distance_km: float, radius_km: float) -> str:
    if distance_km <= radius_km * 0.4:
        return "high"
    if distance_km <= radius_km * 0.8:
        return "medium"
    return "low"


def _build_suggestion(
    feature: dict[str, Any],
    source_key: str,
    lat: float,
    lon: float,
    radius_km: float,
) -> PolygonSuggestion | None:
    distance = feature_distance_km(feature, lat, lon)
    if distance > radius_km:
        return None

    props = feature["properties"]
    geometry = feature["geometry"]
    area_ha = None

    if geometry["type"] == "Polygon":
        area_ha = polygon_area_ha(geometry["coordinates"])

    return PolygonSuggestion(
        id=props["id"],
        suggestion_type=props["type"],
        label=props["label"],
        source=_SOURCE_LABELS[source_key],
        geometry=geometry,
        distance_km=round(distance, 2),
        area_ha=area_ha,
        confidence=_confidence_from_distance(distance, radius_km),
    )


def _validate_app_suggestion(suggestion: dict[str, Any]) -> SicarValidationResult:
    area_ha = suggestion.get("area_ha", 0)
    river_width_m = float(suggestion.get("river_width_m", 0))
    declared_width_m = suggestion.get("declared_width_m")

    if river_width_m <= 0:
        raise ValueError("river_width_m é obrigatório para validar sugestões de APP.")

    app_result = calculate_app_width(river_width_m)
    required_width_m = app_result["min_width_m"]

    sicar_text = suggestion.get(
        "description",
        f"Área de {area_ha:g}ha próxima ao rio foi marcada como APP",
    )

    if declared_width_m is not None:
        declared = float(declared_width_m)
        if declared >= required_width_m:
            status: Literal["correct", "incorrect", "needs_review"] = "correct"
            explanation = (
                f"O SICAR sugeriu que essa área é APP porque tem um rio de "
                f"{river_width_m:g}m passando. Pela lei, você precisa deixar "
                f"{required_width_m}m livres das margens — e a sugestão do SICAR "
                f"({declared:g}m) atende esse mínimo."
            )
        else:
            status = "incorrect"
            explanation = (
                f"O SICAR marcou uma faixa de {declared:g}m, mas o rio tem "
                f"{river_width_m:g}m de largura. Pela lei, você precisa deixar "
                f"pelo menos {required_width_m}m livres de cada margem."
            )
    else:
        status = "needs_review"
        explanation = (
            f"O SICAR sugeriu que essa área é APP porque tem um rio de "
            f"{river_width_m:g}m passando. Pela lei, você precisa deixar "
            f"{required_width_m}m livres das margens. Confira no mapa se a faixa "
            f"marcada cobre essa distância dos dois lados."
        )

    visual_example = (
        f"Imagine o rio no meio. Dos dois lados, conte {required_width_m} passos "
        f"grandes ({required_width_m}m). Essa faixa você não pode mexer."
    )

    return SicarValidationResult(
        sicar_suggested=sicar_text,
        validation_status=status,
        legal_ref=app_result["legal_ref"],
        human_explanation=explanation,
        visual_example=visual_example,
        requires_confirmation=True,
        fix_steps=[
            "Abra o SICAR",
            "Clique em 'Visualizar sugestões'",
            "Confirme que a área marcada está correta",
            "Se precisar ajustar, clique em 'Editar'",
        ],
    )


def _validate_rl_suggestion(suggestion: dict[str, Any]) -> SicarValidationResult:
    property_area_ha = float(suggestion.get("property_area_ha", 0))
    declared_rl_ha = float(suggestion.get("declared_rl_ha", 0))
    rl_percent = int(suggestion.get("rl_percent_legal", 20))
    biome = suggestion.get("biome", "")

    if property_area_ha <= 0:
        raise ValueError("property_area_ha é obrigatório para validar sugestões de RL.")

    rl_result = validate_rl_area(property_area_ha, declared_rl_ha, rl_percent, biome=biome)

    sicar_text = suggestion.get(
        "description",
        f"Área de Reserva Legal de {declared_rl_ha:g}ha sugerida pelo SICAR",
    )

    if rl_result["is_compliant"]:
        status: Literal["correct", "incorrect", "needs_review"] = "correct"
    elif rl_result["deficit_ha"] > 0:
        status = "incorrect"
    else:
        status = "needs_review"

    return SicarValidationResult(
        sicar_suggested=sicar_text,
        validation_status=status,
        legal_ref=rl_result["legal_ref"],
        human_explanation=rl_result["human_explanation"],
        visual_example=rl_result["visual_example"],
        requires_confirmation=True,
        fix_steps=rl_result["fix_steps"],
    )


def validate_sicar_prefill(sicar_suggestion: dict[str, Any]) -> SicarValidationResult:
    """
    Valida e explica sugestões do módulo pré-preenchido do SICAR.

    Args:
        sicar_suggestion: Sugestão do SICAR com campos como ``type`` (app, rl),
            ``description``, ``area_ha``, ``river_width_m``, etc.

    Returns:
        Explicação em linguagem simples, referência legal e confirmação obrigatória.
    """
    if not sicar_suggestion:
        raise ValueError("A sugestão do SICAR não pode ser vazia.")

    suggestion_type = sicar_suggestion.get("type", "app").lower()

    if suggestion_type == "app":
        return _validate_app_suggestion(sicar_suggestion)
    if suggestion_type in ("rl", "reserva_legal"):
        return _validate_rl_suggestion(sicar_suggestion)

    description = sicar_suggestion.get("description", "Sugestão do SICAR")
    return SicarValidationResult(
        sicar_suggested=description,
        validation_status="needs_review",
        legal_ref="Lei 12.651/2012",
        human_explanation=(
            "O SICAR sugeriu uma alteração na sua propriedade. "
            "Confira no mapa se a área marcada corresponde ao que você vê no terreno."
        ),
        visual_example=(
            "Abra o mapa no SICAR e compare a área colorida com o que você conhece "
            "da sua propriedade — rios, matas e pastos."
        ),
        requires_confirmation=True,
        fix_steps=[
            "Abra o SICAR",
            "Clique em 'Visualizar sugestões'",
            "Confirme que a área marcada está correta",
            "Se precisar ajustar, clique em 'Editar'",
        ],
    )


def suggest_polygons(
    municipality: str,
    latitude: float,
    longitude: float,
    *,
    radius_km: float = 2.0,
    municipalities_path: str | None = None,
) -> PrefillResult:
    """
    Busca polígonos públicos próximos para comparação com sugestões do SICAR.

    Mantido para compatibilidade — o fluxo principal é validate_sicar_prefill.
    """
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude deve estar entre -90 e 90.")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude deve estar entre -180 e 180.")
    if radius_km <= 0:
        raise ValueError("O raio de busca deve ser maior que zero.")

    municipality_info = get_municipality_info(
        municipality,
        municipalities_path=municipalities_path,
    )

    datasets = {
        "hydrography": _load_geojson("hydrography.geojson"),
        "land_cover": _load_geojson("land_cover.geojson"),
        "car_reference": _load_geojson("car_reference.geojson"),
    }

    suggestions: list[PolygonSuggestion] = []

    for source_key, collection in datasets.items():
        for feature in collection["features"]:
            suggestion = _build_suggestion(
                feature,
                source_key,
                latitude,
                longitude,
                radius_km,
            )
            if suggestion:
                suggestions.append(suggestion)

    suggestions.sort(key=lambda item: item["distance_km"])

    count = len(suggestions)
    if count == 0:
        human_message = (
            "Não encontramos áreas mapeadas bem perto dessa coordenada na base "
            "offline. Compare com o que o SICAR sugeriu e desenhe manualmente se precisar."
        )
    else:
        human_message = (
            f"Encontramos {count} área(s) perto de você com dados públicos. "
            "Use para conferir se a sugestão do SICAR bate com o que os mapas mostram."
        )

    data_sources = sorted({collection["metadata"]["source"] for collection in datasets.values()})
    data_sources.insert(0, municipality_info["source"])

    return PrefillResult(
        municipality=municipality_info,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        suggestions=suggestions,
        requires_confirmation=True,
        human_message=human_message,
        data_sources=data_sources,
    )


def list_prefill_asset_paths() -> list[str]:
    """Caminhos relativos dos dados para pré-carga offline no PWA."""
    return [
        "data/prefill/municipalities_ibge.json",
        "data/prefill/samples/hydrography.geojson",
        "data/prefill/samples/land_cover.geojson",
        "data/prefill/samples/car_reference.geojson",
    ]


def clear_prefill_cache() -> None:
    """Limpa cache de municípios (útil em testes)."""
    _load_municipalities.cache_clear()
