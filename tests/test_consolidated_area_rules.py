"""Testes das regras de áreas consolidadas — Art. 61-A."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rules.consolidated_area_rules import check_consolidated_rights  # noqa: E402


def test_consolidated_rights_qualifies_with_reduced_app():
    result = check_consolidated_rights(
        deforestation_date="2005-03-15",
        property_size_modulos=0.8,
        river_width_m=8,
        feature_type="river",
    )

    assert result["qualifies"] is True
    assert result["standard_rule"]["min_width_m"] == 30
    assert result["consolidated_rule"]["min_width_m"] == 5
    assert result["savings_m"] == 25
    assert "Art. 61-A" in result["consolidated_rule"]["legal_ref"]


@pytest.mark.parametrize(
    ("modulos", "expected_width"),
    [
        (0.5, 5),
        (1.5, 8),
        (3.0, 15),
    ],
)
def test_consolidated_width_by_module_bracket(modulos, expected_width):
    result = check_consolidated_rights(
        deforestation_date="2000-01-01",
        property_size_modulos=modulos,
        river_width_m=25,
        feature_type="river",
    )

    assert result["consolidated_rule"]["min_width_m"] == expected_width


def test_consolidated_rights_after_cutoff_uses_standard():
    result = check_consolidated_rights(
        deforestation_date="2010-05-01",
        property_size_modulos=1.0,
        river_width_m=25,
        feature_type="river",
    )

    assert result["qualifies"] is False
    assert result["savings_m"] == 0
    assert (
        result["consolidated_rule"]["min_width_m"]
        == result["standard_rule"]["min_width_m"]
    )


def test_consolidated_spring_feature():
    result = check_consolidated_rights(
        deforestation_date="2003-06-01",
        property_size_modulos=1.0,
        river_width_m=5,
        feature_type="spring",
    )

    assert result["feature_type"] == "spring"
    assert result["consolidated_rule"]["min_width_m"] <= 8


def test_invalid_date_raises():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        check_consolidated_rights("15/03/2005", 1.0, 10, "river")


def test_invalid_feature_type_raises():
    with pytest.raises(ValueError, match="feature_type"):
        check_consolidated_rights("2005-01-01", 1.0, 10, "volcano")
