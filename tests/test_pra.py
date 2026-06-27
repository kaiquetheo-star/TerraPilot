"""Testes do serviço PRA — Art. 59."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pra.pra_service import check_pra_eligibility  # noqa: E402


def test_pra_eligible_with_environmental_passive():
    result = check_pra_eligibility(
        {
            "has_environmental_passive": True,
            "notification_received": True,
            "car_status": "notified",
            "deforestation_date": "2005-01-01",
        }
    )

    assert result["eligible"] is True
    assert len(result["benefits"]) == 4
    assert result["legal_ref"] == "Art. 59 da Lei 12.651/2012"
    assert "180 dias" in result["deadline"]
    assert len(result["adhesion_steps"]) >= 5
    assert "Art. 61-A" in result["human_explanation"]


def test_pra_not_eligible_without_passive():
    result = check_pra_eligibility(
        {
            "has_environmental_passive": False,
            "car_status": "approved",
        }
    )

    assert result["eligible"] is False
    assert result["benefits"] == []
    assert result["adhesion_steps"] == []


def test_pra_cra_note_when_surplus_vegetation():
    result = check_pra_eligibility(
        {
            "has_environmental_passive": True,
            "car_status": "pending",
            "surplus_vegetation_ha": 3.5,
        }
    )

    assert result["cra_note"] is not None
    assert "Art. 44" in result["cra_note"]
    assert "3.5" in result["cra_note"]
