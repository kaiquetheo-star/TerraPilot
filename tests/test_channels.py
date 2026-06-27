"""Testes dos canais WhatsApp e SMS."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from channels.message_templates import render_template  # noqa: E402
from channels.sms_gateway import send_sms  # noqa: E402
from channels.whatsapp_bot import (  # noqa: E402
    handle_whatsapp_webhook,
    send_whatsapp_message,
)


def test_render_notification_template():
    text = render_template(
        "notification_received",
        "whatsapp",
        name="Seu Raimundo",
        summary="RL 2ha menor",
    )

    assert "Seu Raimundo" in text
    assert "Responda 1" in text


def test_send_whatsapp_demo_mode():
    result = send_whatsapp_message(
        "+5511999999999",
        {
            "text": "Teste de mensagem",
            "buttons": [{"id": "1", "text": "Ver como corrigir"}],
        },
    )

    assert result["status"] == "demo"
    assert result["delivery_status"] == "sent"


def test_send_sms_shortens_and_adds_link():
    result = send_sms(
        "+5511888888888",
        "A" * 200,
    )

    assert result["status"] == "demo"
    assert "terrapilot.gov.br" in result["message"]
    assert len(result["message"]) <= 160


def test_whatsapp_webhook_response_1_sends_guide():
    result = handle_whatsapp_webhook(
        {
            "from": "+5511777777777",
            "message": {"text": "1"},
            "issue_code": "RL_PERIMETER_DIVERGENCE",
        }
    )

    assert result["action"] == "send_guide"
    assert result["result"]["status"] in ("demo", "sent")


def test_whatsapp_webhook_response_2_schedules_call():
    result = handle_whatsapp_webhook(
        {
            "from": "+5511777777777",
            "message": {"text": "2"},
        }
    )

    assert result["action"] == "schedule_call"
    assert result["result"]["status"] == "scheduled"
    assert "Luana" in result["result"]["analyst"]


def test_whatsapp_webhook_thumbs_up_marks_understood():
    result = handle_whatsapp_webhook(
        {
            "from": "+5511777777777",
            "message": {"text": "👍"},
        }
    )

    assert result["action"] == "mark_understood"
    assert result["result"]["status"] == "understood"
