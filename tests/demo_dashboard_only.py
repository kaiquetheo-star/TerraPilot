"""
Gravação FOCADA apenas no Dashboard da Luana
Executa o fluxo completo de análise e aprovação
"""
import asyncio
from playwright.async_api import async_playwright
import os
from pathlib import Path

# Timings generosos para narração (em ms)
TIMING = {
    'dashboard_load': 4000,       # Tempo para carregar e mostrar stats
    'stats_view': 4000,           # Tempo admirando os stats cards
    'filters_view': 3000,         # Tempo mostrando filtros
    'table_scroll': 3000,         # Tempo mostrando tabela
    'open_modal': 5000,           # Tempo analisando modal
    'review_reasoning': 6000,     # Tempo lendo reasoning da IA
    'approve_action': 3000,       # Tempo clicando aprovar
    'success_feedback': 3000,     # Tempo vendo feedback
    'final_stats': 5000,          # Tempo vendo stats atualizados
    'closing': 3000               # Pausa final
}

async def run_dashboard_demo():
    videos_dir = Path(__file__).parent / 'videos'
    videos_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        print("🎬 Gravando Dashboard (desktop)...")
        print("   🖥️  Viewport: 1920x1080")
        
        # Criar contexto desktop com gravação
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir=str(videos_dir),
            record_video_size={'width': 1920, 'height': 1080},
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )
        
        page = await context.new_page()
        
        # ========================================
        # CENA 1: Carregar Dashboard e mostrar stats
        # ========================================
        print("   📊 Cena 1: Carregando dashboard e mostrando stats...")
        await page.goto('http://localhost:8081')
        await page.wait_for_timeout(TIMING['dashboard_load'])
        
        # ========================================
        # CENA 2: Mostrar stats cards com hover sutil
        # ========================================
        print("   🎯 Cena 2: Destacando stats cards...")
        
        # Hover em cada stat card para destacar
        stat_cards = page.locator('.stat-card')
        count = await stat_cards.count()
        
        for i in range(count):
            await stat_cards.nth(i).hover()
            await page.wait_for_timeout(800)
        
        await page.wait_for_timeout(TIMING['stats_view'])
        
        # ========================================
        # CENA 3: Mostrar filtros
        # ========================================
        print("   🔍 Cena 3: Mostrando filtros...")
        
        # Clicar em "Pendentes" para filtrar
        await page.click('.filter-btn[data-filter="pending"]')
        await page.wait_for_timeout(1500)
        
        # Voltar para "Todos"
        await page.click('.filter-btn[data-filter="all"]')
        await page.wait_for_timeout(TIMING['filters_view'])
        
        # ========================================
        # CENA 4: Scroll na tabela
        # ========================================
        print("   📋 Cena 4: Navegando na tabela de submissões...")
        
        # Hover nas primeiras linhas da tabela
        table_rows = page.locator('tbody tr')
        row_count = await table_rows.count()
        
        for i in range(min(3, row_count)):
            await table_rows.nth(i).hover()
            await page.wait_for_timeout(1000)
        
        await page.wait_for_timeout(TIMING['table_scroll'])
        
        # ========================================
        # CENA 5: Abrir modal de detalhes
        # ========================================
        print("   🔍 Cena 5: Abrindo detalhes de submissão crítica...")
        
        # Clicar no primeiro botão "Ver Detalhes"
        first_action_btn = page.locator('button.action-btn').first
        if await first_action_btn.count() > 0:
            await first_action_btn.click()
            await page.wait_for_timeout(TIMING['open_modal'])
            
            # ========================================
            # CENA 6: Analisar modal (scroll pelos detalhes)
            # ========================================
            print("   📖 Cena 6: Analisando reasoning da IA...")
            
            # Hover no box de análise da IA
            ai_analysis = page.locator('.ai-analysis')
            if await ai_analysis.count() > 0:
                await ai_analysis.hover()
            
            await page.wait_for_timeout(TIMING['review_reasoning'])
            
            # ========================================
            # CENA 7: Aprovar cadastro
            # ========================================
            print("   ✅ Cena 7: Aprovando cadastro...")
            
            # Hover no botão aprovar antes de clicar
            approve_btn = page.locator('#btn-approve')
            await approve_btn.hover()
            await page.wait_for_timeout(1000)
            
            # Clicar em aprovar
            await approve_btn.click()
            await page.wait_for_timeout(TIMING['approve_action'])
            
            # ========================================
            # CENA 8: Feedback de sucesso
            # ========================================
            print("   🎉 Cena 8: Feedback de aprovação...")
            await page.wait_for_timeout(TIMING['success_feedback'])
            
            # ========================================
            # CENA 9: Fechar modal e ver stats atualizados
            # ========================================
            print("   📊 Cena 9: Fechando modal e vendo stats atualizados...")
            
            # Fechar modal (pode ter fechado sozinho ou precisa clicar)
            try:
                await page.click('#modal-close', timeout=2000)
            except:
                pass  # Modal já fechou sozinho
            
            await page.wait_for_timeout(2000)
            
            # Scroll para o topo para ver stats atualizados
            await page.evaluate('window.scrollTo({top: 0, behavior: "smooth"})')
            await page.wait_for_timeout(TIMING['final_stats'])
            
            # Hover no stat card de "Aprovados Hoje" para destacar
            approved_card = page.locator('.stat-card.approved')
            if await approved_card.count() > 0:
                await approved_card.hover()
                await page.wait_for_timeout(2000)
            
        else:
            print("   ⚠️  Nenhuma submissão encontrada na tabela!")
            await page.wait_for_timeout(5000)
        
        # ========================================
        # CENA 10: Pausa final
        # ========================================
        print("   🎬 Cena 10: Pausa final para encerramento...")
        await page.wait_for_timeout(TIMING['closing'])
        
        # Salvar vídeo
        video_path = await page.video.path()
        await context.close()
        await browser.close()
        
        # Renomear arquivo para algo mais amigável
        video_file = Path(video_path)
        new_name = videos_dir / 'dashboard-only.webm'
        if video_file.exists():
            # Remover antigo se existir
            if new_name.exists():
                new_name.unlink()
            video_file.rename(new_name)
            print(f"\n✅ Dashboard gravado com sucesso!")
            print(f"📁 Arquivo: {new_name}")
            print(f"📏 Tamanho: {new_name.stat().st_size / (1024*1024):.1f} MB")
        
        print("\n" + "="*60)
        print("🎉 GRAVAÇÃO DO DASHBOARD COMPLETA!")
        print("="*60)
        print("\n📝 Próximos passos:")
        print("   1. Converter para MP4 (opcional):")
        print("      ffmpeg -i tests/videos/dashboard-only.webm -c:v libx264 tests/videos/dashboard-only.mp4")
        print("   2. Juntar com vídeo do PWA no editor (CapCut/DaVinci)")
        print("   3. Adicionar narração sincronizada")

if __name__ == '__main__':
    asyncio.run(run_dashboard_demo())
