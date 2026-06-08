import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import asyncio
import json

# Cria servidor MCP
server = Server("protected-areas-brasil")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Lista ferramentas disponíveis neste servidor MCP"""
    return [
        types.Tool(
            name="check_protected_area",
            description="Verifica se coordenada GPS sobrepõe área protegida (UC, TI, APP)",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "Latitude em graus decimais"
                    },
                    "lng": {
                        "type": "number",
                        "description": "Longitude em graus decimais"
                    }
                },
                "required": ["lat", "lng"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Executa ferramenta solicitada"""
    if name != "check_protected_area":
        raise ValueError(f"Ferramenta desconhecida: {name}")
    
    lat = arguments.get("lat")
    lng = arguments.get("lng")
    
    # MOCK: Em produção, consultaria API do ICMBio/Funai ou shapefiles
    protected_areas = []
    
    # Simulação: se latitude for par, tem área protegida próxima
    if int(lat) % 2 == 0:
        protected_areas = [
            {
                "name": "Reserva Biológica do Cerrado",
                "type": "Reserva Biológica",
                "distance_km": 2.3,
                "overlap_percentage": 15.5
            }
        ]
    
    result = {
        "query_coords": {"lat": lat, "lng": lng},
        "protected_areas": protected_areas,
        "has_conflict": len(protected_areas) > 0
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

async def main():
    """Inicia servidor MCP via stdio"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="protected-areas-brasil",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
