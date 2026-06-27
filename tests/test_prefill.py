"""Testes do pré-preenchimento com bases abertas."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prefill.prefill_validator import (  # noqa: E402
    clear_prefill_cache,
    get_municipality_info,
    list_prefill_asset_paths,
    suggest_polygons,
    validate_sicar_prefill,
)


@pytest.fixture(autouse=True)
def reset_prefill_cache():
    clear_prefill_cache()
    yield
    clear_prefill_cache()


# Coordenada de demonstração: Lucas do Rio Verde, MT
SAMPLE_LAT = -13.0510
SAMPLE_LON = -55.9140


def test_get_municipality_info_by_name():
    info = get_municipality_info("Lucas do Rio Verde")

    assert info["ibge_code"] == "5105903"
    assert info["modulo_fiscal_ha"] == 75
    assert info["biome"] == "Amazônia Legal"
    assert info["rl_percent_legal"] == 80


def test_get_municipality_info_by_ibge_code():
    info = get_municipality_info("5211909")

    assert info["name"] == "Jataí"
    assert info["biome"] == "Cerrado"
    assert info["rl_percent_legal"] == 20


def test_suggest_polygons_near_sample_coordinate():
    result = suggest_polygons(
        "Lucas do Rio Verde",
        SAMPLE_LAT,
        SAMPLE_LON,
        radius_km=3.0,
    )

    assert result["requires_confirmation"] is True
    assert len(result["suggestions"]) >= 2
    assert "conferir" in result["human_message"].lower()
    assert result["municipality"]["name"] == "Lucas do Rio Verde"

    types = {item["suggestion_type"] for item in result["suggestions"]}
    assert "river" in types
    assert "forest" in types or "land_cover" in types


def test_suggest_polygons_sorted_by_distance():
    result = suggest_polygons("Lucas do Rio Verde", SAMPLE_LAT, SAMPLE_LON)

    distances = [item["distance_km"] for item in result["suggestions"]]
    assert distances == sorted(distances)


def test_suggest_polygons_excludes_far_features():
    result = suggest_polygons(
        "Lucas do Rio Verde",
        SAMPLE_LAT,
        SAMPLE_LON,
        radius_km=0.1,
    )

    assert result["requires_confirmation"] is True
    assert len(result["suggestions"]) == 0
    assert "Não encontramos" in result["human_message"]


def test_suggest_polygons_forest_has_area_ha():
    result = suggest_polygons("Lucas do Rio Verde", SAMPLE_LAT, SAMPLE_LON)

    forest = next(
        (item for item in result["suggestions"] if item["suggestion_type"] == "forest"),
        None,
    )
    assert forest is not None
    assert forest["area_ha"] is not None
    assert forest["area_ha"] > 0


def test_suggest_polygons_lists_open_data_sources():
    result = suggest_polygons("Lucas do Rio Verde", SAMPLE_LAT, SAMPLE_LON)

    sources = " ".join(result["data_sources"])
    assert "IBGE" in sources
    assert "MapBiomas" in sources
    assert "SNIRH" in sources
    assert "CAR" in sources


def test_get_municipality_info_unknown():
    with pytest.raises(KeyError, match="Município não encontrado"):
        get_municipality_info("Cidade Inexistente")


def test_suggest_polygons_invalid_coordinates():
    with pytest.raises(ValueError, match="Latitude"):
        suggest_polygons("Lucas do Rio Verde", 95, SAMPLE_LON)

    with pytest.raises(ValueError, match="Longitude"):
        suggest_polygons("Lucas do Rio Verde", SAMPLE_LAT, 200)


def test_list_prefill_asset_paths_for_pwa():
    paths = list_prefill_asset_paths()

    assert "data/prefill/municipalities_ibge.json" in paths
    assert all(path.endswith((".json", ".geojson")) for path in paths)
