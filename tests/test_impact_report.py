"""Testes do relatório de impacto da analista (Luana)."""

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.impact_report import (  # noqa: E402
    AnalystAction,
    calculate_economic_impact,
    calculate_environmental_impact,
    calculate_metrics,
    extract_success_stories,
    generate_impact_report,
    generate_peer_comparison,
)


def _action(
    case_id: str,
    *,
    action_type: str = "notification_sent",
    producer_id: str = "p1",
    producer_name: str = "Seu Raimundo",
    issue_code: str = "APP_RIVER_WIDTH",
    channel: str = "whatsapp",
    timestamp: datetime | None = None,
    days_to_fix: int = 5,
    fixed: bool = True,
    property_size_ha: float = 30.0,
    credit_rural_value_brl: float = 0.0,
) -> AnalystAction:
    return AnalystAction(
        analyst_id="luana-1",
        case_id=case_id,
        producer_id=producer_id,
        producer_name=producer_name,
        action_type=action_type,
        issue_code=issue_code,
        channel=channel,
        timestamp=timestamp or datetime(2026, 1, 10),
        days_to_fix=days_to_fix,
        fixed=fixed,
        property_size_ha=property_size_ha,
        credit_rural_value_brl=credit_rural_value_brl,
    )


def test_calculate_metrics_consolidates_period_data():
    actions = [
        _action("c1", action_type="notification_sent", fixed=True, days_to_fix=4),
        _action("c1", action_type="call_made", fixed=True, days_to_fix=4),
        _action("c2", action_type="notification_sent", producer_id="p2", fixed=False),
        _action("c2", action_type="approved", producer_id="p2", fixed=True, days_to_fix=8),
    ]

    metrics = calculate_metrics(actions)

    assert metrics["cases_analyzed"] == 2
    assert metrics["producers_helped"] == 2
    assert metrics["notifications_sent"] == 2
    assert metrics["calls_made"] == 1
    assert metrics["cases_approved"] == 1
    assert metrics["first_try_success_rate"] == 1.5
    assert metrics["avg_days_to_fix"] == 5.3


def test_calculate_metrics_empty_returns_empty_dict():
    assert calculate_metrics([]) == {}


def test_calculate_environmental_impact_from_approved_cases():
    actions = [
        _action("c1", action_type="approved", property_size_ha=100),
        _action("c2", action_type="approved", property_size_ha=50),
    ]

    impact = calculate_environmental_impact(actions)

    assert impact["total_ha_regularized"] == 150.0
    assert impact["estimated_app_rl_ha"] == 30.0
    assert impact["co2_sequestered_tons_year"] == 450.0
    assert impact["water_protected_m3_year"] == 15000.0
    assert "150 hectares" in impact["narrative"]


def test_calculate_economic_impact_unlocks_credit_and_time_savings():
    actions = [
        _action(
            "c1",
            action_type="approved",
            property_size_ha=20,
            days_to_fix=4,
            credit_rural_value_brl=80000,
        ),
        _action(
            "c2",
            action_type="approved",
            property_size_ha=10,
            days_to_fix=10,
            credit_rural_value_brl=0,
        ),
    ]

    impact = calculate_economic_impact(actions)

    assert impact["credit_rural_unlocked_brl"] == 115000.0
    assert impact["producer_time_saved_days"] == 14
    assert impact["producer_time_value_brl"] == 2100.0
    assert impact["avg_credit_per_producer"] == 57500.0
    assert "115,000" in impact["narrative"]


def test_extract_success_stories_orders_by_fastest_fix():
    actions = [
        _action("c1", action_type="approved", producer_name="Maria", days_to_fix=12),
        _action("c2", action_type="approved", producer_name="João", days_to_fix=3),
        _action("c3", action_type="approved", producer_name="Raimundo", days_to_fix=7),
    ]

    stories = extract_success_stories(actions, top_n=2)

    assert len(stories) == 2
    assert stories[0]["producer_name"] == "João"
    assert stories[0]["days_to_fix"] == 3
    assert "3 dias" in stories[0]["narrative"]


def test_generate_peer_comparison_marks_better_metrics():
    actions = [
        _action("c1", action_type="notification_sent", fixed=True, days_to_fix=5),
        _action("c2", action_type="notification_sent", fixed=True, days_to_fix=7),
    ]
    benchmark = {"first_try_success_rate": 0.5, "avg_days_to_fix": 10.0}

    comparison = generate_peer_comparison(actions, benchmark)

    assert comparison["first_try_success_rate"]["better_than_average"] is True
    assert comparison["avg_days_to_fix"]["better_than_average"] is True
    assert comparison["avg_days_to_fix"]["delta"] == 4.0


def test_generate_impact_report_full_structure():
    actions = [
        _action(
            "c1",
            action_type="notification_sent",
            timestamp=datetime(2026, 1, 5),
            fixed=True,
            days_to_fix=5,
        ),
        _action(
            "c1",
            action_type="approved",
            timestamp=datetime(2026, 1, 20),
            fixed=True,
            days_to_fix=5,
            property_size_ha=40,
            credit_rural_value_brl=50000,
        ),
    ]
    benchmark = {"first_try_success_rate": 0.4, "avg_days_to_fix": 12.0}

    report = generate_impact_report("luana-1", actions, benchmark)

    assert report.analyst_id == "luana-1"
    assert report.period_start == datetime(2026, 1, 5).isoformat()
    assert report.period_end == datetime(2026, 1, 20).isoformat()
    assert report.metrics["cases_analyzed"] == 1
    assert len(report.success_stories) == 1
    assert report.environmental_impact["total_ha_regularized"] == 40.0
    assert report.economic_impact["credit_rural_unlocked_brl"] == 50000.0
    assert report.peer_comparison["first_try_success_rate"]["better_than_average"] is True


def test_generate_impact_report_empty_actions():
    report = generate_impact_report("luana-1", [])

    assert report.analyst_id == "luana-1"
    assert report.period_start == ""
    assert report.metrics == {}
    assert report.success_stories == []
