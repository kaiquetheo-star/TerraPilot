"""
API REST do TerraPilot — módulos core + analista + canais + exportação.

Expõe regras, tradução, guias, validador de pré-preenchimento, progresso,
conhecimento, módulo analista, WhatsApp/SMS e export.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from export.exporter import (  # noqa: E402
    export_progress_report,
    export_to_geojson,
    export_to_sicar_xml,
)
from guides.retification_guide import get_guide  # noqa: E402
from knowledge.knowledge_service import ProducerProfile, get_contextual_faq  # noqa: E402
from channels.sms_gateway import send_sms as send_sms_message  # noqa: E402
from channels.whatsapp_bot import (  # noqa: E402
    handle_whatsapp_webhook,
    send_whatsapp_message,
)
from analyst.audio_generator import text_to_speech  # noqa: E402
from analyst.dashboard_service import (  # noqa: E402
    get_effectiveness_stats,
    get_stuck_producers as fetch_stuck_producers,
    get_stuck_producers_summary,
)
from analyst.notification_generator import generate_simple_notification  # noqa: E402
# Módulo Analyst (Luana) — Fases 1–6
from analyst.priority_queue import Case, get_queue_summary, prioritize_cases  # noqa: E402
from analyst.error_patterns import ErrorRecord, detect_all_patterns  # noqa: E402
from analyst.communication_templates import (  # noqa: E402
    get_template,
    list_available_templates,
    render_template,
)
from analyst.impact_report import AnalystAction, generate_impact_report  # noqa: E402
from analyst.decision_support import ComplexCaseInput, support_decision  # noqa: E402
from analyst.unified_view import build_unified_view  # noqa: E402
from capability.capability_matrix import get_capability_matrix  # noqa: E402
from prefill.prefill_validator import suggest_polygons, validate_sicar_prefill  # noqa: E402
from progress.progress_service import ProgressTracker  # noqa: E402
from collective.collective_impact import calculate_collective_impact  # noqa: E402
from pra.pra_service import check_pra_eligibility  # noqa: E402
from first_declaration.first_declaration_guide import guide_first_declaration  # noqa: E402
from network.trust_network import generate_leader_template, get_regional_progress  # noqa: E402
from rules.app_rules import calculate_app_width  # noqa: E402
from rules.consolidated_area_rules import check_consolidated_rights  # noqa: E402
from rules.rl_rules import validate_rl_area  # noqa: E402
from translator.notification_translator import translate_notification  # noqa: E402

app = FastAPI(
    title="TerraPilot API",
    version="0.2.0",
    description="Assistente offline para retificações do CAR — Bem Público Digital",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_progress_tracker = ProgressTracker()


class RuleResponse(BaseModel):
    issue_code: str
    legal_ref: str
    human_explanation: str
    fix_steps: list[str]
    visual_example: str | None = None
    min_width_m: int | None = None


class AppRuleRequest(BaseModel):
    river_width_m: float = Field(..., gt=0, description="Largura do rio em metros")


class RlRuleRequest(BaseModel):
    property_area_ha: float = Field(..., gt=0)
    declared_rl_ha: float = Field(..., ge=0)
    rl_percent_legal: int = Field(..., gt=0, le=100)
    biome: str = ""


class ConsolidatedRuleRequest(BaseModel):
    deforestation_date: str = Field(
        ...,
        description="Data da ocupação consolidada (YYYY-MM-DD, antes de 2008-07-22)",
        examples=["2005-03-15"],
    )
    property_size_modulos: float = Field(..., gt=0)
    river_width_m: float = Field(..., gt=0)
    feature_type: Literal["river", "spring", "lake", "vereda"] = "river"


class FirstDeclarationRequest(BaseModel):
    name: str = "produtor"
    municipality: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    property_size_ha: float | None = None
    biome: str | None = None


class PraEligibilityRequest(BaseModel):
    has_environmental_passive: bool = True
    notification_received: bool = False
    car_status: str = "pending"
    deforestation_date: str | None = None
    surplus_vegetation_ha: float | None = None
    municipality: str | None = None


class NotificationRequest(BaseModel):
    technical_text: str = Field(..., min_length=1)


class NotificationResponse(BaseModel):
    simple_text: str
    issue_code: str | None
    original_text: str
    pattern_id: str | None
    fix_step_count: int | None
    legal_ref: str | None = None
    human_explanation: str | None = None
    fix_steps: list[str] | None = None


class PrefillRequest(BaseModel):
    municipality: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(2.0, gt=0)


class SICARSuggestionRequest(BaseModel):
    suggestion: dict[str, Any] = Field(
        ...,
        description="Sugestão do módulo pré-preenchido do SICAR",
        examples=[
            {
                "type": "app",
                "description": "Área de 2ha próxima ao rio foi marcada como APP",
                "area_ha": 2.0,
                "river_width_m": 25,
                "declared_width_m": 50,
            }
        ],
    )


class ProducerProfileRequest(BaseModel):
    name: str = "produtor"
    property_size_ha: float | None = None
    biome: str | None = None
    production_type: str | None = None


class TechnicalNotificationRequest(BaseModel):
    technical_text: str = Field(..., min_length=1)
    producer_profile: ProducerProfileRequest = Field(default_factory=ProducerProfileRequest)


class AudioRequest(BaseModel):
    text: str = Field(..., min_length=1)
    producer_id: str | None = None
    channel: Literal["whatsapp", "sms"] = "whatsapp"
    voice: str = "pt-BR"


class RenderTemplateRequest(BaseModel):
    issue_code: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    channel: Literal["whatsapp", "sms", "audio", "email"] = "whatsapp"


class ImpactReportRequest(BaseModel):
    analyst_id: str = "unknown"
    actions: list[AnalystAction] = Field(default_factory=list)
    benchmark: dict[str, Any] = Field(default_factory=dict)


class UnifiedViewRequest(BaseModel):
    case_id: str
    producer_name: str
    producer_id: str
    municipality: str
    property_size_ha: float
    biome: str
    car_submission_date: str
    sicar_data: dict[str, Any] = Field(default_factory=dict)
    sigef_data: dict[str, Any] | None = None
    notifications: list[dict[str, Any]] = Field(default_factory=list)
    producer_responses: list[dict[str, Any]] = Field(default_factory=list)
    analyst_actions: list[dict[str, Any]] = Field(default_factory=list)
    sent_messages: list[dict[str, Any]] = Field(default_factory=list)
    received_messages: list[dict[str, Any]] = Field(default_factory=list)
    pending_issues: list[dict[str, str]] = Field(default_factory=list)


class WhatsAppRequest(BaseModel):
    phone: str = Field(..., min_length=8)
    message: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "text": "Seu Raimundo, sua Reserva Legal está 2ha menor...",
                "buttons": [{"id": "1", "text": "Ver como corrigir"}],
                "audio_url": "https://terrapilot.gov.br/audio/123.mp3",
            }
        ],
    )


class SMSRequest(BaseModel):
    phone: str = Field(..., min_length=8)
    message: str = Field(..., min_length=1)


class PropertyExportRequest(BaseModel):
    property_id: str
    municipality: str | None = None
    area_ha: float | None = None
    centroid: list[float] | None = None
    geometry: dict[str, Any] | None = None
    polygons: list[dict[str, Any]] | None = None


class GeoJsonExportResponse(BaseModel):
    geojson: str
    feature_count: int


class SicarExportResponse(BaseModel):
    xml: str
    property_id: str


class FAQQueryParams(BaseModel):
    property_size_ha: float | None = None
    modulo_fiscal_ha: float | None = None
    biome: str | None = None
    production_type: Literal["agriculture", "livestock", "mixed", "extractivism"] | None = None
    limit: int | None = Field(None, ge=1, le=50)


def _rule_response_from_app(result: dict[str, Any]) -> RuleResponse:
    return RuleResponse(
        issue_code=result["issue_code"],
        legal_ref=result["legal_ref"],
        human_explanation=result["human_explanation"],
        fix_steps=result["fix_steps"],
        visual_example=result.get("visual_example"),
        min_width_m=result.get("min_width_m"),
    )


def _rule_response_from_rl(result: dict[str, Any]) -> RuleResponse:
    return RuleResponse(
        issue_code=result["issue_code"],
        legal_ref=result["legal_ref"],
        human_explanation=result["human_explanation"],
        fix_steps=result["fix_steps"],
        visual_example=result.get("visual_example"),
        min_width_m=result.get("min_width_m"),
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "online", "version": "0.2.0"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "TerraPilot API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "repository": "https://github.com/kaiquetheodoro/TerraPilot",
    }


@app.post("/api/rules/app", response_model=RuleResponse)
async def validate_app(request: AppRuleRequest) -> RuleResponse:
    """Valida APP de curso d'água — Lei 12.651/2012, Art. 4º, I."""
    try:
        result = calculate_app_width(request.river_width_m)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _rule_response_from_app(result)


