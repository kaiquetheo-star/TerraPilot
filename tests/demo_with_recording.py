import asyncio
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import httpx
from PIL import Image, ImageDraw
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

# Tempos configuráveis (em ms)
TIMING = {
    'intro_pause': 3000,
    'form_field': 2500,
    'gps_capture': 4000,
    'photo_upload': 3000,
    'submit_pause': 3000,
    'sync_complete': 4000,
    'dashboard_intro': 4000,
    'detail_review': 6000,
    'approve_action': 4000,
    'closing': 5000
}

TESTS_DIR = Path(__file__).parent
PHOTOS_DIR = TESTS_DIR / 'demo_photos'
VIDEOS_DIR = TESTS_DIR / 'videos'
SCREENSHOTS_DIR = TESTS_DIR / 'screenshots'


class DemoStats:
    def __init__(self):
        self.actions_completed = 0
        self.warnings = 0


def timestamp():
    return datetime.now().strftime('%H:%M:%S')


def log(message):
    print(f"[{timestamp()}] {message}")


def warn(message, stats=None):
    if stats:
        stats.warnings += 1
    log(f"⚠️  {message}")


def action_done(stats):
    stats.actions_completed += 1


async def save_error_screenshot(page, label, stats):
    """Salva evidência visual quando uma ação falha, sem interromper a gravação."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_label = ''.join(char if char.isalnum() or char in ('-', '_') else '_' for char in label)
    screenshot_path = SCREENSHOTS_DIR / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_label}.png"
    try:
        await page.screenshot(path=str(screenshot_path), full_page=True, timeout=5000)
        log(f"   🖼️  Screenshot de erro salvo em: {screenshot_path}")
    except Exception as exc:
        warn(f"Não foi possível salvar screenshot de erro ({label}): {exc}", stats)


async def safe_goto(page, url, stats, label, timeout=15000):
    """Compatível com Playwright 1.60.0: usa timeout explícito em navegação crítica."""
    try:
        log(f"   🌐 Abrindo {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
        action_done(stats)
        return True
    except Exception as exc:
        warn(f"Falha ao abrir {label}: {exc}", stats)
        await save_error_screenshot(page, f"goto_{label}", stats)
        return False


async def safe_fill(page, selector, value, stats, label, timeout=7000):
    """Espera o elemento antes de preencher para evitar falhas por carregamento tardio."""
    try:
        await page.wait_for_selector(selector, state='visible', timeout=timeout)
        await page.fill(selector, value, timeout=timeout)
        action_done(stats)
        return True
    except PlaywrightTimeoutError:
        warn(f"Elemento não encontrado para preencher '{label}' ({selector})", stats)
        await save_error_screenshot(page, f"fill_{label}", stats)
        return False
    except Exception as exc:
        warn(f"Erro ao preencher '{label}' ({selector}): {exc}", stats)
        await save_error_screenshot(page, f"fill_{label}", stats)
        return False


async def safe_click(page, selector, stats, label, timeout=7000):
    """Isola cliques críticos: se o seletor não existir, registra warning e continua."""
    try:
        await page.wait_for_selector(selector, state='visible', timeout=timeout)
        await page.click(selector, timeout=timeout)
        action_done(stats)
        return True
    except PlaywrightTimeoutError:
        warn(f"Elemento não encontrado para clicar '{label}' ({selector})", stats)
        await save_error_screenshot(page, f"click_{label}", stats)
        return False
    except Exception as exc:
        warn(f"Erro ao clicar '{label}' ({selector}): {exc}", stats)
        await save_error_screenshot(page, f"click_{label}", stats)
        return False


async def safe_set_input_files(page, selector, files, stats, label, timeout=7000):
    """Upload também usa espera explícita, pois inputs podem ser renderizados tardiamente."""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.set_input_files(selector, [str(file_path) for file_path in files], timeout=timeout)
        action_done(stats)
        return True
    except PlaywrightTimeoutError:
        warn(f"Input de upload não encontrado '{label}' ({selector})", stats)
        await save_error_screenshot(page, f"upload_{label}", stats)
        return False
    except Exception as exc:
        warn(f"Erro no upload '{label}' ({selector}): {exc}", stats)
        await save_error_screenshot(page, f"upload_{label}", stats)
        return False


async def safe_evaluate(page, expression, stats, label):
    try:
        await page.evaluate(expression)
        action_done(stats)
        return True
    except Exception as exc:
        warn(f"Erro ao executar script '{label}': {exc}", stats)
        await save_error_screenshot(page, f"evaluate_{label}", stats)
        return False


async def check_services(skip_pwa=False, skip_dashboard=False):
    """Verifica serviços antes do browser para falhar cedo com mensagem clara."""
    services = []
    if not skip_pwa:
        services.append(('PWA', 'http://localhost:8080'))
    if not skip_dashboard:
        services.append(('Dashboard', 'http://localhost:8081'))
    services.append(('Backend', 'http://localhost:8001/health'))

    log("Verificando saúde dos serviços...")
    failures = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services:
            try:
                response = await client.get(url)
                if response.status_code >= 400:
                    failures.append(f"{name} ({url}) retornou HTTP {response.status_code}")
                else:
                    log(f"   ✅ {name} acessível: {url}")
            except httpx.TimeoutException:
                failures.append(f"{name} ({url}) não respondeu em 5 segundos")
            except httpx.HTTPError as exc:
                failures.append(f"{name} ({url}) inacessível: {exc}")

    if failures:
        log("❌ Serviços obrigatórios indisponíveis:")
        for failure in failures:
            log(f"   - {failure}")
        sys.exit(1)


async def create_demo_photos():
    """Cria fotos PNG válidas em path relativo ao arquivo de teste."""
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    photo_files = []
    colors = ['#2d5016', '#4a7c2e', '#6ba84f']  # Tons de verde
    labels = ['Cerrado', 'Nascente', 'Reserva']

    for i, (color, label) in enumerate(zip(colors, labels)):
        photo_path = PHOTOS_DIR / f'photo_{i}.png'

        # Criar imagem 400x300 com gradiente e texto
        img = Image.new('RGB', (400, 300), color=color)
        draw = ImageDraw.Draw(img)

        # Adicionar retângulo decorativo
        draw.rectangle([20, 20, 380, 280], outline='white', width=3)

        # Adicionar texto (se fonte disponível, senão só quadrado)
        try:
            draw.text((150, 140), label, fill='white')
        except Exception:
            pass  # Ignora se não tiver fonte

        img.save(photo_path, 'PNG')
        photo_files.append(photo_path)
        log(f"   📸 Criada: {photo_path}")

    return photo_files


def cleanup_demo_photos():
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR)
        log(f"Fotos temporárias removidas: {PHOTOS_DIR}")


async def record_pwa(browser, photo_files, stats):
    log("Etapa 1/8: Abrindo PWA...")
    log("🎬 Gravando PWA (mobile)...")
    log("   📱 Viewport: 375x812 (iPhone)")

    mobile_context = None
    try:
        mobile_context = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            record_video_dir=str(VIDEOS_DIR),
            record_video_size={'width': 375, 'height': 812},
            # Playwright 1.60.0 não aceita record_video_fps em new_context().
            # A gravação nativa usa apenas record_video_dir e record_video_size.
            geolocation={'latitude': -15.7801, 'longitude': -47.9292},
            permissions=['geolocation'],
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )

        mobile_page = await mobile_context.new_page()

        await safe_goto(mobile_page, 'http://localhost:8080', stats, 'pwa')
        await mobile_page.wait_for_timeout(TIMING['intro_pause'])

        log("Etapa 2/8: Preenchendo formulário mobile...")
        log("   ✏️  Preenchendo ID do produtor...")
        await safe_fill(mobile_page, '#farmer-id', 'raimundo_001', stats, 'ID do produtor')
        await mobile_page.wait_for_timeout(TIMING['form_field'])

        log("   📏 Preenchendo área...")
        await safe_fill(mobile_page, '#area-ha', '50', stats, 'área')
        await mobile_page.wait_for_timeout(TIMING['form_field'])

        log("   🌳 Selecionando vegetação...")
        await safe_click(mobile_page, '.veg-chip[data-value="Cerrado"]', stats, 'vegetação Cerrado')
        await mobile_page.wait_for_timeout(800)
        await safe_click(mobile_page, '.veg-chip[data-value="Mata Atlântica"]', stats, 'vegetação Mata Atlântica')
        await mobile_page.wait_for_timeout(TIMING['form_field'])

        log("Etapa 3/8: Capturando GPS e fotos...")
        log("   📍 Capturando GPS...")
        await safe_click(mobile_page, '#get-gps-btn', stats, 'capturar GPS', timeout=10000)
        await mobile_page.wait_for_timeout(TIMING['gps_capture'])

        log("   📸 Upload de fotos...")
        await safe_set_input_files(mobile_page, '#photos', photo_files, stats, 'fotos', timeout=10000)
        await mobile_page.wait_for_timeout(TIMING['photo_upload'])

        log("Etapa 4/8: Salvando e sincronizando PWA...")
        log("   📝 Observações...")
        await safe_fill(
            mobile_page,
            '#notes',
            'Propriedade com nascente preservada e reserva legal demarcada.',
            stats,
            'observações'
        )
        await mobile_page.wait_for_timeout(TIMING['form_field'])

        log("   💾 Salvando...")
        await safe_click(mobile_page, 'button[type="submit"]', stats, 'salvar cadastro', timeout=10000)
        await mobile_page.wait_for_timeout(TIMING['submit_pause'])

        log("   🔄 Sincronizando...")
        try:
            sync_btn = mobile_page.locator('#sync-btn')
            if await sync_btn.is_visible(timeout=3000):
                await sync_btn.click(timeout=7000)
                action_done(stats)
                await mobile_page.wait_for_timeout(TIMING['sync_complete'])
            else:
                warn("Botão de sincronização não está visível", stats)
                await mobile_page.wait_for_timeout(2000)
        except Exception as exc:
            warn(f"Sincronização ignorada: {exc}", stats)
            await save_error_screenshot(mobile_page, 'sync', stats)
            await mobile_page.wait_for_timeout(2000)

        await mobile_page.wait_for_timeout(2000)

        video = mobile_page.video
        await mobile_context.close()
        mobile_context = None
        if video:
            mobile_video_path = await video.path()
            log(f"   ✅ PWA salvo: {mobile_video_path}")
    finally:
        if mobile_context:
            await mobile_context.close()


async def record_dashboard(browser, stats):
    log("Etapa 5/8: Abrindo Dashboard...")
    log("🎬 Gravando Dashboard (desktop)...")
    log("   🖥️  Viewport: 1920x1080")

    desktop_context = None
    try:
        desktop_context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir=str(VIDEOS_DIR),
            record_video_size={'width': 1920, 'height': 1080},
            # Compatível com Playwright 1.60.0: sem record_video_fps.
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )

        desktop_page = await desktop_context.new_page()

        await safe_goto(desktop_page, 'http://localhost:8081', stats, 'dashboard')
        await desktop_page.wait_for_timeout(TIMING['dashboard_intro'])

        log("Etapa 6/8: Abrindo detalhes da submissão...")
        try:
            await desktop_page.wait_for_selector('button.action-btn', state='visible', timeout=7000)
            first_action_btn = desktop_page.locator('button.action-btn').first
            await first_action_btn.click(timeout=7000)
            action_done(stats)
            await desktop_page.wait_for_timeout(TIMING['detail_review'])

            log("Etapa 7/8: Aprovando submissão...")
            await safe_click(desktop_page, '#btn-approve', stats, 'aprovar submissão', timeout=10000)
            await desktop_page.wait_for_timeout(TIMING['approve_action'])

            await safe_click(desktop_page, '#modal-close', stats, 'fechar modal')
            await desktop_page.wait_for_timeout(2000)
        except PlaywrightTimeoutError:
            warn("Nenhuma submissão pendente no dashboard", stats)
            await save_error_screenshot(desktop_page, 'dashboard_sem_submissao', stats)
            await desktop_page.wait_for_timeout(3000)
        except Exception as exc:
            warn(f"Erro no dashboard: {exc}", stats)
            await save_error_screenshot(desktop_page, 'dashboard', stats)
            await desktop_page.wait_for_timeout(3000)

        log("Etapa 8/8: Finalizando gravação do Dashboard...")
        await safe_evaluate(desktop_page, 'window.scrollTo(0, 0)', stats, 'scroll dashboard')
        await desktop_page.wait_for_timeout(TIMING['closing'])

        video = desktop_page.video
        await desktop_context.close()
        desktop_context = None
        if video:
            desktop_video_path = await video.path()
            log(f"   ✅ Dashboard salvo: {desktop_video_path}")
    finally:
        if desktop_context:
            await desktop_context.close()


def parse_bool(value):
    if isinstance(value, bool):
        return value
    normalized = value.lower()
    if normalized in ('true', '1', 'yes', 'y', 'sim'):
        return True
    if normalized in ('false', '0', 'no', 'n', 'nao', 'não'):
        return False
    raise argparse.ArgumentTypeError("Use true/false para --headless")


def parse_args():
    parser = argparse.ArgumentParser(description='Grava a demo TerraPilot com Playwright.')
    parser.add_argument(
        '--headless',
        nargs='?',
        const=True,
        default=True,
        type=parse_bool,
        help='Executa sem janela visual. Use --headless=false para debug visual.'
    )
    parser.add_argument('--skip-pwa', action='store_true', help='Pula a gravação do PWA.')
    parser.add_argument('--skip-dashboard', action='store_true', help='Pula a gravação do Dashboard.')
    return parser.parse_args()


async def run_demo(args):
    stats = DemoStats()
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    await check_services(skip_pwa=args.skip_pwa, skip_dashboard=args.skip_dashboard)
    photo_files = [] if args.skip_pwa else await create_demo_photos()

    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=args.headless)

            if args.skip_pwa:
                warn("Gravação do PWA pulada por --skip-pwa", stats)
            else:
                await record_pwa(browser, photo_files, stats)

            if args.skip_dashboard:
                warn("Gravação do Dashboard pulada por --skip-dashboard", stats)
            else:
                await record_dashboard(browser, stats)
    finally:
        if browser:
            await browser.close()
        cleanup_demo_photos()

    log("\n" + "=" * 60)
    log("🎉 GRAVAÇÕES COMPLETAS!")
    log("=" * 60)
    log(f"📁 Vídeos salvos em: {VIDEOS_DIR}")
    log(f"✅ {stats.actions_completed} ações completadas, ⚠️ {stats.warnings} warnings")
    log("\n📝 Próximo passo:")
    log("   python tests/join_videos.py")

if __name__ == '__main__':
    asyncio.run(run_demo(parse_args()))