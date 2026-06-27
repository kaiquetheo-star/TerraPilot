"""Testes da base de conhecimento contextual."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge.knowledge_service import (  # noqa: E402
    clear_knowledge_cache,
    get_contextual_faq,
    list_knowledge_asset_paths,
)
from prefill.prefill_validator import get_municipality_info  # noqa: E402


@pytest.fixture(autouse=True)
def reset_knowledge_cache():
    clear_knowledge_cache()
    yield
    clear_knowledge_cache()


def test_faq_general_profile_includes_universal_entries():
    result = get_contextual_faq({})

    assert result["total_entries"] >= 4
    ids = {entry["id"] for entry in result["entries"]}
    assert "faq_car_oque_e" in ids
    assert "faq_retificacao_medo" in ids


def test_faq_small_property_includes_art_67_entry():
    profile = {
        "property_size_ha": 200,
        "modulo_fiscal_ha": 75,
        "biome": "Amazônia Legal",
        "production_type": "agriculture",
    }
    result = get_contextual_faq(profile)

    assert result["property_size_category"] == "small"
    ids = {entry["id"] for entry in result["entries"]}
    assert "faq_pequena_propriedade" in ids


def test_faq_cerrado_livestock_includes_pasto_entry():
    profile = {
        "property_size_ha": 500,
        "modulo_fiscal_ha": 70,
        "biome": "Cerrado",
        "production_type": "livestock",
    }
    result = get_contextual_faq(profile)

    ids = {entry["id"] for entry in result["entries"]}
    assert "faq_rl_cerrado" in ids
    assert "faq_pasto_cerrado" in ids
    assert "faq_rl_amazonia" not in ids


def test_faq_large_property_includes_grande_propriedade():
    profile = {
        "property_size_ha": 2000,
        "modulo_fiscal_ha": 75,
        "biome": "Amazônia Legal",
        "production_type": "mixed",
    }
    result = get_contextual_faq(profile)

    assert result["property_size_category"] == "large"
    ids = {entry["id"] for entry in result["entries"]}
    assert "faq_grande_propriedade" in ids
    assert "faq_rl_amazonia" in ids


def test_faq_entries_include_audio_script():
    result = get_contextual_faq(
        {"biome": "Cerrado", "production_type": "agriculture"},
        limit=3,
    )

    for entry in result["entries"]:
        assert entry["audio_script"]
        assert entry["audio_script_file"].startswith("assets/knowledge/scripts/")
        assert len(entry["audio_script"]) < 500


def test_faq_profile_summary_describes_producer():
    profile = {
        "property_size_ha": 200,
        "modulo_fiscal_ha": 75,
        "biome": "Cerrado",
        "production_type": "livestock",
    }
    result = get_contextual_faq(profile)

    summary = result["profile_summary"]
    assert "pequena" in summary or "propriedade" in summary
    assert "Cerrado" in summary
    assert "pecuária" in summary


def test_integration_prefill_municipality_profile():
    municipality = get_municipality_info("Jataí")
    profile = {
        "property_size_ha": 280,
        "modulo_fiscal_ha": municipality["modulo_fiscal_ha"],
        "biome": municipality["biome"],
        "production_type": "agriculture",
    }
    result = get_contextual_faq(profile)

    ids = {entry["id"] for entry in result["entries"]}
    assert "faq_rl_cerrado" in ids


def test_list_knowledge_asset_paths_for_offline_preload():
    paths = list_knowledge_asset_paths()

    assert "data/knowledge/faq_content.json" in paths
    assert any(path.endswith(".txt") for path in paths)
