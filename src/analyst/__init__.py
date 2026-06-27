"""Módulo da analista (Luana) — notificações, áudio e dashboard."""

from .audio_generator import text_to_speech
from .dashboard_service import (
    get_effectiveness_stats,
    get_stuck_producers,
    get_stuck_producers_summary,
)
from .communication_templates import (
    CommunicationTemplate,
    get_follow_up_schedule,
    get_template,
    list_available_templates,
    render_template,
)
from .decision_support import ComplexCaseInput, DecisionSupport, support_decision
from .error_patterns import ErrorRecord, PatternInsight, detect_all_patterns
from .impact_report import AnalystAction, AnalystImpact, generate_impact_report
from .notification_generator import generate_simple_notification
from .priority_queue import (
    Case,
    PrioritizedCase,
    get_queue_summary,
    prioritize_cases,
)
from .unified_view import UnifiedCaseView, build_unified_view

__all__ = [
    "Case",
    "PrioritizedCase",
    "ErrorRecord",
    "PatternInsight",
    "generate_simple_notification",
    "text_to_speech",
    "get_stuck_producers",
    "get_stuck_producers_summary",
    "get_effectiveness_stats",
    "get_queue_summary",
    "prioritize_cases",
    "detect_all_patterns",
    "CommunicationTemplate",
    "get_template",
    "render_template",
    "list_available_templates",
    "get_follow_up_schedule",
    "AnalystAction",
    "AnalystImpact",
    "generate_impact_report",
    "ComplexCaseInput",
    "DecisionSupport",
    "support_decision",
    "UnifiedCaseView",
    "build_unified_view",
]
