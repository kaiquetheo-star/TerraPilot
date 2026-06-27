"""
Carregador de regras ambientais parametrizáveis por país.

Suporta schemas distintos: Brasil (aninhado em country_rules.json) e
países com arquivo dedicado (ex.: config/colombia_rules.json).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

_COUNTRY_FILE_MAP: dict[str, str] = {
    "CO": "colombia_rules.json",
}

_INDEX_FILE = "country_rules.json"


class CountryRules(TypedDict, total=False):
    country: str
    country_code: str
    law: str
    registry_system: str
    status: str
    notes: str
    governing_body: str
    ecological_regions: dict[str, dict[str, int]]
    protection_areas: dict[str, Any]
    biomes: dict[str, Any]
    app_rules: dict[str, Any]
    key_articles: list[dict[str, str]]
    adaptações_necessárias: list[str]
    contact_suggested: str


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de regras não encontrado: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _extract_from_index(country_code: str) -> dict[str, Any]:
    index = _load_json(CONFIG_DIR / _INDEX_FILE)
    countries = index.get("countries", {})
    entry = countries.get(country_code.upper())
    if entry is None:
        raise KeyError(f"País '{country_code}' não encontrado em {_INDEX_FILE}")
    return {
        "country_code": country_code.upper(),
        "country": entry.get("name", country_code),
        **entry,
    }


def load_country_rules(country_code: str) -> CountryRules:
    """
    Carrega regras de um país a partir de config/.

    BR e demais países indexados usam config/country_rules.json.
    CO usa config/colombia_rules.json (schema próprio).
    """
    code = country_code.upper()
    dedicated = _COUNTRY_FILE_MAP.get(code)
    if dedicated:
        rules = _load_json(CONFIG_DIR / dedicated)
        rules.setdefault("country_code", code)
        _validate_country_rules(rules)
        return rules  # type: ignore[return-value]

    rules = _extract_from_index(code)
    _validate_country_rules(rules)
    return rules  # type: ignore[return-value]


def _validate_country_rules(rules: dict[str, Any]) -> None:
    required = ("country", "law", "registry_system", "status")
    missing = [key for key in required if not rules.get(key)]
    if missing:
        raise ValueError(f"Regras incompletas — campos ausentes: {', '.join(missing)}")

    has_app = bool(rules.get("app_rules") or rules.get("protection_areas"))
    has_reserve = bool(rules.get("biomes") or rules.get("ecological_regions"))
    if not has_app and not has_reserve:
        raise ValueError(
            "Regras incompletas — defina app_rules/protection_areas ou biomes/ecological_regions"
        )


def get_water_buffer_rules(rules: dict[str, Any]) -> list[dict[str, Any]]:
    """Normaliza faixas de proteção de corpos d'água para qualquer schema."""
    if "protection_areas" in rules:
        return list(rules["protection_areas"].get("water_bodies", []))

    brackets = rules.get("app_rules", {}).get("river_width_m", [])
    normalized: list[dict[str, Any]] = []
    for bracket in brackets:
        normalized.append(
            {
                "min_width_m": bracket.get("min", 0),
                "max_width_m": bracket.get("max"),
                "buffer_zone_m": bracket.get("app_width_m"),
                "legal_ref": bracket.get("legal_ref", ""),
            }
        )
    return normalized


def resolve_water_buffer_m(rules: dict[str, Any], water_width_m: float) -> int:
    """Retorna largura da faixa de proteção para um corpo d'água de water_width_m."""
    if water_width_m <= 0:
        raise ValueError("A largura do corpo d'água deve ser maior que zero.")

    for bracket in get_water_buffer_rules(rules):
        lower = bracket.get("min_width_m", 0)
        upper = bracket.get("max_width_m")
        if upper is None:
            if water_width_m > lower:
                return int(bracket["buffer_zone_m"])
        elif lower < water_width_m <= upper:
            return int(bracket["buffer_zone_m"])
        elif lower == 0 and water_width_m <= upper:
            return int(bracket["buffer_zone_m"])

    brackets = get_water_buffer_rules(rules)
    if brackets:
        return int(brackets[-1]["buffer_zone_m"])
    raise ValueError("Nenhuma faixa de proteção configurada para este país.")


def get_forest_reserve_percentage(rules: dict[str, Any], region: str) -> int | None:
    """Retorna percentual de reserva florestal para bioma/região ecológica."""
    if "ecological_regions" in rules:
        region_data = rules["ecological_regions"].get(region)
        if region_data:
            return int(region_data["forest_reserve_percentage"])
        return None

    biomes = rules.get("biomes", {})
    biome_data = biomes.get(region, {})
    rl_pct = biome_data.get("rl_percentage", {})
    if isinstance(rl_pct, dict):
        if "default" in rl_pct:
            return int(rl_pct["default"])
        values = [int(v) for v in rl_pct.values() if isinstance(v, (int, float))]
        return max(values) if values else None
    if isinstance(rl_pct, (int, float)):
        return int(rl_pct)
    return None
