import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import asyncio
import json
import httpx

server = Server("car-validation-brasil")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="validate_car_location",
            description="Valida coordenadas GPS usando reverse geocoding para identificar município, estado e país. Crucial para validar submissões do CAR.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude (Ex: -15.7801)"},
                    "lng": {"type": "number", "description": "Longitude (Ex: -47.9292)"}
                },
                "required": ["lat", "lng"]
            }
        ),
        types.Tool(
            name="check_protected_areas_overlap",
            description="Verifica se as coordenadas sobrepõem Unidades de Conservação (UCs) ou Terras Indígenas (TIs).",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lng": {"type": "number", "description": "Longitude"}
                },
                "required": ["lat", "lng"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    lat = arguments.get("lat")
    lng = arguments.get("lng")

    if name == "validate_car_location":
        return await get_location_data(lat, lng)
    elif name == "check_protected_areas_overlap":
        return await check_protected_areas(lat, lng)
    else:
        raise ValueError(f"Ferramenta desconhecida: {name}")

async def get_location_data(lat: float, lng: float) -> list[types.TextContent]:
    """
    Usa Nominatim (OpenStreetMap) para reverse geocoding.
    Gratuito, sem necessidade de API key, funciona globalmente.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&accept-language=pt-BR"
    
    headers = {
        "User-Agent": "TerraPilot/1.0 (hackathon project)"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                
                # Extrair informações relevantes
                result = {
                    "status": "success",
                    "location": {
                        "pais": address.get("country", "Desconhecido"),
                        "estado": address.get("state", "Desconhecido"),
                        "municipio": address.get("municipality") or address.get("city") or address.get("town", "Desconhecido"),
                        "coordenadas_validas": True,
                        "dentro_do_brasil": address.get("country_code", "").upper() == "BR"
                    },
                    "endereco_completo": data.get("display_name", "")
                }
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            else:
                # Fallback: mock inteligente baseado em coordenadas conhecidas
                return await mock_location_data(lat, lng)
                
    except Exception as e:
        # Fallback em caso de erro de rede
        return await mock_location_data(lat, lng)

async def mock_location_data(lat: float, lng: float) -> list[types.TextContent]:
    """Mock inteligente para quando a API está indisponível."""
    # Regiões conhecidas do Brasil
    regions = [
        {"lat_range": (-34, 5), "lng_range": (-74, -35), "estado": "Brasil", "municipio": "Município Brasileiro"},
    ]
    
    # Verificar se está dentro do Brasil (aproximado)
    dentro_brasil = -34 <= lat <= 5 and -74 <= lng <= -35
    
    result = {
        "status": "success",
        "location": {
            "pais": "Brasil" if dentro_brasil else "Desconhecido",
            "estado": "Estado Brasileiro" if dentro_brasil else "Desconhecido",
            "municipio": "Município Brasileiro" if dentro_brasil else "Desconhecido",
            "coordenadas_validas": True,
            "dentro_do_brasil": dentro_brasil
        },
        "endereco_completo": f"Coordenadas: {lat}, {lng}",
        "note": "Dados mockados - API indisponível"
    }
    
    return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

async def check_protected_areas(lat: float, lng: float) -> list[types.TextContent]:
    """Verifica sobreposição com áreas protegidas."""
    protected_areas_db = [
        {"nome": "Parque Nacional de Brasília", "tipo": "UC - Proteção Integral", "lat": -15.75, "lng": -47.90},
        {"nome": "Terra Indígena Xingu", "tipo": "TI", "lat": -12.50, "lng": -52.50},
        {"nome": "Parque Nacional da Chapada dos Veadeiros", "tipo": "UC - Proteção Integral", "lat": -14.10, "lng": -47.60},
    ]
    
    overlaps = []
    for area in protected_areas_db:
        # Distância aproximada em graus (0.5 graus ≈ 55km)
        dist = ((lat - area['lat'])**2 + (lng - area['lng'])**2)**0.5
        if dist < 0.5:
            overlaps.append({
                "nome": area['nome'],
                "tipo": area['tipo'],
                "distancia_km": round(dist * 111, 2)  # Conversão aproximada
            })

    result = {
        "status": "success",
        "query_coords": {"lat": lat, "lng": lng},
        "overlaps_found": len(overlaps),
        "protected_areas": overlaps if overlaps else "Nenhuma sobreposição detectada em áreas cadastradas."
    }
    
    return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="car-validation-brasil",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())