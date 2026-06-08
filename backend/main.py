from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ai_service import analisar_registro, log_event
from database import (
    init_db,
    list_registros,
    save_agent_memory,
    save_received_registro,
    update_ai_result,
)
from mcp_protected_areas import mcp_app
from models import RegistroOut, SyncPayload, SyncResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Raiz.CAR API",
    version="0.1.0",
    description="Recepção e validação de dados ambientais offline-first.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp/protected-areas", mcp_app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/sync", response_model=SyncResponse)
async def sync(payload: SyncPayload) -> SyncResponse:
    salvos: list[RegistroOut] = []

    try:
        for registro in payload.records:
            await save_received_registro(registro)
            decision = await analisar_registro(registro)
            final_record = await update_ai_result(
                registro=registro,
                confidence_score=decision.confidence_score,
                flag_status=decision.flag_status,
                justificativa_ia=decision.justificativa_ia,
                mcp_tool_result=decision.mcp_tool_result,
            )
            await save_agent_memory(
                f"registro:{registro.id}",
                {
                    "registro_id": registro.id,
                    "thoughts": decision.thoughts,
                    "mcp_tool_result": decision.mcp_tool_result,
                    "status_ia": decision.flag_status,
                    "score": decision.confidence_score,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            salvos.append(final_record)

        return SyncResponse(ok=True, recebidos=len(salvos), registros=salvos)
    except Exception as exc:
        log_event(
            {
                "event": "api_error",
                "endpoint": "POST /api/sync",
                "error": str(exc),
                "logged_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        raise HTTPException(status_code=502, detail="Falha no fluxo Raiz.CAR Pro Max")


@app.get("/api/registros", response_model=list[RegistroOut])
async def registros() -> list[RegistroOut]:
    try:
        return await list_registros()
    except Exception as exc:
        log_event(
            {
                "event": "api_error",
                "endpoint": "GET /api/registros",
                "error": str(exc),
                "logged_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        raise HTTPException(status_code=502, detail="Falha ao consultar Tablestore")
