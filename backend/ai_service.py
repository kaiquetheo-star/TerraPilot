import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aliyun.log import LogClient, LogItem, PutLogsRequest
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

from mcp_protected_areas import check_protected_area
from models import FlagStatus, RegistroIn


VALID_FLAGS: set[FlagStatus] = {"Aprovado", "Revisão Manual", "Inconsistente"}


@dataclass(frozen=True)
class AgentDecision:
    confidence_score: int
    flag_status: FlagStatus
    justificativa_ia: str
    thoughts: str
    mcp_tool_result: dict[str, Any]


@register_tool("mcp_protected_areas")
class ProtectedAreasMCPTool(BaseTool):
    description = (
        "Consulta MCP mockada para verificar se coordenadas sobrepoem terra "
        "indigena ou area de preservacao."
    )
    parameters = [
        {
            "name": "latitude",
            "type": "number",
            "description": "Latitude do registro ambiental.",
            "required": True,
        },
        {
            "name": "longitude",
            "type": "number",
            "description": "Longitude do registro ambiental.",
            "required": True,
        },
    ]

    def call(self, params: str, **_: Any) -> str:
        args = json.loads(params)
        result = check_protected_area(args.get("latitude"), args.get("longitude"))
        return json.dumps(result, ensure_ascii=False)


async def analisar_registro(registro: RegistroIn) -> AgentDecision:
    mcp_tool_result = check_protected_area(registro.latitude, registro.longitude)

    try:
        decision = _run_qwen_agent(registro, mcp_tool_result)
    except Exception as exc:
        decision = _fallback_analysis(registro, mcp_tool_result, str(exc))

    _send_sls_log(
        {
            "event": "agent_decision",
            "registro_id": registro.id,
            "propriedade": registro.nome_propriedade,
            "thoughts": decision.thoughts,
            "mcp_tool_result": decision.mcp_tool_result,
            "confidence_score": decision.confidence_score,
            "flag_status": decision.flag_status,
            "justificativa_ia": decision.justificativa_ia,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    return decision


def log_event(payload: dict[str, Any]) -> None:
    _send_sls_log(payload)


def _run_qwen_agent(
    registro: RegistroIn,
    mcp_tool_result: dict[str, Any],
) -> AgentDecision:
    llm_cfg = {
        "model": os.getenv("QWEN_MODEL", "qwen-max"),
        "model_server": os.getenv("QWEN_MODEL_SERVER", "dashscope"),
        "api_key": os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"),
    }

    agent = Assistant(
        llm=llm_cfg,
        name="raiz_car_environmental_auditor",
        description="Auditor Ambiental CAR com verificacao MCP de areas protegidas.",
        system_message=(
            "Voce e um Auditor Ambiental do CAR. Antes da decisao final, use a "
            "ferramenta mcp_protected_areas para avaliar risco territorial. "
            "Retorne estritamente JSON valido com as chaves: confidence_score, "
            "flag_status, justificativa_ia, thoughts."
        ),
        function_list=["mcp_protected_areas"],
    )

    prompt = f"""
Analise o registro ambiental:
- id: {registro.id}
- propriedade: {registro.nome_propriedade}
- latitude: {registro.latitude}
- longitude: {registro.longitude}
- area_hectares: {registro.area_hectares}
- observacao: {registro.observacao}
- contexto_mcp_preflight: {json.dumps(mcp_tool_result, ensure_ascii=False)}

Contrato de resposta:
{{
  "confidence_score": 0-100,
  "flag_status": "Aprovado" | "Revisão Manual" | "Inconsistente",
  "justificativa_ia": "frase curta",
  "thoughts": "resumo objetivo do raciocinio e da chamada MCP"
}}
"""

    messages = [{"role": "user", "content": prompt}]
    responses = list(agent.run(messages=messages))
    content = _extract_agent_content(responses)
    data = _extract_json(content)

    score = max(0, min(100, int(data["confidence_score"])))
    flag_status = data["flag_status"]
    if flag_status not in VALID_FLAGS:
        raise ValueError(f"flag_status invalido: {flag_status}")

    return AgentDecision(
        confidence_score=score,
        flag_status=flag_status,
        justificativa_ia=str(data.get("justificativa_ia", ""))[:1000],
        thoughts=str(data.get("thoughts", ""))[:2000],
        mcp_tool_result=mcp_tool_result,
    )


def _fallback_analysis(
    registro: RegistroIn,
    mcp_tool_result: dict[str, Any],
    error_message: str,
) -> AgentDecision:
    thoughts = (
        "Fallback deterministico acionado apos falha no Qwen Agent. "
        f"Erro: {error_message[:240]}"
    )

    if registro.latitude is None or registro.longitude is None:
        return AgentDecision(45, "Revisão Manual", "Coordenadas ausentes.", thoughts, mcp_tool_result)
    if mcp_tool_result.get("risk_level") == "critical":
        return AgentDecision(10, "Inconsistente", "Coordenadas invalidas.", thoughts, mcp_tool_result)
    if mcp_tool_result.get("overlaps_protected_area"):
        return AgentDecision(55, "Revisão Manual", "Possivel sobreposicao territorial.", thoughts, mcp_tool_result)
    if registro.area_hectares is None or registro.area_hectares <= 0:
        return AgentDecision(40, "Revisão Manual", "Area nao informada ou invalida.", thoughts, mcp_tool_result)
    if not registro.observacao.strip():
        return AgentDecision(70, "Revisão Manual", "Observacao insuficiente.", thoughts, mcp_tool_result)
    return AgentDecision(88, "Aprovado", "Registro sem conflitos aparentes.", thoughts, mcp_tool_result)


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").replace("json\n", "", 1).strip()
    return json.loads(cleaned)


def _extract_agent_content(responses: list[Any]) -> str:
    for response in reversed(responses):
        if isinstance(response, list):
            for message in reversed(response):
                content = message.get("content") if isinstance(message, dict) else None
                if content:
                    return str(content)
        if isinstance(response, dict) and response.get("content"):
            return str(response["content"])
    raise ValueError("Qwen Agent nao retornou conteudo.")


def _send_sls_log(payload: dict[str, Any]) -> None:
    endpoint = os.getenv("ALIYUN_SLS_ENDPOINT")
    project = os.getenv("ALIYUN_SLS_PROJECT")
    logstore = os.getenv("ALIYUN_SLS_LOGSTORE")
    access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

    if not all([endpoint, project, logstore, access_key_id, access_key_secret]):
        return

    contents = [
        (key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value))
        for key, value in payload.items()
    ]
    item = LogItem(int(datetime.now(timezone.utc).timestamp()), contents)
    request = PutLogsRequest(project, logstore, "raiz-car-agent", "ecs", [item])
    LogClient(endpoint, access_key_id, access_key_secret).put_logs(request)
