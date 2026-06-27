"""
Templates de mensagens para WhatsApp, SMS e áudio.

Cada template tem versões por canal, formatadas com variáveis como {name} e {summary}.
"""

from __future__ import annotations

from typing import Any, Literal

Channel = Literal["whatsapp", "sms", "audio"]

TEMPLATES: dict[str, dict[str, str]] = {
    "notification_received": {
        "whatsapp": (
            "Olá {name}! Recebemos uma notificação sobre seu CAR. {summary}. "
            "Responda 1 pra ver como corrigir, 2 pra falar com analista."
        ),
        "sms": "CAR pendente: {summary}. Acesse terrapilot.gov.br ou ligue 0800-XXX-XXXX",
        "audio": (
            "Olá {name}. Recebemos uma notificação sobre seu CAR. {summary}. "
            "Não se preocupe, vamos resolver juntos."
        ),
    },
    "reminder": {
        "whatsapp": (
            "Oi {name}, você ainda não corrigiu a pendência do CAR. Falta pouco! "
            "Responda 1 pra continuar."
        ),
        "sms": "Lembrete: CAR pendente. Acesse terrapilot.gov.br",
        "audio": "Oi {name}, você ainda tem uma pendência no CAR. Falta pouco pra resolver.",
    },
    "success": {
        "whatsapp": (
            "Parabéns {name}! Seu CAR foi aprovado ✅. "
            "Agora você pode acessar crédito rural e outros benefícios."
        ),
        "sms": "CAR aprovado! Acesse beneficios.gov.br",
        "audio": (
            "Parabéns {name}! Seu CAR foi aprovado. "
            "Agora você pode acessar crédito rural e outros benefícios."
        ),
    },
}


def render_template(
    template_key: str,
    channel: Channel,
    **variables: Any,
) -> str:
    """Renderiza um template com as variáveis fornecidas."""
    if template_key not in TEMPLATES:
        raise KeyError(f"Template não encontrado: {template_key}")
    if channel not in TEMPLATES[template_key]:
        raise KeyError(f"Canal '{channel}' não disponível para template '{template_key}'")

    return TEMPLATES[template_key][channel].format(**variables)
