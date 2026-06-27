"""
Testa responsividade do PWA em dispositivos mobile.
Valida: botões 48px+, contraste, navegação por touch, offline.
"""
import pytest
from playwright.sync_api import sync_playwright

DEVICES = [
    {"name": "iPhone SE", "width": 375, "height": 667},
    {"name": "Galaxy S8", "width": 360, "height": 740},
    {"name": "iPad Mini", "width": 768, "height": 1024},
]

BASE_URL = "http://localhost:8080"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def _wait_for_app(page):
    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_selector("h1:has-text('TerraPilot')", state="visible")


def _wait_for_service_worker(page):
    page.wait_for_function(
        """async () => {
            if (!('serviceWorker' in navigator)) return false;
            const reg = await navigator.serviceWorker.getRegistration();
            if (!reg) return false;
            if (reg.active) return true;
            await new Promise((resolve) => {
                const worker = reg.installing || reg.waiting;
                if (!worker) { resolve(false); return; }
                worker.addEventListener('statechange', () => {
                    if (worker.state === 'activated') resolve(true);
                });
            });
            return !!reg.active;
        }""",
        timeout=15000,
    )


@pytest.mark.parametrize("device", DEVICES)
def test_pwa_loads_on_device(browser, device):
    """PWA carrega em diferentes tamanhos de tela."""
    context = browser.new_context(
        viewport={"width": device["width"], "height": device["height"]}
    )
    page = context.new_page()
    _wait_for_app(page)

    assert "TerraPilot" in page.title()
    assert page.locator("h1", has_text="TerraPilot").is_visible()

    context.close()


def test_buttons_min_48px(browser):
    """Todos os botões visíveis têm pelo menos 48px de altura (acessibilidade mobile)."""
    context = browser.new_context(viewport={"width": 375, "height": 667})
    page = context.new_page()
    _wait_for_app(page)

    buttons = page.locator("button:visible, .btn:visible, a.btn:visible").all()
    assert buttons, "Nenhum botão visível encontrado na home"

    for button in buttons:
        box = button.bounding_box()
        if box:
            assert box["height"] >= 48, (
                f"Botão '{button.inner_text()}' tem {box['height']}px (mínimo 48px)"
            )

    context.close()


def test_text_readable_without_zoom(browser):
    """Texto é legível sem zoom (fonte mínima 16px)."""
    context = browser.new_context(viewport={"width": 375, "height": 667})
    page = context.new_page()
    _wait_for_app(page)

    font_size = page.evaluate("() => window.getComputedStyle(document.body).fontSize")
    assert int(float(font_size.replace("px", ""))) >= 16, (
        f"Fonte do body é {font_size} (mínimo 16px)"
    )

    context.close()


def test_offline_mode(browser):
    """PWA funciona offline após primeira carga."""
    context = browser.new_context(viewport={"width": 375, "height": 667})
    page = context.new_page()

    _wait_for_app(page)
    _wait_for_service_worker(page)

    context.set_offline(True)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("h1:has-text('TerraPilot')", state="visible", timeout=10000)

    assert page.locator("h1", has_text="TerraPilot").is_visible(), "PWA não funciona offline!"

    context.close()


def test_touch_targets_accessible(browser):
    """Elementos interativos são grandes o suficiente para touch."""
    context = browser.new_context(viewport={"width": 375, "height": 667})
    page = context.new_page()
    _wait_for_app(page)

    page.locator('.bottom-nav a[data-route="notifications/list"]').click()
    page.wait_for_timeout(800)

    action_buttons = page.locator("button:visible, .btn:visible, a.btn:visible").all()
    assert action_buttons, "Nenhum botão visível na tela de avisos"

    for btn in action_buttons:
        box = btn.bounding_box()
        if box:
            assert box["width"] >= 48 and box["height"] >= 48, (
                f"Alvo de toque pequeno: {btn.inner_text()} ({box['width']}x{box['height']}px)"
            )

    context.close()
