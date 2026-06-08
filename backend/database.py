import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any

import tablestore as ots

from models import FlagStatus, RegistroIn, RegistroOut


REGISTROS_TABLE = "RegistrosAmbientais"
MEMORY_TABLE = "AgentMemory"


def _client() -> ots.OTSClient:
    return ots.OTSClient(
        os.environ["ALIBABA_TABLESTORE_ENDPOINT"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
        os.environ["ALIBABA_TABLESTORE_INSTANCE"],
    )


def _create_table_if_missing(
    client: ots.OTSClient,
    table_name: str,
    primary_key_name: str,
) -> None:
    table_meta = ots.TableMeta(table_name, [(primary_key_name, "STRING")])
    table_options = ots.TableOptions(
        time_to_live=-1,
        max_version=1,
        max_time_deviation=86400,
    )
    throughput = ots.ReservedThroughput(ots.CapacityUnit(0, 0))

    try:
        client.create_table(table_meta, table_options, throughput)
    except Exception as exc:
        if "OTSObjectAlreadyExist" not in str(exc) and "already exist" not in str(exc):
            raise


async def init_db() -> None:
    await asyncio.to_thread(_init_db_sync)


def _init_db_sync() -> None:
    client = _client()
    _create_table_if_missing(client, REGISTROS_TABLE, "id")
    _create_table_if_missing(client, MEMORY_TABLE, "memory_key")


async def save_received_registro(registro: RegistroIn) -> RegistroOut:
    return await asyncio.to_thread(_save_received_registro_sync, registro)


def _save_received_registro_sync(registro: RegistroIn) -> RegistroOut:
    now = datetime.now(timezone.utc).isoformat()
    row = ots.Row(
        [("id", registro.id)],
        {
            "PUT": [
                ("propriedade", registro.nome_propriedade),
                ("coordenadas", _coords(registro.latitude, registro.longitude)),
                ("latitude", _safe_float(registro.latitude)),
                ("longitude", _safe_float(registro.longitude)),
                ("area_hectares", _safe_float(registro.area_hectares)),
                ("status_ia", "Revisão Manual"),
                ("score", 0),
                ("observacao", registro.observacao),
                ("data_coleta", registro.data_coleta.isoformat()),
                ("justificativa_ia", "Registro recebido; análise IA pendente."),
                ("mcp_tool_result", "{}"),
                ("criado_em", now),
            ]
        },
    )
    _client().update_row(
        REGISTROS_TABLE,
        row,
        ots.Condition(ots.RowExistenceExpectation.IGNORE),
    )
    return get_registro_sync(registro.id)


async def update_ai_result(
    registro: RegistroIn,
    confidence_score: int,
    flag_status: FlagStatus,
    justificativa_ia: str,
    mcp_tool_result: dict[str, Any],
) -> RegistroOut:
    return await asyncio.to_thread(
        _update_ai_result_sync,
        registro,
        confidence_score,
        flag_status,
        justificativa_ia,
        mcp_tool_result,
    )


def _update_ai_result_sync(
    registro: RegistroIn,
    confidence_score: int,
    flag_status: FlagStatus,
    justificativa_ia: str,
    mcp_tool_result: dict[str, Any],
) -> RegistroOut:
    row = ots.Row(
        [("id", registro.id)],
        {
            "PUT": [
                ("propriedade", registro.nome_propriedade),
                ("coordenadas", _coords(registro.latitude, registro.longitude)),
                ("latitude", _safe_float(registro.latitude)),
                ("longitude", _safe_float(registro.longitude)),
                ("area_hectares", _safe_float(registro.area_hectares)),
                ("status_ia", flag_status),
                ("score", int(confidence_score)),
                ("observacao", registro.observacao),
                ("data_coleta", registro.data_coleta.isoformat()),
                ("justificativa_ia", justificativa_ia),
                ("mcp_tool_result", json.dumps(mcp_tool_result, ensure_ascii=False)),
            ]
        },
    )
    _client().update_row(
        REGISTROS_TABLE,
        row,
        ots.Condition(ots.RowExistenceExpectation.IGNORE),
    )
    return get_registro_sync(registro.id)


async def save_agent_memory(memory_key: str, content: dict[str, Any]) -> None:
    await asyncio.to_thread(_save_agent_memory_sync, memory_key, content)


def _save_agent_memory_sync(memory_key: str, content: dict[str, Any]) -> None:
    row = ots.Row(
        [("memory_key", memory_key)],
        {
            "PUT": [
                ("content", json.dumps(content, ensure_ascii=False)),
                ("updated_at", datetime.now(timezone.utc).isoformat()),
            ]
        },
    )
    _client().update_row(
        MEMORY_TABLE,
        row,
        ots.Condition(ots.RowExistenceExpectation.IGNORE),
    )


async def list_registros() -> list[RegistroOut]:
    return await asyncio.to_thread(_list_registros_sync)


def _list_registros_sync() -> list[RegistroOut]:
    rows: list[RegistroOut] = []
    next_start_pk = None

    while True:
        consumed, next_start_pk, row_items, _ = _client().get_range(
            REGISTROS_TABLE,
            ots.Direction.FORWARD,
            inclusive_start_primary_key=next_start_pk or [("id", ots.INF_MIN)],
            exclusive_end_primary_key=[("id", ots.INF_MAX)],
            columns_to_get=[
                "propriedade",
                "coordenadas",
                "latitude",
                "longitude",
                "area_hectares",
                "status_ia",
                "score",
                "observacao",
                "data_coleta",
                "justificativa_ia",
                "mcp_tool_result",
                "criado_em",
            ],
            limit=200,
        )
        del consumed
        rows.extend(_row_to_registro(row) for row in row_items)

        if not next_start_pk:
            break

    priority = {"Revisão Manual": 0, "Inconsistente": 1, "Aprovado": 2}
    return sorted(
        rows,
        key=lambda item: (
            priority.get(item.status_ia, 9),
            item.data_coleta,
        ),
        reverse=False,
    )


def get_registro_sync(registro_id: str) -> RegistroOut:
    _, row, _ = _client().get_row(REGISTROS_TABLE, [("id", registro_id)])
    if not row:
        raise LookupError(f"Registro {registro_id} não encontrado")
    return _row_to_registro(row)


def _row_to_registro(row: ots.Row) -> RegistroOut:
    attrs = dict(row.attribute_columns)
    primary = dict(row.primary_key)
    status = attrs.get("status_ia", "Revisão Manual")
    score = int(attrs.get("score", 0))
    mcp_raw = attrs.get("mcp_tool_result") or "{}"

    try:
        mcp_tool_result = json.loads(mcp_raw)
    except json.JSONDecodeError:
        mcp_tool_result = {"raw": mcp_raw}

    latitude = _none_if_empty(attrs.get("latitude"))
    longitude = _none_if_empty(attrs.get("longitude"))
    propriedade = attrs.get("propriedade", "")

    return RegistroOut(
        id=primary["id"],
        nome_propriedade=propriedade,
        propriedade=propriedade,
        observacao=attrs.get("observacao", ""),
        latitude=latitude,
        longitude=longitude,
        coordenadas=attrs.get("coordenadas", _coords(latitude, longitude)),
        area_hectares=_none_if_empty(attrs.get("area_hectares")),
        data_coleta=attrs.get("data_coleta", datetime.now(timezone.utc).isoformat()),
        confidence_score=score,
        score=score,
        flag_status=status,
        status_ia=status,
        justificativa_ia=attrs.get("justificativa_ia"),
        mcp_tool_result=mcp_tool_result,
        criado_em=attrs.get("criado_em", datetime.now(timezone.utc).isoformat()),
    )


def _coords(latitude: float | None, longitude: float | None) -> str:
    if latitude is None or longitude is None:
        return ""
    return f"{latitude},{longitude}"


def _safe_float(value: float | None) -> float | str:
    return "" if value is None else float(value)


def _none_if_empty(value: Any) -> float | None:
    if value in ("", None):
        return None
    return float(value)
