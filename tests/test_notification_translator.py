"""Testes do tradutor de notificações OEMA → linguagem simples."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from translator.notification_translator import (  # noqa: E402
    clear_dictionary_cache,
    translate_notification,
)


@pytest.fixture(autouse=True)
def reset_dictionary_cache():
    clear_dictionary_cache()
    yield
    clear_dictionary_cache()


def test_translate_rl_perimeter_divergence_example():
    technical = "Inconsistência no perímetro da RL - divergência de 2,3ha"
    result = translate_notification(technical)

    assert result["simple_text"] == (
        "A área de Reserva Legal que você marcou está 2 hectares menor "
        "que o necessário. Vamos corrigir isso juntos em 3 passos."
    )
    assert result["issue_code"] == "RL_PERIMETER_DIVERGENCE"
    assert result["pattern_id"] == "rl_perimeter_divergence"
    assert result["fix_step_count"] == 3
    assert result["original_text"] == technical


@pytest.mark.parametrize(
    ("technical", "expected_fragment", "issue_code"),
    [
        (
            "APP do curso d'água com largura insuficiente na propriedade",
            "faixa de proteção perto do rio",
            "APP_RIVER_WIDTH",
        ),
        (
            "Sobreposição detectada com APP de preservação permanente",
            "perto de rio ou nascente",
            "APP_OVERLAP",
        ),
        (
            "Ausência de área de Reserva Legal declarada",
            "Falta marcar a Reserva Legal",
            "RL_MISSING",
        ),
        (
            "Geometria inválida no polígono da área consolidada",
            "desenho de uma área no seu mapa",
            "GEOMETRY_INVALID",
        ),
    ],
)
def test_translate_known_patterns(technical, expected_fragment, issue_code):
    result = translate_notification(technical)

    assert expected_fragment.lower() in result["simple_text"].lower()
    assert result["issue_code"] == issue_code
    assert result["pattern_id"] is not None


def test_translate_unknown_notification_uses_fallback():
    technical = "Pendência cadastral código XYZ-999 sem descrição padrão"
    result = translate_notification(technical)

    assert "Não se preocupe" in result["simple_text"]
    assert result["issue_code"] is None
    assert result["pattern_id"] is None


def test_translate_rejects_empty_text():
    with pytest.raises(ValueError, match="não pode ser vazio"):
        translate_notification("   ")


def test_translate_rl_divergence_with_dot_decimal():
    technical = "Inconsistencia no perimetro da RL - divergencia de 1.7ha"
    result = translate_notification(technical)

    assert "2 hectares menor" in result["simple_text"]
    assert result["issue_code"] == "RL_PERIMETER_DIVERGENCE"
