"""Testes de templates de comunicação (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.communication_templates import (  # noqa: E402
    get_follow_up_schedule,
    get_template,
    list_available_templates,
    render_template,
)


def test_list_available_templates_returns_all_issue_codes():
    templates = list_available_templates()

    assert len(templates) == 4
    codes = {t["issue_code"] for t in templates}
    assert codes == {"APP_RIVER_WIDTH", "RL_PERCENTAGE", "CONSOLIDATED_APP", "PRA_PENDING"}
    assert all("legal_reference" in t and "tone" in t for t in templates)


def test_get_template_returns_full_template():
    template = get_template("APP_RIVER_WIDTH")

    assert template is not None
    assert template.issue_code == "APP_RIVER_WIDTH"
    assert len(template.follow_up_schedule) == 4
    assert len(template.button_options) == 3


def test_get_template_unknown_returns_none():
    assert get_template("UNKNOWN_CODE") is None


def test_render_whatsapp_with_full_context():
    rendered = render_template(
        "APP_RIVER_WIDTH",
        {
            "producer_name": "Seu Raimundo",
            "river_name": "Paraguaçu",
            "required_m": 30,
        },
        channel="whatsapp",
    )

    assert rendered is not None
    assert "Seu Raimundo" in rendered
    assert "Paraguaçu" in rendered
    assert "30 metros" in rendered
    assert "{producer_name}" not in rendered


def test_render_with_missing_placeholders_uses_empty_string():
    rendered = render_template(
        "APP_RIVER_WIDTH",
        {"producer_name": "Seu Raimundo"},
        channel="whatsapp",
    )

    assert rendered is not None
    assert "Seu Raimundo" in rendered
    assert "{river_name}" not in rendered
    assert "{required_m}" not in rendered


def test_render_all_channels():
    context = {
        "producer_name": "Maria",
        "river_name": "Tocantins",
        "required_m": 30,
        "difference_ha": 2.3,
        "biome": "Cerrado",
        "required_pct": 20,
        "reduced_m": 15,
        "standard_m": 30,
    }

    whatsapp = render_template("APP_RIVER_WIDTH", context, channel="whatsapp")
    sms = render_template("APP_RIVER_WIDTH", context, channel="sms")
    audio = render_template("APP_RIVER_WIDTH", context, channel="audio")
    email = render_template("APP_RIVER_WIDTH", context, channel="email")

    assert whatsapp and "Maria" in whatsapp
    assert sms and "Tocantins" in sms
    assert audio and "Tocantins" in audio
    assert email and "Maria" in email


def test_render_rl_percentage_channels():
    context = {
        "producer_name": "João",
        "difference_ha": 1.5,
        "biome": "Amazonia",
        "required_pct": 80,
    }

    whatsapp = render_template("RL_PERCENTAGE", context, channel="whatsapp")
    sms = render_template("RL_PERCENTAGE", context, channel="sms")
    audio = render_template("RL_PERCENTAGE", context, channel="audio")

    assert whatsapp and "1.5 hectares" in whatsapp
    assert sms and "1.5ha" in sms
    assert audio and "Amazonia" in audio


def test_render_unknown_issue_or_channel_returns_none():
    assert render_template("UNKNOWN", {}, channel="whatsapp") is None
    assert render_template("APP_RIVER_WIDTH", {}, channel="telegram") is None


def test_get_follow_up_schedule():
    schedule = get_follow_up_schedule("APP_RIVER_WIDTH")

    assert len(schedule) == 4
    assert schedule[0]["days"] == 3
    assert schedule[-1]["days"] == 30


def test_get_follow_up_schedule_unknown_returns_empty():
    assert get_follow_up_schedule("UNKNOWN") == []
