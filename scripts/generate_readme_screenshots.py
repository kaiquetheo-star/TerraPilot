#!/usr/bin/env python3
"""Gera screenshots do README a partir de mockups HTML."""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "scripts" / "generate_screenshots.html"
OUT = ROOT / "images" / "screenshots"

SCREENS = {
    "home": "home.png",
    "notification-translated": "notification-translated.png",
    "step-by-step": "step-by-step.png",
    "legal-explanation": "legal-explanation.png",
    "progress": "progress.png",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    file_url = HTML.as_uri()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 400, "height": 720})

        for element_id, filename in SCREENS.items():
            page.goto(file_url)
            locator = page.locator(f"#{element_id} .phone")
            locator.screenshot(path=str(OUT / filename))

        browser.close()

    print(f"Screenshots gerados em {OUT}")


if __name__ == "__main__":
    main()
