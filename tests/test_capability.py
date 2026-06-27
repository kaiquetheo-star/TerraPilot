"""Testes da matriz de capacidades."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from capability.capability_matrix import CAPABILITY_MATRIX, get_capability_matrix  # noqa: E402


def test_capability_matrix_has_does_and_does_not():
    assert len(CAPABILITY_MATRIX["does"]) >= 6
    assert len(CAPABILITY_MATRIX["does_not"]) >= 5


def test_get_capability_matrix_includes_summary():
    matrix = get_capability_matrix()
    assert "summary" in matrix
    assert "Luana" in matrix["summary"] or "analista" in matrix["summary"]


def test_does_not_include_substitutes_analyst():
    features = [item["feature"] for item in CAPABILITY_MATRIX["does_not"]]
    assert "Substitui o analista" in features
