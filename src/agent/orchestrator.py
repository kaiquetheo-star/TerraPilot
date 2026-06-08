import os
import json
from dotenv import load_dotenv

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
        """Valida submissão do CAR usando Qwen ou mock"""
        
        if self.use_mock:
            return self._mock_validation(submission_data)
        
        import requests
        
        prompt = f"""Você é um especialista em validação do Cadastro Ambiental Rural (CAR) brasileiro.

Analise esta submissão:
- Coordenadas GPS: {submission_data.get('gps_coords')}
- Área declarada: {submission_data.get('area_ha')} hectares
- Tipo de vegetação: {submission_data.get('vegetation_type')}

Retorne APENAS um JSON válido (sem markdown, sem explicações extras):
{{
    "confidence_score": <número de 0 a 100>,
    "flag_status": "<Aprovado|Revisão Manual|Inconsistente>",
    "reasoning": "<explicação técnica da decisão em português>"
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
                        "reasoning": f"Resposta não estruturada: {content[:200]}"
                    }
            else:
                return {
                    "error": f"API error {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def _mock_validation(self, submission_data: dict) -> dict:
        """Simula resposta do Qwen para desenvolvimento"""
        area = submission_data.get('area_ha', 0)
        
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
    print("\n📊 Resultado da Validação:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
