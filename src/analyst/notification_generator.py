"""
Gerador de notificações em linguagem simples para o produtor rural.

Converte texto técnico da OEMA em mensagens personalizadas por perfil,
com versões para áudio, SMS e botões do WhatsApp.
"""

from __future__ import annotations

from typing import Any, TypedDict

from translator.notification_translator import translate_notification


class SimpleNotificationResult(TypedDict):
    simple_text: str
    audio_script: str
    sms_version: str
    whatsapp_buttons: list[dict[str, str]]


def _short_summary(simple_text: str, max_len: int = 80) -> str:
    if len(simple_text) <= max_len:
        return simple_text
    return simple_text[: max_len - 3].rsplit(" ", 1)[0] + "..."


def generate_simple_notification(
    technical_notification: str,
    producer_profile: dict[str, Any],
) -> SimpleNotificationResult:
    """
    Converte notificação técnica em linguagem simples para o produtor.

    Args:
        technical_notification: Texto técnico da OEMA.
        producer_profile: Perfil do produtor (name, property_size_ha, etc.).

    Returns:
        Mensagem simples, roteiro de áudio, versão SMS e botões WhatsApp.
    """
    translation = translate_notification(technical_notification)

    name = producer_profile.get("name", "produtor")
    greeting = f"Olá {name}! "
    empathetic_message = "Não se preocupe, vamos resolver isso juntos."

    human_explanation = translation["simple_text"]
    simple_text = f"{greeting}{human_explanation}\n\n{empathetic_message}"
    summary = _short_summary(human_explanation)

    return SimpleNotificationResult(
        simple_text=simple_text,
        audio_script=greeting + human_explanation,
        sms_version=(
            f"CAR pendente: {summary}. "
            "Acesse terrapilot.gov.br ou ligue 0800-XXX-XXXX"
        ),
        whatsapp_buttons=[
            {"id": "1", "text": "Ver como corrigir"},
            {"id": "2", "text": "Falar com analista"},
            {"id": "3", "text": "Agora não"},
        ],
    )
