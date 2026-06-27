"""Motor de regras determinísticas do Código Florestal (Lei 12.651/2012)."""

from rules.app_rules import calculate_app_width
from rules.consolidated_area_rules import check_consolidated_rights
from rules.rl_rules import validate_rl_area
from rules.rule_loader import (
    get_forest_reserve_percentage,
    get_water_buffer_rules,
    load_country_rules,
    resolve_water_buffer_m,
)

__all__ = [
    "calculate_app_width",
    "validate_rl_area",
    "check_consolidated_rights",
    "load_country_rules",
    "get_water_buffer_rules",
    "resolve_water_buffer_m",
    "get_forest_reserve_percentage",
]
