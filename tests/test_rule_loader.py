"""Testes do carregador de regras parametrizáveis por país."""

from rules.rule_loader import (
    get_forest_reserve_percentage,
    get_water_buffer_rules,
    load_country_rules,
    resolve_water_buffer_m,
)


def test_load_colombia_rules():
    rules = load_country_rules("CO")
    assert rules["country_code"] == "CO"
    assert rules["country"] == "Colombia"
    assert rules["registry_system"] == "RUP (Registro Único de Predios Rurales)"
    assert rules["status"] == "template_basico"
    assert "protection_areas" in rules
    assert "ecological_regions" in rules


def test_load_brazil_rules_from_index():
    rules = load_country_rules("BR")
    assert rules["country_code"] == "BR"
    assert rules["status"] == "implemented"
    assert "app_rules" in rules
    assert "biomes" in rules


def test_colombia_water_buffer_brackets():
    rules = load_country_rules("CO")
    assert resolve_water_buffer_m(rules, 3) == 30
    assert resolve_water_buffer_m(rules, 7) == 50
    assert resolve_water_buffer_m(rules, 25) == 100
    assert resolve_water_buffer_m(rules, 80) == 200


def test_colombia_forest_reserve_by_region():
    rules = load_country_rules("CO")
    assert get_forest_reserve_percentage(rules, "Amazonia") == 80
    assert get_forest_reserve_percentage(rules, "Andina") == 30
    assert get_forest_reserve_percentage(rules, "Inexistente") is None


def test_brazil_water_buffer_normalized():
    rules = load_country_rules("BR")
    brackets = get_water_buffer_rules(rules)
    assert len(brackets) == 5
    assert resolve_water_buffer_m(rules, 8) == 30
    assert resolve_water_buffer_m(rules, 30) == 50
