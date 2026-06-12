import os
import json
import asyncio
from dotenv import load_dotenv
from mcp_client import MCPClient

load_dotenv()

class TerraPilotAgent:
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")
        
        # Lista de modelos para tentar (do mais capaz para o mais barato)
        self.model_candidates = [
            "qwen-max",
            "qwen-plus", 
            "qwen-turbo",
            "qwen2.5-72b-instruct",
            "qwen2.5-32b-instruct",
            "qwen2.5-14b-instruct"
        ]
        
        self.model = None
        self.use_mock = False
        
        if not self.api_key:
            print("⚠️  MODO MOCK: QWEN_API_KEY não encontrada")
            self.use_mock = True
        else:
            # Testa qual modelo está disponível
            self.model = self._find_available_model()
            if self.model:
                print(f"✅ Modelo disponível: {self.model}")
            else:
                print("⚠️  Nenhum modelo disponível. Usando MODO MOCK.")
                self.use_mock = True
    
    def _find_available_model(self) -> str | None:
        """Testa modelos até encontrar um disponível"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for model in self.model_candidates:
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": "user", "content": "Diga OK"}
                    ]
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return model
                elif response.status_code == 403:
                    print(f"   ⚠️  {model}: Acesso negado (não ativado)")
                else:
                    print(f"   ⚠️  {model}: Erro {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  {model}: Exceção - {str(e)}")
        
        return None
    
    async def validate_car_submission(self, submission_data: dict) -> dict:
        """Valida submissão do CAR usando Qwen + MCP tools"""
        
        # PASSO 1: Consultar ferramentas MCP (SEMPRE, mesmo em mock mode)
        mcp_data = await self._gather_mcp_data(submission_data)
        
        # PASSO 2: Usar Qwen ou Mock para tomar decisão
        if self.use_mock:
            return self._mock_validation(submission_data, mcp_data)
        
        # PASSO 3: Qwen API real
        import requests
        
        prompt = f"""Você é um especialista em validação do Cadastro Ambiental Rural (CAR) brasileiro.

Analise esta submissão com base nos dados coletados:

## DADOS DA SUBMISSÃO:
- ID do Produtor: {submission_data.get('farmer_id')}
- Área declarada: {submission_data.get('area_ha')} hectares
- Tipo de vegetação: {submission_data.get('vegetation_type')}
- Coordenadas GPS: {submission_data.get('gps_coords')}

## DADOS VALIDADOS POR FERRAMENTAS:
{json.dumps(mcp_data, indent=2, ensure_ascii=False)}

## INSTRUÇÕES:
1. Verifique se as coordenadas estão dentro do Brasil
2. Verifique se há sobreposição com áreas protegidas (UCs ou TIs)
3. Avalie se a área declarada é compatível com o bioma/região
4. Considere o tipo de vegetação declarado vs localização

