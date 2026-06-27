"""Testes da rede de confiança."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from network.trust_network import generate_leader_template, get_regional_progress  # noqa: E402


def test_get_regional_progress_itaberaba():
    result = get_regional_progress("2914703", "Caatinga")

    assert result["municipality"] == "Itaberaba-BA"
    assert result["producers_regularized_this_month"] == 12
    assert "produtor" in result["peer_message"]
    assert len(result["cooperatives_active"]) >= 1


def test_get_regional_progress_unknown_code_uses_defaults():
    result = get_regional_progress("9999999", "Cerrado")

    assert result["producers_regularized_this_month"] >= 1
    assert 0 < result["percentage_complete"] < 1


def test_generate_leader_template_union():
    template = generate_leader_template("union")

    assert template["leader_type"] == "union"
    assert len(template["talking_points"]) >= 3


def test_generate_leader_template_invalid_type():
    import pytest

    with pytest.raises(KeyError, match="leader_type"):
        generate_leader_template("mayor")
