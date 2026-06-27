"""Testes do motor de regras APP — Art. 4º, I da Lei 12.651/2012."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rules.app_rules import calculate_app_width


@pytest.mark.parametrize(
    ("river_width_m", "expected_app_m", "expected_alinea"),
    [
        (5, 30, "a"),
        (25, 50, "b"),
        (100, 100, "c"),
        (300, 200, "d"),
        (700, 500, "e"),
    ],
)
def test_calculate_app_width_brackets(river_width_m, expected_app_m, expected_alinea):
    result = calculate_app_width(river_width_m)

    assert result["min_width_m"] == expected_app_m
    assert result["issue_code"] == "APP_RIVER_WIDTH"
    assert result["legal_ref"] == f"Art. 4º, I, '{expected_alinea}' da Lei 12.651/2012"
    assert str(expected_app_m) in result["human_explanation"]
    assert len(result["fix_steps"]) >= 3
    assert result["visual_example"]


def test_calculate_app_width_rejects_non_positive():
    with pytest.raises(ValueError, match="maior que zero"):
        calculate_app_width(0)

    with pytest.raises(ValueError, match="maior que zero"):
        calculate_app_width(-5)


@pytest.mark.parametrize(
    ("river_width_m", "expected_app_m"),
    [
        (10, 30),
        (50, 50),
        (200, 100),
        (600, 200),
    ],
)
def test_calculate_app_width_boundary_values(river_width_m, expected_app_m):
    result = calculate_app_width(river_width_m)
    assert result["min_width_m"] == expected_app_m
