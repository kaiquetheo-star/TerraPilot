import os
from dotenv import load_dotenv
import dashscope

load_dotenv()

class TerraPilotAgent:
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError("QWEN_API_KEY não encontrada")
        
        dashscope.api_key = self.api_key
        self.model = "qwen-max"
    
    async def validate_car_submission(self, submission_data: dict) -> dict:
        """Valida submissão do CAR usando Qwen"""
        prompt = f"""
        Analise esta submissão do Cadastro Ambiental Rural (CAR):
        - Coordenadas GPS: {submission_data.get('gps_coords')}
        - Área declarada: {submission_data.get('area_ha')} hectares
        - Tipo de vegetação: {submission_data.get('vegetation_type')}
        
        Retorne JSON com:
        - confidence_score: 0-100
        - flag_status: "Aprovado", "Revisão Manual" ou "Inconsistente"
        - reasoning: explicação da decisão
        """
        
        response = dashscope.Generation.call(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        if response.status_code == 200:
            # Parse da resposta (vamos refinar depois)
            return {"raw_response": response.output.text}
        else:
            return {"error": f"API error: {response}"}

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
    print(result)