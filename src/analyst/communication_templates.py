"""
Templates de comunicação para a analista Luana.
Resolve: "Luana perde tempo escrevendo notificações similares"
Cada template tem: WhatsApp, SMS, áudio, follow-up schedule.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel


class CommunicationTemplate(BaseModel):
    issue_code: str
    whatsapp_message: str  # até 1024 chars, com {placeholders}
    audio_script: str  # para TTS offline (pyttsx3/gTTS)
    sms_fallback: str  # até 160 chars
    email_subject: str
    email_body: str
    legal_reference: str
    follow_up_schedule: list[dict[str, Any]]
    button_options: list[dict[str, str]]
    tone: str  # "empathetic", "formal", "educational"


TEMPLATES: dict[str, CommunicationTemplate] = {
    "APP_RIVER_WIDTH": CommunicationTemplate(
        issue_code="APP_RIVER_WIDTH",
        whatsapp_message=(
            "Olá {producer_name}! 👋\n\n"
            "Recebemos uma notificação sobre seu CAR.\n\n"
            "📍 *O que aconteceu:*\n"
            "A área próxima ao rio {river_name} precisa de uma faixa livre "
            "de {required_m} metros. Essa faixa protege a água e o solo da sua terra.\n\n"
            "📖 *Por quê:*\n"
            "É o Art. 4º da Lei do CAR (Lei 12.651/2012).\n\n"
            "✅ *Como corrigir:*\n"
            "Responda *1* para ver o passo a passo.\n"
            "Responda *2* para ouvir uma explicação em áudio.\n"
            "Responda *3* para falar com a analista."
        ),
        audio_script=(
            "Olá {producer_name}. Aqui é do órgão ambiental. "
            "Recebemos uma notificação sobre seu CAR. "
            "A área perto do rio {river_name} precisa ter {required_m} metros livres "
            "da margem. Essa faixa protege a água e o solo da sua terra. "
            "Não se preocupe, vamos te ajudar a corrigir. "
            "Responda o número 1 no WhatsApp para ver o passo a passo."
        ),
        sms_fallback=(
            "CAR pendente: faixa do rio {river_name} precisa de {required_m}m. "
            "terrapilot.gov.br ou ligue 0800-XXX-XXXX"
        ),
        email_subject="Seu CAR precisa de um ajuste — vamos te ajudar",
        email_body=(
            "Olá {producer_name},\n\n"
            "Identificamos que a faixa marginal do rio {river_name} no seu CAR "
            "precisa ser ajustada para {required_m} metros, conforme Art. 4º da Lei 12.651/2012.\n\n"
            "Acesse terrapilot.gov.br para ver o passo a passo completo."
        ),
        legal_reference="Art. 4º, I, alíneas a-e da Lei 12.651/2012",
        follow_up_schedule=[
            {"days": 3, "action": "Lembrete WhatsApp se não respondeu"},
            {"days": 7, "action": "Ligação automática ou SMS"},
            {"days": 14, "action": "Encaminhar para visita técnica (se disponível)"},
            {"days": 30, "action": "Alerta de abandono — prioridade máxima"},
        ],
        button_options=[
            {"id": "1", "text": "Ver passo a passo"},
            {"id": "2", "text": "Ouvir áudio"},
            {"id": "3", "text": "Falar com analista"},
        ],
        tone="empathetic",
    ),
    "RL_PERCENTAGE": CommunicationTemplate(
        issue_code="RL_PERCENTAGE",
        whatsapp_message=(
            "Olá {producer_name}! 👋\n\n"
            "📍 *O que aconteceu:*\n"
            "Sua Reserva Legal está {difference_ha} hectares menor que o necessário.\n\n"
            "📖 *Por quê:*\n"
            "No bioma {biome}, a lei exige {required_pct}% da propriedade como RL (Art. 12).\n\n"
            "✅ *Como corrigir:*\n"
            "Responda *1* para ver o passo a passo.\n"
            "Responda *4* para saber sobre PRA (suspensão de multas)."
        ),
        audio_script=(
            "Olá {producer_name}. Sua Reserva Legal está {difference_ha} hectares menor "
            "do que a lei pede. No {biome}, o mínimo é {required_pct}% da propriedade. "
            "Isso é o Art. 12 da Lei do CAR. "
            "Não se preocupe, vamos te ajudar. Responda 1 no WhatsApp."
        ),
        sms_fallback="CAR: RL {difference_ha}ha menor. terrapilot.gov.br",
        email_subject="Sua Reserva Legal precisa de ajuste",
        email_body="",
        legal_reference="Art. 12 da Lei 12.651/2012",
        follow_up_schedule=[
            {"days": 3, "action": "Lembrete WhatsApp"},
            {"days": 7, "action": "SMS"},
            {"days": 14, "action": "Ligação"},
        ],
        button_options=[
            {"id": "1", "text": "Ver passo a passo"},
            {"id": "4", "text": "Saber sobre PRA"},
            {"id": "3", "text": "Falar com analista"},
        ],
        tone="empathetic",
    ),
    "CONSOLIDATED_APP": CommunicationTemplate(
        issue_code="CONSOLIDATED_APP",
        whatsapp_message=(
            "Olá {producer_name}! 👋\n\n"
            "🎁 *Boa notícia!*\n"
            "Você pode ter um *direito adquirido* no seu CAR.\n\n"
            "Se sua área foi usada antes de 22/07/2008, a lei permite "
            "recompor APENAS {reduced_m}m (em vez de {standard_m}m).\n\n"
            "📖 Isso é o Art. 61-A da Lei 12.651.\n\n"
            "Responda *1* para confirmar e aproveitar esse direito."
        ),
        audio_script=(
            "Olá {producer_name}. Tenho uma boa notícia. "
            "Se a área próxima ao rio já era usada antes de julho de 2008, "
            "você só precisa recompor {reduced_m} metros, em vez de {standard_m}. "
            "Isso é um direito seu, garantido pelo Art. 61-A da Lei do CAR. "
            "Responda 1 para confirmar."
        ),
        sms_fallback="Direito adquirido CAR: recompor so {reduced_m}m. terrapilot.gov.br",
        email_subject="Você tem um direito adquirido no CAR",
        email_body="",
        legal_reference="Art. 61-A da Lei 12.651/2012",
        follow_up_schedule=[
            {"days": 5, "action": "Lembrete WhatsApp"},
            {"days": 15, "action": "SMS"},
        ],
        button_options=[
            {"id": "1", "text": "Sim, área antes de 2008"},
            {"id": "2", "text": "Não tenho certeza"},
        ],
        tone="educational",
    ),
    "PRA_PENDING": CommunicationTemplate(
        issue_code="PRA_PENDING",
        whatsapp_message=(
            "Olá {producer_name}! 👋\n\n"
            "📍 *Sobre o PRA (Programa de Regularização Ambiental):*\n\n"
            "Ao aderir ao PRA (Art. 59 da Lei 12.651):\n"
            "✅ Multas antigas são suspensas\n"
            "✅ Você não pode ser autuado durante o cumprimento\n"
            "✅ Acesso a crédito rural mantido\n\n"
            "Responda *1* para iniciar a adesão."
        ),
        audio_script=(
            "Olá {producer_name}. Quero te falar sobre o PRA, "
            "que é o Programa de Regularização Ambiental. "
            "Ao aderir, multas antigas são suspensas e você mantém acesso ao crédito rural. "
            "Responda 1 para começar."
        ),
        sms_fallback="PRA: suspende multas e mantem credito. terrapilot.gov.br",
        email_subject="PRA: seus benefícios",
        email_body="",
        legal_reference="Art. 59 da Lei 12.651/2012",
        follow_up_schedule=[
            {"days": 5, "action": "Lembrete WhatsApp"},
            {"days": 15, "action": "SMS"},
        ],
        button_options=[
            {"id": "1", "text": "Iniciar adesão"},
            {"id": "2", "text": "Saber mais"},
        ],
        tone="educational",
    ),
}


def get_template(issue_code: str) -> CommunicationTemplate | None:
    """Retorna template específico ou None."""
    return TEMPLATES.get(issue_code)


def render_template(
    issue_code: str,
    context: dict[str, Any],
    channel: str = "whatsapp",
) -> str | None:
    """
    Renderiza template com contexto do produtor.
    channel: whatsapp | sms | audio | email
    """
    template = TEMPLATES.get(issue_code)
    if not template:
        return None

    if channel == "whatsapp":
        raw = template.whatsapp_message
    elif channel == "sms":
        raw = template.sms_fallback
    elif channel == "audio":
        raw = template.audio_script
    elif channel == "email":
        raw = template.email_body
    else:
        return None

    placeholders = set(re.findall(r"\{(\w+)\}", raw))
    safe_context = {k: context.get(k, "") for k in placeholders}
    return raw.format(**safe_context)


def get_follow_up_schedule(issue_code: str) -> list[dict[str, Any]]:
    template = TEMPLATES.get(issue_code)
    return template.follow_up_schedule if template else []


def list_available_templates() -> list[dict[str, str]]:
    """Lista todos os templates disponíveis para a Luana."""
    return [
        {
            "issue_code": code,
            "legal_reference": t.legal_reference,
            "tone": t.tone,
        }
        for code, t in TEMPLATES.items()
    ]
