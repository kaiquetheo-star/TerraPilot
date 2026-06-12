import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Caminho para o seu servidor MCP (ajuste se necessário)
SERVER_SCRIPT = "/home/kaiquedeoliveiratheodoro/Área de trabalho/TerraPilot/src/mcp_servers/protected_areas.py"

class MCPClient:
    def __init__(self):
        self.session = None
        self._streams_context = None
        self._session_context = None
    
    async def connect_to_server(self, server_script_path: str):
        """Conecta a um servidor MCP"""
        server_params = StdioServerParameters(
            command="python3",
            args=[server_script_path]
        )
        
        self._streams_context = stdio_client(server_params)
        read, write = await self._streams_context.__aenter__()
        
        self._session_context = ClientSession(read, write)
        self.session = await self._session_context.__aenter__()
        
        # Inicializa conexão
        await self.session.initialize()
        
        # Lista ferramentas disponíveis
        tools = await self.session.list_tools()
        print(f"✅ Conectado ao servidor MCP. Ferramentas disponíveis:")
        for tool in tools.tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Chama ferramenta do servidor MCP"""
        if not self.session:
            raise RuntimeError("Não conectado ao servidor MCP")
        
        result = await self.session.call_tool(tool_name, arguments)
        return result.content[0].text
    
    async def cleanup(self):
        """Fecha conexão"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

async def test_mcp_client():
    client = MCPClient()
    
    try:
        # Conectar ao servidor
        await client.connect_to_server(SERVER_SCRIPT)
        
        print("\n" + "="*60)
        print(" TESTE 1: API REAL DO IBGE (validate_car_location)")
        print("="*60)
        
        # Testar ferramenta 1: Validação IBGE (Coordenadas de Brasília)
        result_ibge = await client.call_tool("validate_car_location", {
            "lat": -15.7801,
            "lng": -47.9292
        })
        print(f"📍 Resultado IBGE:\n{result_ibge}")
        
        print("\n" + "="*60)
        print("🧪 TESTE 2: ÁREAS PROTEGIDAS (check_protected_areas_overlap)")
        print("="*60)
        
        # Testar ferramenta 2: Áreas Protegidas (Perto de Brasília - deve achar sobreposição)
        result_overlap = await client.call_tool("check_protected_areas_overlap", {
            "lat": -15.75,  # Perto do Parque Nacional de Brasília
            "lng": -47.90
        })
        print(f"🌳 Resultado Áreas Protegidas:\n{result_overlap}")
        
        print("\n" + "="*60)
        print("🧪 TESTE 3: ÁREAS PROTEGIDAS (Local sem sobreposição)")
        print("="*60)
        
        # Testar ferramenta 2: Áreas Protegidas (Local longe - não deve achar sobreposição)
        result_no_overlap = await client.call_tool("check_protected_areas_overlap", {
            "lat": -23.5505,  # São Paulo
            "lng": -46.6333
        })
        print(f"🌳 Resultado Sem Sobreposição:\n{result_no_overlap}")
        
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())