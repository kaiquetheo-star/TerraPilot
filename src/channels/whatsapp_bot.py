"""
Envio de mensagens via WhatsApp — ZERO CUSTO, ZERO CARTÃO.

Usa api.whatsapp.com (link direto) que abre o WhatsApp do produtor
com mensagem pré-preenchida. Não precisa de API paga nem aprovação.
"""
import urllib.parse
from typing import Dict, Any


def generate_whatsapp_link(phone: str, message: str) -> str:
    """
    Gera link do WhatsApp Web que abre compartilhamento direto.

    Args:
        phone: Número com DDI+DDD (ex: "5575999999999")
        message: Texto da mensagem

    Returns:
        URL completa para abrir WhatsApp com mensagem pronta

    Example:
        >>> generate_whatsapp_link("5575999999999", "Olá!")
        'https://api.whatsapp.com/send?phone=5575999999999&text=Ol%C3%A1!'
    """
    clean_phone = ''.join(filter(str.isdigit, phone))
    encoded_message = urllib.parse.quote(message, safe='')
    return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"


def send_whatsapp_message(phone: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera link para enviar mensagem via WhatsApp (modo produção).

    Não envia automaticamente — retorna link que o produtor clica
    e abre o WhatsApp dele com mensagem pronta.

    Vantagens:
    - Zero custo (não usa API paga)
    - Zero cartão de crédito
    - Zero aprovação do Facebook
    - Funciona imediatamente

    Args:
        phone: Número do produtor (com DDI+DDD)
        message: Dict com 'text' e opcionalmente 'buttons'

    Returns:
        Dict com link e status
    """
    text = message.get("text", "")

    buttons = message.get("buttons", [])
    if buttons:
        text += "\n\n"
        for btn in buttons:
            text += f"▶ {btn['text']}\n"

    link = generate_whatsapp_link(phone, text)

    return {
        "status": "link_generated",
        "method": "whatsapp_web_api",
        "link": link,
        "phone": phone,
        "message_preview": text[:100] + "..." if len(text) > 100 else text,
        "instructions": "Clique no link para abrir o WhatsApp com a mensagem pronta",
        "cost": "R$ 0,00",
        "requires_credit_card": False,
    }


def send_sms(phone: str, message: str) -> Dict[str, Any]:
    """
    SMS via link mailto: ou sms: (abre app de SMS do dispositivo).

    Alternativa gratuita que não precisa de gateway pago.
    """
    clean_phone = ''.join(filter(str.isdigit, phone))
    sms_link = f"sms:{clean_phone}?body={urllib.parse.quote(message, safe='')}"

    return {
        "status": "link_generated",
        "method": "sms_link",
        "link": sms_link,
        "phone": phone,
        "message": message,
        "instructions": "Clique para abrir app de SMS com mensagem pronta",
        "cost": "R$ 0,00 (operadora cobra SMS normal)",
        "requires_credit_card": False,
    }


def handle_whatsapp_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa respostas do produtor (modo demo).

    Em produção, isso seria um webhook real do WhatsApp Business API.
    Aqui simulamos respostas baseadas no que o produtor digitaria.
    """
    user_response = payload.get("message", "").strip().lower()
    producer_phone = payload.get("from", "")

    if user_response in ["1", "ver como corrigir"]:
        return {
            "action": "send_guide",
            "message": "Ótimo! Aqui está o passo a passo para corrigir...",
            "next_step": "Abrir tela de guia passo-a-passo",
        }
    elif user_response in ["2", "falar com analista"]:
        return {
            "action": "schedule_call",
            "message": "Vamos agendar uma ligação com a analista Luana.",
            "next_step": "Abrir agendamento",
        }
    elif user_response in ["3", "agora não"]:
        return {
            "action": "remind_later",
            "message": "Sem problema! Te lembremos em 3 dias.",
            "next_step": "Agendar lembrete",
        }
    elif user_response in ["👍", "sim", "entendi"]:
        return {
            "action": "mark_understood",
            "message": "Que bom que entendeu! Qualquer dúvida, estamos aqui.",
            "next_step": "Marcar como compreendido",
        }
    else:
        return {
            "action": "unknown",
            "message": "Não entendi. Responda 1, 2 ou 3.",
            "next_step": "Reenviar opções",
        }
