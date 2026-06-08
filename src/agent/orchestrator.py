import os
import json
from dotenv import load_dotenv

load_dotenv()

class TerraPilotAgent:
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        self.use_mock = not self.api_key  # Se não tem key, usa mock
        
        if self.use_mock:
            print("⚠️  MODO MOCK: QWEN_API_KEY não encontrada. Usando respostas simuladas.")
        else:
            import dashscope
            dashscope.api_key = self.api_key
            self.model = "qwen-max"
    
    async def validate_car_submission(self, submission_data: dict) -> dict:
        """Valida submissão do CAR usando Qwen ou mock"""
        
        if self.use_mock:
            return self._mock_validation(submission_data)
        
        # Código real com Qwen (será usado quando tiver API key)
        import dashscope
        prompt = f"""
        Analise esta submissão do Cadastro Ambiental Rural (CAR):
        - Coordenadas GPS: {submission_data.get('gps_coords')}
        - Área declarada: {submission_data.get('area_ha')} hectares
        - Tipo de vegetação: {submission_data.get('vegetation_type')}
        
        Retorne JSON estrito com:
        {{
            "confidence_score": <0-100>,
            "flag_status": "<Aprovado|Revisão Manual|Inconsistente>",
            "reasoning": "<explicação da decisão>"
        }}
        """
        
        response = dashscope.Generation.call(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            result_format='message'
        )
        
        if response.status_code == 200:
            try:
                # Tenta parsear JSON da resposta
                content = response.output.choices[0].message.content
                return json.loads(content)
            except:
                return {"raw_response": response.output.text}
        else:
            return {"error": f"API error: {response.code} - {response.message}"}
    
    def _mock_validation(self, submission_data: dict) -> dict:
        """Simula resposta do Qwen para desenvolvimento"""
        area = submission_data.get('area_ha', 0)
        
        # Lógica simples de mock
        if area > 100:
            return {
                "confidence_score": 45,
                "flag_status": "Revisão Manual",
                "reasoning": "Área muito grande requer validação humana"
            }
        elif area < 1:
            return {
                "confidence_score": 20,
                "flag_status": "Inconsistente",
                "reasoning": "Área declarada é muito pequena"
            }
        else:
            return {
                "confidence_score": 85,
                "flag_status": "Aprovado",
                "reasoning": "Área dentro dos parâmetros esperados"
            }

# Teste rápido
if __name__ == "__main__":
    import asyncio
    agent = TerraPilotAgent()
    test_data = {
        "gps_coords": (-15.7801, -47.9292),
        "area_ha": 50,
        "vegetation_type": "Cerrado"
    }
    result = asyncio.run(agent.validate_car_submission(test_data))
    print(json.dumps(result, indent=2, ensure_ascii=False))
