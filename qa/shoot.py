"""Full-page screenshots of the site at the fold / phone / desktop sizes.

usage: python qa/shoot.py <out_dir> [base_url]
Runs with reduced motion and a dark theme so captures are deterministic
and can be diffed pixel for pixel.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SIZES = [(382, 580), (669, 825), (870, 669), (951, 543), (390, 844), (1440, 900)]
PAGES = {"home": "/"}  # single-page site: every section lives on /


def settle(page):
    # walk the page so every IntersectionObserver reveal fires, then return to top
    height = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(60)
        y += 300
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1700)


def main():
    out = Path(sys.argv[1])
    base = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8090"
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in SIZES:
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                reduced_motion="reduce",
                color_scheme="dark",
                has_touch=w < 1000,
            )
            page = ctx.new_page()
            for name, path in PAGES.items():
                page.goto(base + path, wait_until="networkidle")
                settle(page)
                file = out / f"{name}-{w}x{h}.png"
                page.screenshot(path=str(file), full_page=True, animations="disabled",
                                mask=[page.locator("#trace-ms")])
                print(file)
            ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
