import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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
            print(f"   - {tool.name}: {tool.description}")
    
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

# Teste
async def test_mcp_client():
    client = MCPClient()
    
    try:
        await client.connect_to_server("/home/kaiquedeoliveiratheodoro/Área de trabalho/TerraPilot/src/mcp_servers/protected_areas.py")
        
        # Testa ferramenta
        result = await client.call_tool("check_protected_area", {
            "lat": -15.7801,
            "lng": -47.9292
        })
        
        print("\n📍 Resultado da consulta MCP:")
        print(result)
        
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())