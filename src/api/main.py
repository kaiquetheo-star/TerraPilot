from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
import json

# Adiciona src ao path para importar agent
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent.orchestrator import TerraPilotAgent
from agent.mcp_client import MCPClient

app = FastAPI(title="TerraPilot API", version="0.1.0")

# Inicializa agente
agent = TerraPilotAgent()

class CARSubmission(BaseModel):
    farmer_id: str
    gps_coords: tuple[float, float]
    area_ha: float
    vegetation_type: str
    documents: Optional[list[str]] = None

class ValidationResponse(BaseModel):
    farmer_id: str
    confidence_score: int
    flag_status: str
    reasoning: str
    protected_areas: Optional[list] = None

@app.get("/health")
async def health_check():
    return {"status": "online", "version": "0.1.0"}

@app.post("/api/validate", response_model=ValidationResponse)
async def validate_car(submission: CARSubmission):
    """Valida submissão do CAR usando agente Qwen + MCP"""
    
    # 1. Validação inicial com Qwen
    validation_result = await agent.validate_car_submission({
        "gps_coords": submission.gps_coords,
        "area_ha": submission.area_ha,
        "vegetation_type": submission.vegetation_type
    })
    
    # 2. Consulta MCP para áreas protegidas
    mcp_client = MCPClient()
    try:
        await mcp_client.connect_to_server(
            "/home/kaiquedeoliveiratheodoro/Área de trabalho/TerraPilot/src/mcp_servers/protected_areas.py"
        )
        
        mcp_result = await mcp_client.call_tool("check_protected_area", {
            "lat": submission.gps_coords[0],
            "lng": submission.gps_coords[1]
        })
        
        protected_areas = json.loads(mcp_result).get("protected_areas", [])
        
    finally:
        await mcp_client.cleanup()
    
    # 3. Combina resultados
    return ValidationResponse(
        farmer_id=submission.farmer_id,
        confidence_score=validation_result.get("confidence_score", 0),
        flag_status=validation_result.get("flag_status", "Inconsistente"),
        reasoning=validation_result.get("reasoning", ""),
        protected_areas=protected_areas
    )

@app.get("/")
async def root():
    return {
        "message": "TerraPilot API",
        "docs": "/docs",
        "health": "/health"
    }