@app.post("/api/rules/rl", response_model=RuleResponse)
async def validate_rl(request: RlRuleRequest) -> RuleResponse:
    """Valida Reserva Legal — Lei 12.651/2012, Art. 12."""
    try:
        result = validate_rl_area(
            request.property_area_ha,
            request.declared_rl_ha,
            request.rl_percent_legal,
            biome=request.biome,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _rule_response_from_rl(result)


@app.post("/api/rules/consolidated")
async def validate_consolidated(request: ConsolidatedRuleRequest) -> dict[str, Any]:
    """Verifica direitos adquiridos — Art. 61-A da Lei 12.651/2012."""
    try:
        return check_consolidated_rights(
            request.deforestation_date,
            request.property_size_modulos,
            request.river_width_m,
            request.feature_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/capability/matrix")
async def capability_matrix() -> dict[str, Any]:
    """Matriz Pode/Não Pode do TerraPilot."""
    return get_capability_matrix()


@app.get("/api/network/regional-progress")
async def regional_progress(
    municipality_code: str,
    biome: str = "",
) -> dict[str, Any]:
    """Progresso agregado de regularização na região (sem PII)."""
    return get_regional_progress(municipality_code, biome)


@app.get("/api/network/leader-template/{leader_type}")
async def leader_template(leader_type: str) -> dict[str, Any]:
    """Template para líderes comunitários usarem em reuniões."""
    try:
        return generate_leader_template(leader_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/declare/first-time")
async def first_declaration(request: FirstDeclarationRequest) -> dict[str, Any]:
    """Guia para primeira declaração do CAR."""
    return guide_first_declaration(request.model_dump(exclude_none=True))


@app.post("/api/benefits/pra")
async def pra_eligibility(request: PraEligibilityRequest) -> dict[str, Any]:
    """Verifica elegibilidade e benefícios do PRA (Art. 59)."""
    return check_pra_eligibility(request.model_dump(exclude_none=True))


@app.get("/api/collective/impact/{property_id}")
async def collective_impact(property_id: str) -> dict[str, Any]:
    """Impacto coletivo da regularização individual."""
    try:
        return calculate_collective_impact(property_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/translate/notification", response_model=NotificationResponse)
async def translate_notification_endpoint(request: NotificationRequest) -> NotificationResponse:
    """Traduz notificação técnica da OEMA para linguagem do produtor."""
    try:
        result = translate_notification(request.technical_text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    fix_steps: list[str] | None = None
    legal_ref: str | None = None
    human_explanation = result["simple_text"]

    if result["issue_code"]:
        try:
            guide = get_guide(result["issue_code"])
            fix_steps = [step["instruction"] for step in guide["steps"]]
            legal_ref = "Lei 12.651/2012 — ver guia por issue_code"
        except KeyError:
            pass

    return NotificationResponse(
        simple_text=result["simple_text"],
        issue_code=result["issue_code"],
        original_text=result["original_text"],
        pattern_id=result["pattern_id"],
        fix_step_count=result["fix_step_count"],
        legal_ref=legal_ref,
        human_explanation=human_explanation,
        fix_steps=fix_steps,
    )


@app.get("/api/guide/{issue_code}")
async def get_guide_endpoint(
    issue_code: str,
    min_width_m: int | None = Query(None),
    area_ha: float | None = Query(None),
) -> dict[str, Any]:
    """Retorna guia passo-a-passo visual para um issue_code."""
    context: dict[str, Any] = {}
    if min_width_m is not None:
        context["min_width_m"] = min_width_m
    if area_ha is not None:
        context["area_ha"] = area_ha

    try:
        guide = get_guide(issue_code, **context)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Guia não encontrado: {issue_code}") from exc

    return guide


@app.post("/api/prefill/validate")
async def validate_prefill(request: SICARSuggestionRequest) -> dict[str, Any]:
    """Valida e explica sugestões do módulo pré-preenchido do SICAR."""
    try:
        return validate_sicar_prefill(request.suggestion)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/prefill/suggest")
async def prefill_suggest(request: PrefillRequest) -> dict[str, Any]:
    """Busca polígonos públicos para comparar com sugestões do SICAR."""
    try:
        return suggest_polygons(
            request.municipality,
            request.latitude,
            request.longitude,
            radius_km=request.radius_km,
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/analyst/generate-notification")
async def generate_notification(request: TechnicalNotificationRequest) -> dict[str, Any]:
    """Luana escreve técnico, sistema traduz para linguagem simples."""
    try:
        return generate_simple_notification(
            request.technical_text,
            request.producer_profile.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ========== ENDPOINTS DO MÓDULO ANALYST (Fases 1–6) ==========


@app.post("/api/analyst/prioritize")
async def prioritize_queue(cases: list[Case]) -> dict[str, Any]:
    """Ordena casos por prioridade com razões explicáveis."""
    prioritized = prioritize_cases(cases)
    return {
        "cases": [pc.model_dump() for pc in prioritized],
        "summary": get_queue_summary(prioritized),
    }


@app.post("/api/analyst/detect-patterns")
async def detect_patterns(records: list[ErrorRecord]) -> dict[str, Any]:
    """Detecta padrões de erro para ação preventiva."""
    return detect_all_patterns(records)


@app.get("/api/analyst/templates")
async def list_templates() -> dict[str, Any]:
    """Lista todos os templates de comunicação disponíveis."""
    return {"templates": list_available_templates()}


@app.get("/api/analyst/templates/{issue_code}")
async def get_template_endpoint(issue_code: str) -> dict[str, Any]:
    """Retorna template completo para um tipo de erro."""
    template = get_template(issue_code)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template não encontrado: {issue_code}")
    return template.model_dump()


@app.post("/api/analyst/render-template")
async def render_template_endpoint(request: RenderTemplateRequest) -> dict[str, Any]:
    """Renderiza template com contexto do produtor."""
    rendered = render_template(
        issue_code=request.issue_code,
        context=request.context,
        channel=request.channel,
    )
    if rendered is None:
        raise HTTPException(
            status_code=404,
            detail=f"Template ou canal inválido: {request.issue_code} / {request.channel}",
        )
    return {"rendered": rendered}


@app.post("/api/analyst/impact-report")
async def impact_report_endpoint(request: ImpactReportRequest) -> dict[str, Any]:
    """Gera relatório de impacto do trabalho da analista."""
    report = generate_impact_report(
        analyst_id=request.analyst_id,
        actions=request.actions,
        benchmark=request.benchmark,
    )
    return report.model_dump()


@app.post("/api/analyst/decision-support")
async def decision_support_endpoint(case: ComplexCaseInput) -> dict[str, Any]:
    """Suporte de decisão para casos complexos — não decide, apresenta opções."""
    return support_decision(case).model_dump()


@app.post("/api/analyst/unified-view")
async def unified_view_endpoint(request: UnifiedViewRequest) -> dict[str, Any]:
    """Visão unificada de todos os dados do caso para a Luana."""
    from datetime import datetime

    view = build_unified_view(
        case_id=request.case_id,
        producer_name=request.producer_name,
        producer_id=request.producer_id,
        municipality=request.municipality,
        property_size_ha=request.property_size_ha,
        biome=request.biome,
        sicar_data=request.sicar_data,
        sigef_data=request.sigef_data,
        car_submission_date=datetime.fromisoformat(request.car_submission_date),
        notifications=request.notifications,
        producer_responses=request.producer_responses,
        analyst_actions=request.analyst_actions,
        sent_messages=request.sent_messages,
        received_messages=request.received_messages,
        pending_issues=request.pending_issues,
    )
    return view.model_dump()


# ========== ENDPOINTS ANALYST — Dashboard e canais ==========
async def stuck_producers_endpoint(oema_id: str) -> list[dict[str, Any]]:
    """Dashboard de produtores travados com priorização inteligente."""
    return fetch_stuck_producers(oema_id)


@app.get("/api/analyst/stuck-producers/summary")
async def stuck_producers_summary_endpoint(oema_id: str) -> dict[str, Any]:
    """Resumo da fila de casos para triagem rápida da analista."""
    return get_stuck_producers_summary(oema_id)


@app.get("/api/analyst/effectiveness-stats")
async def effectiveness_stats_endpoint(oema_id: str) -> dict[str, Any]:
    """Estatísticas de eficácia das notificações traduzidas."""
    return get_effectiveness_stats(oema_id)


@app.post("/api/analyst/send-audio")
async def send_audio(request: AudioRequest) -> dict[str, Any]:
    """Gera áudio explicativo para envio via WhatsApp/SMS."""
    try:
        audio_path = text_to_speech(request.text, voice=request.voice)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "status": "ready",
        "audio_path": audio_path,
        "channel": request.channel,
        "producer_id": request.producer_id,
        "message": (
            f"Áudio gerado para envio via {request.channel}. "
            "Use /api/channels/whatsapp/send para enviar ao produtor."
        ),
    }


@app.post("/api/channels/whatsapp/send")
async def send_whatsapp(request: WhatsAppRequest) -> dict[str, Any]:
    """Envia mensagem via WhatsApp."""
    try:
        return send_whatsapp_message(request.phone, request.message)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/channels/sms/send")
async def send_sms_endpoint(request: SMSRequest) -> dict[str, Any]:
    """Envia SMS como fallback."""
    try:
        return send_sms_message(request.phone, request.message)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/channels/whatsapp/webhook")
async def whatsapp_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    """Webhook para receber respostas do WhatsApp."""
    return handle_whatsapp_webhook(payload)


@app.get("/api/progress/{property_id}")
async def get_progress(property_id: str) -> dict[str, Any]:
    """Retorna progresso das retificações do produtor."""
    progress = _progress_tracker.get_progress(property_id)
    history = _progress_tracker.get_history(property_id)
    return {
        "property_id": property_id,
        "progress": progress,
        "history": history,
        "human_explanation": progress["bar_message"],
    }


@app.get("/api/knowledge/faq")
async def knowledge_faq(
    property_size_ha: float | None = Query(None),
    modulo_fiscal_ha: float | None = Query(None),
    biome: str | None = Query(None),
    production_type: Literal["agriculture", "livestock", "mixed", "extractivism"] | None = Query(
        None
    ),
    limit: int | None = Query(None, ge=1, le=50),
) -> dict[str, Any]:
    """FAQ contextual filtrado pelo perfil do produtor."""
    profile: ProducerProfile = {}
    if property_size_ha is not None:
        profile["property_size_ha"] = property_size_ha
    if modulo_fiscal_ha is not None:
        profile["modulo_fiscal_ha"] = modulo_fiscal_ha
    if biome is not None:
        profile["biome"] = biome
    if production_type is not None:
        profile["production_type"] = production_type

    return get_contextual_faq(profile, limit=limit)


@app.post("/api/export/geojson", response_model=GeoJsonExportResponse)
async def export_geojson(request: PropertyExportRequest) -> GeoJsonExportResponse:
    """Exporta dados da propriedade em GeoJSON (RFC 7946)."""
    payload = request.model_dump(exclude_none=True)
    geojson = export_to_geojson(payload)
    import json

    feature_count = len(json.loads(geojson).get("features", []))
    return GeoJsonExportResponse(geojson=geojson, feature_count=feature_count)


@app.post("/api/export/sicar", response_model=SicarExportResponse)
async def export_sicar(request: PropertyExportRequest) -> SicarExportResponse:
    """Exporta dados da propriedade em XML simplificado para SICAR Offline."""
    payload = request.model_dump(exclude_none=True)
    xml = export_to_sicar_xml(payload)
    return SicarExportResponse(xml=xml, property_id=request.property_id)


@app.get("/api/export/progress/{property_id}")
async def export_progress(property_id: str) -> dict[str, Any]:
    """Relatório exportável do progresso de retificações."""
    return export_progress_report(property_id)
