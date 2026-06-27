"""Testes dos guias de retificação passo-a-passo."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from guides.retification_guide import (  # noqa: E402
    clear_guides_cache,
    get_alternative_explanation,
    get_guide,
    list_available_guides,
    list_illustration_paths,
)
from rules.app_rules import calculate_app_width  # noqa: E402
from translator.notification_translator import translate_notification  # noqa: E402


@pytest.fixture(autouse=True)
def reset_guides_cache():
    clear_guides_cache()
    yield
    clear_guides_cache()


def test_get_guide_app_river_width_with_context():
    guide = get_guide("APP_RIVER_WIDTH", min_width_m=50)

    assert guide["issue_code"] == "APP_RIVER_WIDTH"
    assert guide["total_steps"] == 4
    assert guide["steps"][0]["instruction"].startswith("Abra o SICAR Offline")
    assert "50 metros" in guide["steps"][2]["instruction"]
    assert guide["steps"][0]["illustration"].endswith(".svg")


def test_get_alternative_explanation_step_two():
    text = get_alternative_explanation("APP_RIVER_WIDTH", 2, min_width_m=30)

    assert "zoom" in text.lower() or "rio" in text.lower()


def test_guides_cover_all_translator_issue_codes():
    translator_codes = {
        "RL_PERIMETER_DIVERGENCE",
        "APP_RIVER_WIDTH",
        "APP_OVERLAP",
        "RL_MISSING",
        "GEOMETRY_INVALID",
        "AREA_OUTSIDE_BOUNDARY",
    }
    available = set(list_available_guides())

    assert translator_codes.issubset(available)


def test_integration_translate_notification_to_guide():
    translation = translate_notification(
        "Inconsistência no perímetro da RL - divergência de 2,3ha"
    )
    guide = get_guide(translation["issue_code"], area_ha=2)

    assert guide["total_steps"] == translation["fix_step_count"]
    assert "Reserva Legal" in guide["title"] or "Reserva Legal" in guide["steps"][0]["instruction"]
    assert "crédito rural" in guide["benefit"].lower()


def test_integration_app_rules_to_guide():
    rule = calculate_app_width(25)
    guide = get_guide(rule["issue_code"], min_width_m=rule["min_width_m"])

    assert str(rule["min_width_m"]) in guide["steps"][2]["instruction"]


def test_list_illustration_paths_for_offline_preload():
    paths = list_illustration_paths()

    assert "assets/guides/sicar-open.svg" in paths
    assert all(path.endswith(".svg") for path in paths)


def test_get_guide_unknown_issue_code():
    with pytest.raises(KeyError, match="Guia não encontrado"):
        get_guide("UNKNOWN_CODE")


def test_get_alternative_explanation_invalid_step():
    with pytest.raises(ValueError, match="inválido"):
        get_alternative_explanation("GEOMETRY_INVALID", 99)
