"""
Script de automação para demo do TerraPilot
Executa todos os fluxos end-to-end durante gravação de tela
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def run_demo():
    async with async_playwright() as p:
        # Iniciar browser em modo visível (para gravação)
        browser = await p.chromium.launch(headless=False)
        
        # ========================================
        # PARTE 1: PWA (Mobile Viewport)
        # ========================================
        print("🚀 Iniciando demo do PWA...")
        
        # Criar contexto mobile (iPhone X)
        mobile_context = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            geolocation={'latitude': -15.7801, 'longitude': -47.9292},
            permissions=['geolocation']
        )
        
        mobile_page = await mobile_context.new_page()
        
        # Abrir PWA
        await mobile_page.goto('http://localhost:8080')
        await mobile_page.wait_for_timeout(2000)
        
        # Preencher formulário
        print("📝 Preenchendo formulário...")
        await mobile_page.fill('#farmer-id', 'raimundo_001')
        await mobile_page.wait_for_timeout(500)
        
        await mobile_page.fill('#area-ha', '50')
        await mobile_page.wait_for_timeout(500)
        
        # Selecionar vegetação (chips)
        await mobile_page.click('.veg-chip[data-value="Cerrado"]')
        await mobile_page.wait_for_timeout(300)
        await mobile_page.click('.veg-chip[data-value="Mata Atlântica"]')
        await mobile_page.wait_for_timeout(500)
        
        # Capturar GPS (mock já configurado no contexto)
        print("📍 Capturando GPS...")
        await mobile_page.click('#get-gps-btn')
        await mobile_page.wait_for_timeout(3000)
        
        # Upload de fotos
        print("📸 Fazendo upload de fotos...")
        # Criar fotos dummy
        photos_dir = os.path.join(os.path.dirname(__file__), 'demo_photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Criar 3 fotos dummy (1x1 pixel PNG)
        photo_files = []
        for i in range(3):
            photo_path = os.path.join(photos_dir, f'photo_{i}.png')
            if not os.path.exists(photo_path):
                # Criar imagem dummy
                with open(photo_path, 'wb') as f:
                    # PNG 1x1 pixel verde
                    f.write(bytes.fromhex(
                        '89504e470d0a1a0a0000000d49484452000000010000000108020000009001'
                        '2e00000000c4944415478789c6360606000000002000160e7274200000000'
                        '49454e44ae426082'
                    ))
            photo_files.append(photo_path)
        
        # Upload das fotos
        await mobile_page.set_input_files('#photos', photo_files)
        await mobile_page.wait_for_timeout(2000)
        
        # Preencher observações
        await mobile_page.fill('#notes', 'Propriedade com nascente preservada e reserva legal demarcada.')
        await mobile_page.wait_for_timeout(1000)
        
        # Salvar cadastro
        print("💾 Salvando cadastro...")
        await mobile_page.click('button[type="submit"]')
        await mobile_page.wait_for_timeout(3000)
        
        # ========================================
        # PARTE 2: DASHBOARD (Desktop Viewport)
        # ========================================
        print("👩‍💼 Abrindo Dashboard...")
        
        # Criar contexto desktop
        desktop_context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        desktop_page = await desktop_context.new_page()
        
        # Abrir Dashboard
        await desktop_page.goto('http://localhost:8081')
        await desktop_page.wait_for_timeout(3000)
        
        # Clicar em "Ver Detalhes" da primeira submissão
        print("🔍 Abrindo detalhes da submissão...")
        await desktop_page.click('button.action-btn')
        await desktop_page.wait_for_timeout(2000)
        
        # Aprovar cadastro
        print("✅ Aprovando cadastro...")
        await desktop_page.click('#btn-approve')
        await desktop_page.wait_for_timeout(2000)
        
        # Fechar modal
        await desktop_page.click('#modal-close')
        await desktop_page.wait_for_timeout(1000)
        
        # Mostrar stats atualizados
        print("📊 Stats atualizados no dashboard")
        await desktop_page.wait_for_timeout(2000)
        
        # ========================================
        # PARTE 3: MOSTRAR BACKEND LOGS
        # ========================================
        print("🔧 Mostrando logs do backend...")
        
        # Abrir nova aba com terminal (simulado)
        terminal_page = await desktop_context.new_page()
        await terminal_page.goto('http://localhost:8001/docs')
        await terminal_page.wait_for_timeout(3000)
        
        # ========================================
        # FINALIZAÇÃO
        # ========================================
        print("✅ Demo completa!")
        print("📹 Continue gravando por mais 10 segundos...")
        await asyncio.sleep(10)
        
        # Fechar browser
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_demo())