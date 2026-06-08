from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class ProtectedAreaRequest(BaseModel):
    latitude: float | None
    longitude: float | None


class ProtectedAreaResponse(BaseModel):
    overlaps_protected_area: bool
    overlap_type: str | None
    risk_level: str
    source: str = "mock-mcp-protected-areas"


def check_protected_area(
    latitude: float | None,
    longitude: float | None,
) -> dict[str, Any]:
    if latitude is None or longitude is None:
        return ProtectedAreaResponse(
            overlaps_protected_area=True,
            overlap_type="Coordenadas ausentes",
            risk_level="high",
        ).model_dump()

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return ProtectedAreaResponse(
            overlaps_protected_area=True,
            overlap_type="Coordenadas inválidas",
            risk_level="critical",
        ).model_dump()

    if -15.25 <= latitude <= -14.25 and -53.5 <= longitude <= -52.4:
        return ProtectedAreaResponse(
            overlaps_protected_area=True,
            overlap_type="Terra Indígena",
            risk_level="high",
        ).model_dump()

    if -4.7 <= latitude <= -3.1 and -56.3 <= longitude <= -54.7:
        return ProtectedAreaResponse(
            overlaps_protected_area=True,
            overlap_type="Área de Preservação Permanente",
            risk_level="medium",
        ).model_dump()

    return ProtectedAreaResponse(
        overlaps_protected_area=False,
        overlap_type=None,
        risk_level="low",
    ).model_dump()


mcp_app = FastAPI(title="Raiz.CAR Protected Areas MCP")


@mcp_app.post("/tools/check_protected_area", response_model=ProtectedAreaResponse)
async def protected_area_tool(payload: ProtectedAreaRequest) -> dict[str, Any]:
    return check_protected_area(payload.latitude, payload.longitude)


@mcp_app.post("/mcp")
async def mcp_json_rpc(payload: dict[str, Any]) -> dict[str, Any]:
    params = payload.get("params", {})
    result = check_protected_area(params.get("latitude"), params.get("longitude"))
    return {
        "jsonrpc": "2.0",
        "id": payload.get("id"),
        "result": result,
    }
