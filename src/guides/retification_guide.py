"""
Guias visuais de retificação por issue_code.

Cada guia tem passos grandes, explicação alternativa para "Não entendi"
e caminhos de ilustrações para pré-carga offline no PWA.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict


class GuideStep(TypedDict):
    step_number: int
    instruction: str
    alternative_explanation: str
    illustration: str


class GuideResult(TypedDict):
    issue_code: str
    title: str
    benefit: str
    total_steps: int
    steps: list[GuideStep]


_DEFAULT_GUIDES_PATH = (
    Path(__file__).resolve().parents[2] / "guides" / "retification_guides.json"
)

_DEFAULT_CONTEXT: dict[str, Any] = {
    "min_width_m": 30,
    "area_ha": 2,
}


@lru_cache(maxsize=1)
def _load_guides(path: str | None = None) -> dict[str, Any]:
    guides_path = Path(path) if path else _DEFAULT_GUIDES_PATH
    with guides_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _format_text(template: str, context: dict[str, Any]) -> str:
    merged = {**_DEFAULT_CONTEXT, **context}
    return template.format(**merged)


def _build_step(raw_step: dict[str, str], step_number: int, context: dict[str, Any]) -> GuideStep:
    return GuideStep(
        step_number=step_number,
        instruction=_format_text(raw_step["instruction"], context),
        alternative_explanation=_format_text(raw_step["alternative_explanation"], context),
        illustration=raw_step["illustration"],
    )


def list_available_guides(*, guides_path: str | None = None) -> list[str]:
    """Retorna os issue_codes com guia disponível."""
    return sorted(_load_guides(guides_path).keys())


def get_guide(
    issue_code: str,
    *,
    guides_path: str | None = None,
    **context: Any,
) -> GuideResult:
    """
    Retorna o guia completo para um tipo de problema.

    Args:
        issue_code: Código do problema (ex.: APP_RIVER_WIDTH).
        guides_path: Caminho opcional para o JSON de guias.
        **context: Variáveis para os templates (ex.: min_width_m=50, area_ha=3).
    """
    guides = _load_guides(guides_path)
    key = issue_code.strip().upper()

    if key not in guides:
        raise KeyError(f"Guia não encontrado para issue_code: {issue_code}")

    entry = guides[key]
    steps = [
        _build_step(raw_step, index, context)
        for index, raw_step in enumerate(entry["steps"], start=1)
    ]

    return GuideResult(
        issue_code=key,
        title=entry["title"],
        benefit=entry["benefit"],
        total_steps=len(steps),
        steps=steps,
    )


def get_alternative_explanation(
    issue_code: str,
    step_number: int,
    *,
    guides_path: str | None = None,
    **context: Any,
) -> str:
    """
    Retorna a explicação alternativa de um passo (botão "Não entendi").
    """
    if step_number < 1:
        raise ValueError("O número do passo deve ser maior ou igual a 1.")

    guide = get_guide(issue_code, guides_path=guides_path, **context)

    if step_number > guide["total_steps"]:
        raise ValueError(
            f"Passo {step_number} inválido. O guia {issue_code} tem "
            f"{guide['total_steps']} passos."
        )

    return guide["steps"][step_number - 1]["alternative_explanation"]


def list_illustration_paths(*, guides_path: str | None = None) -> list[str]:
    """Lista caminhos de ilustrações para pré-carga offline no PWA."""
    guides = _load_guides(guides_path)
    paths: set[str] = set()

    for entry in guides.values():
        for step in entry["steps"]:
            paths.add(step["illustration"])

    return sorted(paths)


def clear_guides_cache() -> None:
    """Limpa o cache dos guias (útil em testes)."""
    _load_guides.cache_clear()
