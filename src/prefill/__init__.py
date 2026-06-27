"""Validador de pré-preenchimento do SICAR."""

from .prefill_validator import (
    get_municipality_info,
    list_prefill_asset_paths,
    suggest_polygons,
    validate_sicar_prefill,
)

__all__ = [
    "validate_sicar_prefill",
    "suggest_polygons",
    "get_municipality_info",
    "list_prefill_asset_paths",
]
