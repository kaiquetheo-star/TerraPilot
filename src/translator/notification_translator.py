"""
Tradutor determinístico de notificações CAR/OEMA.

Converte linguagem técnica em mensagens empáticas para o produtor rural,
usando apenas o dicionário em dictionaries/technical_to_simple.json — sem IA.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict


class TranslationResult(TypedDict):
    simple_text: str
    issue_code: str | None
    original_text: str
    pattern_id: str | None
    fix_step_count: int | None


_DEFAULT_DICT_PATH = (
    Path(__file__).resolve().parents[2] / "dictionaries" / "technical_to_simple.json"
)


@lru_cache(maxsize=1)
def _load_dictionary(path: str | None = None) -> dict[str, Any]:
    dict_path = Path(path) if path else _DEFAULT_DICT_PATH
    with dict_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _parse_hectares(value: str) -> int:
    normalized = value.strip().replace(",", ".")
    hectares = float(normalized)
    return round(hectares)


def _extract_variables(
    match: re.Match[str],
    extract_rules: dict[str, Any],
) -> dict[str, Any]:
    variables: dict[str, Any] = {}
    for name, rule in extract_rules.items():
        raw = match.group(rule["group"])
        if rule.get("format") == "hectares_round":
            variables[name] = _parse_hectares(raw)
        else:
            variables[name] = raw.strip()
    return variables


def translate_notification(
    technical_text: str,
    *,
    dictionary_path: str | None = None,
) -> TranslationResult:
    """
    Traduz uma notificação técnica da OEMA para linguagem simples.

    Args:
        technical_text: Texto original da notificação (ex.: inconsistência de RL).
        dictionary_path: Caminho opcional para sobrescrever o JSON do dicionário.

    Returns:
        Texto acessível, issue_code quando houver padrão reconhecido,
        e metadados para integração com guias de retificação.
    """
    text = technical_text.strip()
    if not text:
        raise ValueError("O texto da notificação não pode ser vazio.")

    dictionary = _load_dictionary(dictionary_path)
    patterns = dictionary.get("patterns", [])

    for entry in patterns:
        match = re.search(entry["regex"], text)
        if not match:
            continue

        variables = dict(entry.get("defaults", {}))
        if "extract" in entry:
            variables.update(_extract_variables(match, entry["extract"]))

        simple_text = entry["template"].format(**variables)
        steps = variables.get("steps")

        return TranslationResult(
            simple_text=simple_text,
            issue_code=entry.get("issue_code"),
            original_text=text,
            pattern_id=entry.get("id"),
            fix_step_count=int(steps) if steps is not None else None,
        )

    fallback = dictionary["fallback"]["template"]

    return TranslationResult(
        simple_text=fallback,
        issue_code=None,
        original_text=text,
        pattern_id=None,
        fix_step_count=None,
    )


def clear_dictionary_cache() -> None:
    """Limpa o cache do dicionário (útil em testes)."""
    _load_dictionary.cache_clear()
