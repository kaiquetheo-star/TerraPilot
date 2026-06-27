"""Canais de comunicação com o produtor — WhatsApp e SMS."""

from .message_templates import TEMPLATES, render_template
from .sms_gateway import send_sms
from .whatsapp_bot import handle_whatsapp_webhook, send_whatsapp_message

__all__ = [
    "TEMPLATES",
    "render_template",
    "send_whatsapp_message",
    "handle_whatsapp_webhook",
    "send_sms",
]
