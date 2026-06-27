"""Testes de integração dos endpoints do módulo analyst (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

client = TestClient(app)


def test_capability_matrix_endpoint():
    response = client.get("/api/capability/matrix")
    assert response.status_code == 200
    data = response.json()
    assert "does" in data
    assert "does_not" in data
    assert "summary" in data


def test_analyst_prioritize_endpoint():
    response = client.post(
        "/api/analyst/prioritize",
        json=[
            {
                "case_id": "1",
                "producer_name": "Raimundo",
                "producer_id": "p1",
                "municipality": "Sinop",
                "property_size_ha": 30,
                "modulo_fiscal": 2,
                "issue_code": "APP_RIVER_WIDTH",
                "days_since_notification": 20,
                "days_since_last_contact": 10,
                "historical_fix_rate": 0.8,
                "channel_reached": "whatsapp",
                "biome": "Amazonia",
                "has_pending_fines": False,
                "is_small_property": True,
            }
        ],
    )
    assert response.status_code == 200
    data = response.json()
    assert "cases" in data
    assert "summary" in data


def test_analyst_detect_patterns_endpoint():
    response = client.post(
        "/api/analyst/detect-patterns",
        json=[
            {
                "case_id": "c1",
                "issue_code": "APP_RIVER_WIDTH",
                "producer_id": "p1",
                "municipality": "Sinop",
                "biome": "Amazonia",
                "property_size_ha": 30,
                "modulo_fiscal": 2,
                "days_to_fix": 5,
                "fixed": True,
                "fix_attempt_count": 1,
                "channel": "whatsapp",
                "translated_notification_used": True,
            }
        ],
    )
    assert response.status_code == 200
    assert response.json()["total_records_analyzed"] == 1


def test_analyst_impact_report_endpoint():
    response = client.post(
        "/api/analyst/impact-report",
        json={
            "analyst_id": "luana-1",
            "actions": [
                {
                    "analyst_id": "luana-1",
                    "case_id": "c1",
                    "producer_id": "p1",
                    "producer_name": "Raimundo",
                    "action_type": "approved",
                    "issue_code": "APP_RIVER_WIDTH",
                    "channel": "whatsapp",
                    "timestamp": "2026-01-15T10:00:00",
                    "days_to_fix": 5,
                    "fixed": True,
                    "property_size_ha": 30,
                    "credit_rural_value_brl": 50000,
                }
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["analyst_id"] == "luana-1"


def test_analyst_decision_support_endpoint():
    response = client.post(
        "/api/analyst/decision-support",
        json={
            "case_id": "CAR-MT-001",
            "producer_name": "Seu Raimundo",
            "property_size_ha": 30,
            "municipality": "Alta Floresta",
            "state": "MT",
            "biome": "Amazonia",
            "issue_code": "RL_PERCENTAGE",
            "overlaps_uc": True,
            "uc_type": "protecao_integral",
            "overlaps_ti": False,
            "overlaps_quilombo": False,
            "overlaps_border": False,
            "has_pending_fines": True,
            "fine_count": 2,
            "consolidated_before_2008": False,
            "property_size_modulos": 3,
            "legal_issues": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "CAR-MT-001"
    assert len(data["options"]) >= 1


def test_analyst_unified_view_endpoint():
    response = client.post(
        "/api/analyst/unified-view",
        json={
            "case_id": "CAR-MT-001",
            "producer_name": "Seu Raimundo",
            "producer_id": "p1",
            "municipality": "Alta Floresta",
            "property_size_ha": 30,
            "biome": "Amazonia",
            "car_submission_date": "2026-01-01T00:00:00+00:00",
            "pending_issues": [{"issue_code": "APP_RIVER_WIDTH"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "CAR-MT-001"
    assert "timeline" in data
    assert "suggested_next_action" in data


def test_analyst_templates_endpoint():
    response = client.get("/api/analyst/templates")
    assert response.status_code == 200
    assert len(response.json()["templates"]) >= 4
