"""
FAQ dinâmico baseado no perfil do produtor.

Conteúdo estático pré-carregável no PWA, com roteiros de áudio curtos
para o produtor ouvir em vez de ler (Speech Synthesis ou áudio gravado).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypedDict

PropertySize = Literal["small", "medium", "large"]
ProductionType = Literal["agriculture", "livestock", "mixed", "extractivism"]


class ProducerProfile(TypedDict, total=False):
    property_size_ha: float
    modulo_fiscal_ha: float
    biome: str
    production_type: ProductionType


class FAQEntry(TypedDict):
    id: str
    question: str
    answer: str
    audio_script: str
    audio_script_file: str
    priority: int


class FAQResult(TypedDict):
    profile_summary: str
    property_size_category: PropertySize | None
    total_entries: int
    entries: list[FAQEntry]


_CONTENT_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "faq_content.json"
_SCRIPTS_ROOT = Path(__file__).resolve().parents[2] / "frontend" / "pwa"


@lru_cache(maxsize=1)
def _load_content(path: str | None = None) -> dict:
    content_path = Path(path) if path else _CONTENT_PATH
    with content_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _property_size_category(
    property_size_ha: float | None,
    modulo_fiscal_ha: float | None,
) -> PropertySize | None:
    if property_size_ha is None or modulo_fiscal_ha is None or modulo_fiscal_ha <= 0:
        return None

    modulos = property_size_ha / modulo_fiscal_ha
    if modulos <= 4:
        return "small"
    if modulos <= 15:
        return "medium"
    return "large"


def _matches_filter(allowed: list[str], value: str | None) -> bool:
    if "*" in allowed:
        return True
    if value is None:
        return False
    return value in allowed


def _load_audio_script(relative_path: str) -> str:
    script_path = _SCRIPTS_ROOT / relative_path
    if not script_path.exists():
        return ""
    return script_path.read_text(encoding="utf-8").strip()


def _profile_summary(profile: ProducerProfile, size_category: PropertySize | None) -> str:
    parts: list[str] = []

    if size_category == "small":
        parts.append("propriedade pequena (até 4 módulos fiscais)")
    elif size_category == "medium":
        parts.append("propriedade média")
    elif size_category == "large":
        parts.append("propriedade grande")

    biome = profile.get("biome")
    if biome:
        parts.append(f"bioma {biome}")

    production = profile.get("production_type")
    production_labels = {
        "agriculture": "agricultura",
        "livestock": "pecuária",
        "mixed": "agricultura e pecuária",
        "extractivism": "extrativismo",
    }
    if production:
        parts.append(f"produção de {production_labels.get(production, production)}")

    if not parts:
        return "perfil geral"

    return ", ".join(parts)


def get_contextual_faq(
    profile: ProducerProfile,
    *,
    content_path: str | None = None,
    limit: int | None = None,
) -> FAQResult:
    """
    Retorna perguntas frequentes filtradas pelo perfil do produtor.

    Args:
        profile: Tamanho (ha + módulo fiscal), bioma e tipo de produção.
        content_path: Caminho opcional para sobrescrever o JSON de conteúdo.
        limit: Limite opcional de entradas (ordenadas por prioridade).
    """
    content = _load_content(content_path)
    size_category = _property_size_category(
        profile.get("property_size_ha"),
        profile.get("modulo_fiscal_ha"),
    )

    biome = profile.get("biome")
    production_type = profile.get("production_type")

    matched: list[FAQEntry] = []

    for raw in content["entries"]:
        filters = raw["filters"]
        if not _matches_filter(filters["biomes"], biome):
            continue
        if not _matches_filter(filters["property_sizes"], size_category):
            continue
        if not _matches_filter(filters["production_types"], production_type):
            continue

        script_file = raw["audio_script_file"]
        matched.append(
            FAQEntry(
                id=raw["id"],
                question=raw["question"],
                answer=raw["answer"],
                audio_script=_load_audio_script(script_file) or raw["answer"],
                audio_script_file=script_file,
                priority=raw["priority"],
            )
        )

    matched.sort(key=lambda item: (item["priority"], item["question"]))

    if limit is not None:
        matched = matched[:limit]

    return FAQResult(
        profile_summary=_profile_summary(profile, size_category),
        property_size_category=size_category,
        total_entries=len(matched),
        entries=matched,
    )


def list_knowledge_asset_paths(*, content_path: str | None = None) -> list[str]:
    """Caminhos para pré-carga offline no PWA (JSON + roteiros de áudio)."""
    content = _load_content(content_path)
    paths = ["data/knowledge/faq_content.json"]

    for entry in content["entries"]:
        script_file = entry["audio_script_file"]
        if script_file not in paths:
            paths.append(script_file)

    return paths


def clear_knowledge_cache() -> None:
    """Limpa cache do conteúdo (útil em testes)."""
    _load_content.cache_clear()
