"""Testes do acompanhamento de progresso das retificações."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from progress.progress_service import (  # noqa: E402
    ProgressTracker,
    clear_guide_metadata_cache,
)
from translator.notification_translator import translate_notification  # noqa: E402


@pytest.fixture
def tracker(tmp_path):
    clear_guide_metadata_cache()
    instance = ProgressTracker(db_path=tmp_path / "progress.db")
    yield instance
    clear_guide_metadata_cache()


def test_register_issues_and_progress_bar(tracker):
    registered = tracker.register_issues(
        "raimundo_001",
        ["RL_PERIMETER_DIVERGENCE", "APP_RIVER_WIDTH", "GEOMETRY_INVALID"],
    )

    assert registered == 3
    progress = tracker.get_progress("raimundo_001")

    assert progress["resolved_count"] == 0
    assert progress["total_count"] == 3
    assert progress["percent"] == 0
    assert "3 problema(s)" in progress["bar_message"]
    assert progress["is_complete"] is False


def test_complete_issue_shows_tangible_benefit(tracker):
    tracker.register_issues("raimundo_001", ["RL_PERIMETER_DIVERGENCE"])

    result = tracker.complete_issue("raimundo_001", "RL_PERIMETER_DIVERGENCE")

    assert "crédito rural" in result["benefit_message"].lower()
    assert result["progress"]["resolved_count"] == 1
    assert result["progress"]["is_complete"] is True


def test_progress_bar_falta_pouco_message(tracker):
    issue_codes = [
        "RL_PERIMETER_DIVERGENCE",
        "APP_RIVER_WIDTH",
        "APP_OVERLAP",
        "GEOMETRY_INVALID",
        "RL_MISSING",
        "AREA_OUTSIDE_BOUNDARY",
        "APP_RIVER_WIDTH",
    ]
    tracker.register_issues("raimundo_001", issue_codes[:6])

    tracker.complete_issue("raimundo_001", "RL_PERIMETER_DIVERGENCE")
    tracker.complete_issue("raimundo_001", "APP_RIVER_WIDTH")
    tracker.complete_issue("raimundo_001", "APP_OVERLAP")

    progress = tracker.get_progress("raimundo_001")

    assert progress["resolved_count"] == 3
    assert progress["total_count"] == 6
    assert progress["bar_message"] == "3 de 6 problemas resolvidos — falta pouco!"


def test_history_shows_advancing_retifications(tracker):
    tracker.register_issues(
        "raimundo_001",
        ["GEOMETRY_INVALID", "RL_PERIMETER_DIVERGENCE"],
    )
    tracker.complete_issue("raimundo_001", "GEOMETRY_INVALID")

    history = tracker.get_history("raimundo_001")

    assert len(history) == 2
    resolved = [item for item in history if item["status"] == "resolved"]
    pending = [item for item in history if item["status"] == "pending"]

    assert len(resolved) == 1
    assert len(pending) == 1
    assert resolved[0]["benefit_message"] is not None


def test_register_skips_duplicate_pending(tracker):
    tracker.register_issues("raimundo_001", ["APP_OVERLAP"])
    second = tracker.register_issues("raimundo_001", ["APP_OVERLAP"])

    assert second == 0
    assert tracker.get_progress("raimundo_001")["total_count"] == 1


def test_integration_notification_to_progress(tracker):
    notifications = [
        "Inconsistência no perímetro da RL - divergência de 2,3ha",
        "APP do curso d'água com largura insuficiente na propriedade",
        "Geometria inválida no polígono da área consolidada",
    ]

    issue_codes = []
    for text in notifications:
        translation = translate_notification(text)
        issue_codes.append(translation["issue_code"])

    tracker.register_issues("raimundo_001", issue_codes)
    tracker.complete_issue("raimundo_001", issue_codes[0])

    progress = tracker.get_progress("raimundo_001")

    assert progress["resolved_count"] == 1
    assert progress["total_count"] == 3
    assert progress["pending_issue_codes"] == issue_codes[1:]


def test_register_unknown_issue_code(tracker):
    with pytest.raises(KeyError, match="desconhecido"):
        tracker.register_issues("raimundo_001", ["UNKNOWN_CODE"])


def test_register_empty_producer_id(tracker):
    with pytest.raises(ValueError, match="produtor"):
        tracker.register_issues("", ["APP_OVERLAP"])
