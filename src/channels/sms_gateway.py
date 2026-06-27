"""
Gateway SMS — fallback para produtores sem WhatsApp.

Usa Twilio (trial gratuito) ou modo demo quando credenciais não estão configuradas.
"""

from __future__ import annotations

import os
from typing import Any, TypedDict

PWA_URL = "terrapilot.gov.br"
SMS_MAX_LEN = 160


class SMSResult(TypedDict):
    status: str
    phone: str
    message: str
    provider: str
    message_id: str | None


def _shorten_for_sms(message: str, max_body: int = 140) -> str:
    """Encurta mensagem e adiciona link para o PWA."""
    text = message.strip()
    if len(text) <= max_body:
        return f"{text} {PWA_URL}"

    truncated = text[: max_body - 3].rsplit(" ", 1)[0]
    return f"{truncated}... {PWA_URL}"


def _send_via_twilio(phone: str, message: str) -> SMSResult:
    from twilio.rest import Client

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ.get("TWILIO_SMS_FROM", "")

    client = Client(account_sid, auth_token)
    result = client.messages.create(body=message, from_=from_number, to=phone)

    return SMSResult(
        status="sent",
        phone=phone,
        message=message,
        provider="twilio",
        message_id=result.sid,
    )


def send_sms(phone: str, message: str) -> SMSResult:
    """
    Envia SMS como fallback para quem não tem WhatsApp.

    Encurta a mensagem para o limite de 160 caracteres e adiciona link do PWA.
    """
    if not phone.strip():
        raise ValueError("O número de telefone não pode ser vazio.")
    if not message.strip():
        raise ValueError("A mensagem SMS não pode ser vazia.")

    short_message = _shorten_for_sms(message)

    if len(short_message) > SMS_MAX_LEN:
        short_message = short_message[: SMS_MAX_LEN - 3] + "..."

    twilio_configured = all(
        os.environ.get(key)
        for key in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_SMS_FROM")
    )

    if twilio_configured:
        return _send_via_twilio(phone, short_message)

    return SMSResult(
        status="demo",
        phone=phone,
        message=short_message,
        provider="demo",
        message_id=f"demo-sms-{phone[-4:]}",
    )
