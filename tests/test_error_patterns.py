"""Testes de detecção de padrões de erro (Luana)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyst.error_patterns import (  # noqa: E402
    ErrorRecord,
    analyze_biome_patterns,
    analyze_channel_effectiveness,
    analyze_regional_patterns,
    analyze_top_errors,
    analyze_translation_effectiveness,
    detect_all_patterns,
)


def _record(
    case_id: str,
    *,
    issue_code: str = "APP_RIVER_WIDTH",
    municipality: str = "Sinop-MT",
    biome: str = "Amazonia",
    fixed: bool = True,
    days_to_fix: int = 5,
    channel: str = "whatsapp",
    translated: bool = True,
) -> ErrorRecord:
    return ErrorRecord(
        case_id=case_id,
        issue_code=issue_code,
        producer_id=f"p-{case_id}",
        municipality=municipality,
        biome=biome,
        property_size_ha=30.0,
        modulo_fiscal=2.0,
        days_to_fix=days_to_fix,
        fixed=fixed,
        fix_attempt_count=1,
        channel=channel,
        translated_notification_used=translated,
    )


def test_analyze_top_errors_identifies_dominant_issue():
    records = [
        _record("1", issue_code="APP_RIVER_WIDTH"),
        _record("2", issue_code="APP_RIVER_WIDTH"),
        _record("3", issue_code="APP_RIVER_WIDTH"),
        _record("4", issue_code="RL_PERCENTAGE"),
    ]
    insight = analyze_top_errors(records)

    assert insight is not None
    assert insight.pattern_type == "top_error"
    assert "APP_RIVER_WIDTH" in insight.description
    assert insight.evidence["top_errors"][0]["issue_code"] == "APP_RIVER_WIDTH"
    assert "Art. 4º" in insight.recommendation


def test_analyze_top_errors_empty_returns_none():
    assert analyze_top_errors([]) is None


def test_analyze_regional_patterns_flags_hotspot_municipality():
    records = []
    for i in range(30):
        records.append(_record(f"hot-{i}", municipality="Alta Floresta-MT"))
    for muni_idx in range(9):
        records.append(_record(f"other-{muni_idx}", municipality=f"Municipio-{muni_idx}"))

    insights = analyze_regional_patterns(records)

    assert len(insights) >= 1
    assert insights[0].pattern_type == "regional"
    assert insights[0].evidence["municipality"] == "Alta Floresta-MT"
    assert insights[0].evidence["multiplier"] > 3


def test_analyze_regional_patterns_requires_minimum_sample():
    records = [_record(str(i)) for i in range(10)]
    assert analyze_regional_patterns(records) == []


def test_analyze_biome_patterns_detects_dominant_error():
    records = [
        _record(str(i), biome="Cerrado", issue_code="RL_PERCENTAGE")
        for i in range(4)
    ] + [
        _record("5", biome="Cerrado", issue_code="APP_RIVER_WIDTH"),
    ]

    insights = analyze_biome_patterns(records)

    assert len(insights) == 1
    assert insights[0].pattern_type == "biome"
    assert insights[0].evidence["biome"] == "Cerrado"
    assert insights[0].evidence["top_issue"] == "RL_PERCENTAGE"
    assert insights[0].evidence["percentage"] == 0.8


def test_analyze_channel_effectiveness_prefers_best_channel():
    records = []
    for i in range(5):
        records.append(_record(f"w-{i}", channel="whatsapp", fixed=True, days_to_fix=3))
    for i in range(5):
        records.append(
            _record(f"e-{i}", channel="email", fixed=(i < 2), days_to_fix=20)
        )

    insight = analyze_channel_effectiveness(records)

    assert insight is not None
    assert insight.pattern_type == "channel_effectiveness"
    assert insight.evidence["by_channel"]["whatsapp"]["fix_rate"] == 1.0
    assert "whatsapp" in insight.description


def test_analyze_translation_effectiveness_measures_improvement():
    translated = [
        _record(f"t-{i}", translated=True, fixed=True, days_to_fix=3)
        for i in range(6)
    ]
    not_translated = [
        _record(f"n-{i}", translated=False, fixed=True, days_to_fix=15)
        for i in range(6)
    ]

    insight = analyze_translation_effectiveness(translated + not_translated)

    assert insight is not None
    assert insight.pattern_type == "translation_effectiveness"
    assert insight.evidence["improvement_percent"] > 0
    assert insight.evidence["avg_days_translated"] < insight.evidence["avg_days_not_translated"]


def test_detect_all_patterns_consolidates_insights():
    records = []
    for i in range(30):
        records.append(
            _record(
                f"hot-{i}",
                municipality="Alta Floresta-MT",
                biome="Amazonia",
                issue_code="APP_RIVER_WIDTH",
                channel="whatsapp",
                translated=True,
                fixed=True,
                days_to_fix=4,
            )
        )
    for muni_idx in range(9):
        records.append(
            _record(
                f"other-{muni_idx}",
                municipality=f"Municipio-{muni_idx}",
                biome="Amazonia",
                issue_code="RL_PERCENTAGE",
                channel="email",
                translated=False,
                fixed=True,
                days_to_fix=12,
            )
        )

    result = detect_all_patterns(records)

    assert result["total_records_analyzed"] == 39
    assert result["insights_count"] >= 3
    assert result["generated_at"] is not None
    pattern_types = {i["pattern_type"] for i in result["insights"]}
    assert "top_error" in pattern_types
    assert "regional" in pattern_types
    assert "biome" in pattern_types
