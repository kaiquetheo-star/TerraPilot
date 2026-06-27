"""
Visão unificada de sistemas para a analista Luana.
Resolve: "Luana alterna entre múltiplos sistemas e perde tempo"
Agrega dados de SICAR, histórico de comunicação, notificações, em timeline única.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel


class TimelineEvent(BaseModel):
    timestamp: datetime
    event_type: str  # "car_submitted", "notification_sent", "producer_response", "rectification", "approved"
    source: str  # "sicar", "terrapilot", "analyst", "producer"
    description: str
    details: dict[str, Any] | None = None


class CommunicationRecord(BaseModel):
    timestamp: datetime
    direction: str  # "outbound" or "inbound"
    channel: str  # whatsapp, sms, email, call, visit
    content_summary: str
    translated_notification_used: bool
    response_received: bool


class UnifiedCaseView(BaseModel):
    case_id: str
    producer_name: str
    producer_id: str
    municipality: str
    property_size_ha: float
    biome: str
    sicar_data: dict[str, Any]
    sigef_data: dict[str, Any] | None  # sobreposição com vizinhos
    current_status: str
    pending_issues: list[dict[str, str]]
    timeline: list[TimelineEvent]
    communications: list[CommunicationRecord]
    total_days_since_submission: int
    days_since_last_action: int
    suggested_next_action: str


def _parse_timestamp(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return _ensure_utc(value)
    return _ensure_utc(datetime.fromisoformat(value))


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def build_timeline(
    car_submission_date: datetime,
    notifications: list[dict[str, Any]],
    producer_responses: list[dict[str, Any]],
    analyst_actions: list[dict[str, Any]],
) -> list[TimelineEvent]:
    """Constrói timeline unificada cronológica."""
    events = [
        TimelineEvent(
            timestamp=car_submission_date,
            event_type="car_submitted",
            source="producer",
            description="CAR submetido pelo produtor",
        )
    ]

    for notification in notifications:
        events.append(
            TimelineEvent(
                timestamp=_parse_timestamp(notification["timestamp"]),
                event_type="notification_sent",
                source="analyst",
                description=f"Notificação enviada: {notification['issue_code']}",
                details={
                    "channel": notification.get("channel"),
                    "translated": notification.get("translated", False),
                },
            )
        )

    for response in producer_responses:
        events.append(
            TimelineEvent(
                timestamp=_parse_timestamp(response["timestamp"]),
                event_type="producer_response",
                source="producer",
                description=f"Produtor respondeu via {response['channel']}",
                details={"content": response.get("content")},
            )
        )

    for action in analyst_actions:
        events.append(
            TimelineEvent(
                timestamp=_parse_timestamp(action["timestamp"]),
                event_type=action["type"],
                source="analyst",
                description=action.get("description", ""),
                details=action.get("details"),
            )
        )

    return sorted(events, key=lambda e: e.timestamp)


def build_communications_list(
    sent_messages: list[dict[str, Any]],
    received_messages: list[dict[str, Any]],
) -> list[CommunicationRecord]:
    """Lista unificada de comunicações."""
    records = []

    for message in sent_messages:
        records.append(
            CommunicationRecord(
                timestamp=_parse_timestamp(message["timestamp"]),
                direction="outbound",
                channel=message.get("channel", "unknown"),
                content_summary=message.get("summary", ""),
                translated_notification_used=message.get("translated", False),
                response_received=message.get("response_received", False),
            )
        )

    for message in received_messages:
        records.append(
            CommunicationRecord(
                timestamp=_parse_timestamp(message["timestamp"]),
                direction="inbound",
                channel=message.get("channel", "unknown"),
                content_summary=message.get("content", ""),
                translated_notification_used=False,
                response_received=True,
            )
        )

    return sorted(records, key=lambda r: r.timestamp, reverse=True)


def suggest_next_action(
    view: UnifiedCaseView,
    reference_time: datetime | None = None,
) -> str:
    """Sugere próxima ação com base no estado atual."""
    if not view.pending_issues:
        return "Caso sem pendências — aprovar CAR"

    now = reference_time or datetime.now(UTC)
    days_since = view.days_since_last_action

    if days_since > 30:
        return "Abandono detectado — ligar diretamente ou agendar visita"
    if days_since > 14:
        return "Follow-up urgente — nova notificação via WhatsApp"
    if days_since > 7:
        return "Lembrete via SMS ou WhatsApp"

    recent_responses = [
        communication
        for communication in view.communications
        if communication.direction == "inbound"
        and (now - _ensure_utc(communication.timestamp)).days < 7
    ]
    if recent_responses:
        return "Produtor respondeu — validar correção e decidir"

    return "Aguardar resposta — próxima ação em alguns dias"


def build_unified_view(
    case_id: str,
    producer_name: str,
    producer_id: str,
    municipality: str,
    property_size_ha: float,
    biome: str,
    sicar_data: dict[str, Any],
    sigef_data: dict[str, Any] | None,
    car_submission_date: datetime,
    notifications: list[dict[str, Any]],
    producer_responses: list[dict[str, Any]],
    analyst_actions: list[dict[str, Any]],
    sent_messages: list[dict[str, Any]],
    received_messages: list[dict[str, Any]],
    pending_issues: list[dict[str, str]],
    reference_time: datetime | None = None,
) -> UnifiedCaseView:
    """Monta a visão unificada completa."""
    now = reference_time or datetime.now(UTC)
    submission = _ensure_utc(car_submission_date)

    timeline = build_timeline(
        submission,
        notifications,
        producer_responses,
        analyst_actions,
    )
    communications = build_communications_list(sent_messages, received_messages)

    days_since_submission = (now - submission).days

    if timeline:
        last_event = timeline[-1]
        days_since_last = (now - _ensure_utc(last_event.timestamp)).days
    else:
        days_since_last = days_since_submission

    view = UnifiedCaseView(
        case_id=case_id,
        producer_name=producer_name,
        producer_id=producer_id,
        municipality=municipality,
        property_size_ha=property_size_ha,
        biome=biome,
        sicar_data=sicar_data,
        sigef_data=sigef_data,
        current_status="pending" if pending_issues else "resolved",
        pending_issues=pending_issues,
        timeline=timeline,
        communications=communications,
        total_days_since_submission=days_since_submission,
        days_since_last_action=days_since_last,
        suggested_next_action="",
    )

    view.suggested_next_action = suggest_next_action(view, reference_time=now)
    return view
