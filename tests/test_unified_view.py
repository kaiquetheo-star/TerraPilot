"""Testes da visão unificada de sistemas (Luana)."""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.unified_view import (  # noqa: E402
    CommunicationRecord,
    UnifiedCaseView,
    build_communications_list,
    build_timeline,
    build_unified_view,
    suggest_next_action,
)


def _now() -> datetime:
    return datetime(2026, 6, 26, 12, 0, 0, tzinfo=UTC)


def test_build_timeline_orders_events_chronologically():
    submission = datetime(2026, 1, 1, tzinfo=UTC)
    notifications = [
        {
            "timestamp": datetime(2026, 1, 5, tzinfo=UTC),
            "issue_code": "APP_RIVER_WIDTH",
            "channel": "whatsapp",
            "translated": True,
        }
    ]
    producer_responses = [
        {
            "timestamp": datetime(2026, 1, 10, tzinfo=UTC),
            "channel": "whatsapp",
            "content": "Entendi, vou corrigir",
        }
    ]
    analyst_actions = [
        {
            "timestamp": datetime(2026, 1, 15, tzinfo=UTC),
            "type": "approved",
            "description": "CAR aprovado após retificação",
        }
    ]

    timeline = build_timeline(submission, notifications, producer_responses, analyst_actions)

    assert len(timeline) == 4
    assert timeline[0].event_type == "car_submitted"
    assert timeline[1].event_type == "notification_sent"
    assert timeline[2].event_type == "producer_response"
    assert timeline[3].event_type == "approved"
    assert timeline[1].details["channel"] == "whatsapp"


def test_build_timeline_accepts_iso_timestamp_strings():
    timeline = build_timeline(
        datetime(2026, 1, 1, tzinfo=UTC),
        [{"timestamp": "2026-01-05T10:00:00+00:00", "issue_code": "RL_PERCENTAGE"}],
        [],
        [],
    )

    assert len(timeline) == 2
    assert timeline[1].description == "Notificação enviada: RL_PERCENTAGE"


def test_build_communications_list_merges_and_sorts_by_recent():
    sent = [
        {
            "timestamp": datetime(2026, 1, 5, tzinfo=UTC),
            "channel": "whatsapp",
            "summary": "Notificação APP rio",
            "translated": True,
            "response_received": True,
        }
    ]
    received = [
        {
            "timestamp": datetime(2026, 1, 10, tzinfo=UTC),
            "channel": "whatsapp",
            "content": "Vou corrigir amanhã",
        }
    ]

    communications = build_communications_list(sent, received)

    assert len(communications) == 2
    assert communications[0].direction == "inbound"
    assert communications[1].direction == "outbound"
    assert communications[1].translated_notification_used is True


def test_suggest_next_action_no_pending_issues():
    view = UnifiedCaseView(
        case_id="c1",
        producer_name="Raimundo",
        producer_id="p1",
        municipality="Sinop",
        property_size_ha=30,
        biome="Amazonia",
        sicar_data={},
        sigef_data=None,
        current_status="resolved",
        pending_issues=[],
        timeline=[],
        communications=[],
        total_days_since_submission=10,
        days_since_last_action=2,
        suggested_next_action="",
    )

    assert suggest_next_action(view, reference_time=_now()) == "Caso sem pendências — aprovar CAR"


def test_suggest_next_action_abandonment_after_30_days():
    view = UnifiedCaseView(
        case_id="c1",
        producer_name="Raimundo",
        producer_id="p1",
        municipality="Sinop",
        property_size_ha=30,
        biome="Amazonia",
        sicar_data={},
        sigef_data=None,
        current_status="pending",
        pending_issues=[{"issue_code": "APP_RIVER_WIDTH"}],
        timeline=[],
        communications=[],
        total_days_since_submission=60,
        days_since_last_action=35,
        suggested_next_action="",
    )

    assert suggest_next_action(view, reference_time=_now()) == (
        "Abandono detectado — ligar diretamente ou agendar visita"
    )


def test_suggest_next_action_recent_producer_response():
    view = UnifiedCaseView(
        case_id="c1",
        producer_name="Raimundo",
        producer_id="p1",
        municipality="Sinop",
        property_size_ha=30,
        biome="Amazonia",
        sicar_data={},
        sigef_data=None,
        current_status="pending",
        pending_issues=[{"issue_code": "APP_RIVER_WIDTH"}],
        timeline=[],
        communications=[
            CommunicationRecord(
                timestamp=_now() - timedelta(days=2),
                direction="inbound",
                channel="whatsapp",
                content_summary="Corrigi no SICAR",
                translated_notification_used=False,
                response_received=True,
            )
        ],
        total_days_since_submission=10,
        days_since_last_action=2,
        suggested_next_action="",
    )

    assert suggest_next_action(view, reference_time=_now()) == (
        "Produtor respondeu — validar correção e decidir"
    )


def test_build_unified_view_full_structure():
    now = _now()
    submission = now - timedelta(days=45)

    view = build_unified_view(
        case_id="CAR-MT-001",
        producer_name="Seu Raimundo",
        producer_id="p1",
        municipality="Alta Floresta",
        property_size_ha=30,
        biome="Amazonia",
        sicar_data={"status": "pending", "car_number": "MT-123"},
        sigef_data={"overlap_neighbors": 1},
        car_submission_date=submission,
        notifications=[
            {
                "timestamp": submission + timedelta(days=5),
                "issue_code": "APP_RIVER_WIDTH",
                "channel": "whatsapp",
                "translated": True,
            }
        ],
        producer_responses=[
            {
                "timestamp": submission + timedelta(days=20),
                "channel": "whatsapp",
                "content": "Estou corrigindo",
            }
        ],
        analyst_actions=[],
        sent_messages=[
            {
                "timestamp": submission + timedelta(days=5),
                "channel": "whatsapp",
                "summary": "APP rio",
                "translated": True,
            }
        ],
        received_messages=[
            {
                "timestamp": submission + timedelta(days=20),
                "channel": "whatsapp",
                "content": "Estou corrigindo",
            }
        ],
        pending_issues=[{"issue_code": "APP_RIVER_WIDTH", "severity": "high"}],
        reference_time=now,
    )

    assert view.case_id == "CAR-MT-001"
    assert view.current_status == "pending"
    assert view.sicar_data["car_number"] == "MT-123"
    assert len(view.timeline) == 3
    assert len(view.communications) == 2
    assert view.total_days_since_submission == 45
    assert view.days_since_last_action == 25
    assert "Follow-up urgente" in view.suggested_next_action