Retorne APENAS um JSON válido (sem markdown, sem explicações extras):
{{
    "confidence_score": <número de 0 a 100>,
    "flag_status": "<Aprovado|Revisão Manual|Inconsistente>",
    "reasoning": "<explicação técnica da decisão em português, citando os dados das ferramentas>",
    "risks": ["<lista de riscos identificados>"],
    "recommendations": ["<lista de recomendações>"]
}}"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["output"]["choices"][0]["message"]["content"]
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {
                        "confidence_score": 50,
                        "flag_status": "Revisão Manual",
                        "reasoning": f"Resposta não estruturada: {content[:200]}",
                        "risks": ["Resposta da IA não pôde ser parseada"],
                        "recommendations": ["Revisar manualmente"]
                    }
            else:
                return {
                    "error": f"API error {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    async def _gather_mcp_data(self, submission_data: dict) -> dict:
        """Coleta dados das ferramentas MCP"""
        mcp_client = MCPClient()
        gps_coords = submission_data.get('gps_coords')
        
        mcp_results = {
            "location_validation": None,
            "protected_areas": None
        }
        
        if not gps_coords or len(gps_coords) != 2:
            return mcp_results
        
        lat, lng = gps_coords
        
        try:
            # Conectar ao servidor MCP
            server_path = "/home/kaiquedeoliveiratheodoro/Área de trabalho/TerraPilot/src/mcp_servers/protected_areas.py"
            await mcp_client.connect_to_server(server_path)
            
            # Ferramenta 1: Validar localização
            location_result = await mcp_client.call_tool("validate_car_location", {
                "lat": lat,
                "lng": lng
            })
            mcp_results["location_validation"] = json.loads(location_result)
            
            # Ferramenta 2: Verificar áreas protegidas
            overlap_result = await mcp_client.call_tool("check_protected_areas_overlap", {
                "lat": lat,
                "lng": lng
            })
            mcp_results["protected_areas"] = json.loads(overlap_result)
            
        except Exception as e:
            print(f"❌ Erro ao consultar MCP: {e}")
            mcp_results["error"] = str(e)
        finally:
            await mcp_client.cleanup()
        
        return mcp_results
    
    def _mock_validation(self, submission_data: dict, mcp_data: dict) -> dict:
        """Validação mock usando dados reais do MCP"""
        area = submission_data.get('area_ha', 0)
        
        # Extrair dados do MCP
        location = mcp_data.get("location_validation", {})
        protected = mcp_data.get("protected_areas", {})
        
        dentro_brasil = location.get("location", {}).get("dentro_do_brasil", False)
        overlaps = protected.get("overlaps_found", 0)
        
        # Lógica de decisão baseada em dados reais
        risks = []
        recommendations = []
        
        if not dentro_brasil:
            risks.append("Coordenadas fora do território brasileiro")
            recommendations.append("Verificar coordenadas GPS")
        
        if overlaps > 0:
            areas = protected.get("protected_areas", [])
            risks.append(f"Sobreposição com {overlaps} área(s) protegida(s)")
            for area_prot in areas:
                risks.append(f"  - {area_prot.get('nome', 'Área desconhecida')}")
            recommendations.append("Análise presencial obrigatória")
        
        if area < 0.5:
            risks.append("Área muito pequena (possível erro de medição)")
            recommendations.append("Verificar documentação de posse")
        elif area > 500:
            risks.append("Área extensa requer validação detalhada")
            recommendations.append("Análise de impacto ambiental")
        
        # Calcular confidence score
        confidence = 90
        if not dentro_brasil:
            confidence -= 50
        if overlaps > 0:
            confidence -= 30
        if area < 0.5 or area > 500:
            confidence -= 10
        
        confidence = max(0, min(100, confidence))
        
        # Determinar flag
        if confidence >= 80 and len(risks) == 0:
            flag = "Aprovado"
        elif confidence >= 50:
            flag = "Revisão Manual"
        else:
            flag = "Inconsistente"
        
        # Gerar reasoning
        municipio = location.get("location", {}).get("municipio", "Desconhecido")
        estado = location.get("location", {}).get("estado", "Desconhecido")
        
        reasoning = f"Submissão de {area}ha em {municipio}/{estado}. "
        if overlaps > 0:
            reasoning += f"Detectada sobreposição com {overlaps} área(s) protegida(s). "
        if dentro_brasil:
            reasoning += "Coordenadas validadas dentro do Brasil. "
        else:
            reasoning += "ATENÇÃO: Coordenadas fora do Brasil. "
        
        return {
            "confidence_score": confidence,
            "flag_status": flag,
            "reasoning": reasoning,
            "risks": risks,
            "recommendations": recommendations,
            "mcp_data_used": True
        }

# Teste rápido
if __name__ == "__main__":
    agent = TerraPilotAgent()
    
    test_data = {
        "farmer_id": "raimundo_001",
        "gps_coords": [-15.7801, -47.9292],  # Brasília
        "area_ha": 50,
        "vegetation_type": "Cerrado"
    }
    
    print("\n" + "="*60)
    print("🧪 TESTE: Validação Completa com MCP")
    print("="*60)
    
    result = asyncio.run(agent.validate_car_submission(test_data))
    print(json.dumps(result, indent=2, ensure_ascii=False))