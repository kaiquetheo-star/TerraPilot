"""Testes de impacto coletivo."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from collective.collective_impact import calculate_collective_impact  # noqa: E402


def test_collective_impact_raimundo_profile():
    result = calculate_collective_impact("raimundo_itaberaba")

    assert result["producer_name"] == "Seu Raimundo"
    assert "Paraguaçu" in result["watershed_contribution"]
    assert "67%" in result["municipal_goal_progress"]
    assert "480" in result["carbon_sequestered"]
    assert "Itaberaba" in result["narrative"]
    assert len(result["collective_benefits"]) >= 3


def test_collective_impact_unknown_property_uses_defaults():
    result = calculate_collective_impact("unknown_property_xyz")

    assert result["property_id"] == "unknown_property_xyz"
    assert "bacia" in result["watershed_contribution"].lower()
    assert result["municipal_goal_progress"]


def test_collective_impact_empty_id_raises():
    with pytest.raises(ValueError, match="property_id"):
        calculate_collective_impact("")
