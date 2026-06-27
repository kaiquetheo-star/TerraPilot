"""Testes do validador de pré-preenchimento SICAR."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prefill.prefill_validator import validate_sicar_prefill  # noqa: E402


def test_validate_app_suggestion_correct():
    result = validate_sicar_prefill(
        {
            "type": "app",
            "description": "Área de 2ha próxima ao rio foi marcada como APP",
            "area_ha": 2.0,
            "river_width_m": 25,
            "declared_width_m": 50,
        }
    )

    assert result["validation_status"] == "correct"
    assert result["requires_confirmation"] is True
    assert "Art. 4º" in result["legal_ref"]
    assert "50" in result["human_explanation"]
    assert len(result["fix_steps"]) >= 3


def test_validate_app_suggestion_incorrect():
    result = validate_sicar_prefill(
        {
            "type": "app",
            "river_width_m": 25,
            "declared_width_m": 30,
        }
    )

    assert result["validation_status"] == "incorrect"


def test_validate_app_suggestion_needs_review_without_declared_width():
    result = validate_sicar_prefill(
        {
            "type": "app",
            "river_width_m": 25,
        }
    )

    assert result["validation_status"] == "needs_review"


def test_validate_rl_suggestion():
    result = validate_sicar_prefill(
        {
            "type": "rl",
            "property_area_ha": 100,
            "declared_rl_ha": 70,
            "rl_percent_legal": 80,
            "biome": "Amazônia Legal",
        }
    )

    assert result["validation_status"] == "incorrect"
    assert "Art. 12" in result["legal_ref"]


def test_validate_empty_suggestion_raises():
    with pytest.raises(ValueError, match="não pode ser vazia"):
        validate_sicar_prefill({})


def test_validate_app_missing_river_width_raises():
    with pytest.raises(ValueError, match="river_width_m"):
        validate_sicar_prefill({"type": "app"})
