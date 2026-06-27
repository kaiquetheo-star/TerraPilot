"""Testes do guia de primeira declaração."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from first_declaration.first_declaration_guide import guide_first_declaration  # noqa: E402

SAMPLE_LAT = -13.0510
SAMPLE_LON = -55.9140


def test_guide_first_declaration_basic():
    result = guide_first_declaration({"name": "Seu Raimundo", "biome": "Cerrado"})

    assert result["requires_confirmation"] is True
    assert len(result["steps"]) >= 5
    assert result["steps"][1]["title"] == "O que é APP?"
    assert result["steps"][1]["legal_ref"] == "Art. 3º, II"


def test_guide_first_declaration_with_prefill():
    result = guide_first_declaration(
        {
            "name": "Seu Raimundo",
            "municipality": "Lucas do Rio Verde",
            "latitude": SAMPLE_LAT,
            "longitude": SAMPLE_LON,
        }
    )

    assert len(result["pre_identified_features"]) >= 1
    types = {f["type"] for f in result["pre_identified_features"]}
    assert "river" in types or "forest" in types
