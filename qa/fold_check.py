"""Playwright check for the fold layout (screens roughly 600-1000px wide).

usage: python qa/fold_check.py [base_url]
Exits 1 if any rule fails.

Rules
  no-sideways   nothing pokes past the viewport edge (all sizes)
  tap-44        every visible tap target is at least 44x44 (fold sizes)
  two-panes     list + detail blocks sit side by side (fold sizes)
  not-covered   fixed bars never cover a jumped-to heading or the last links (fold sizes)
  safe-area     page gutters honor safe-area-inset-left/right (fold sizes)
"""
import sys
from playwright.sync_api import sync_playwright

ALL_SIZES = [(382, 580), (669, 825), (870, 669), (951, 543), (390, 844), (1440, 900)]
FOLD = {(669, 825), (870, 669), (951, 543)}

# [list pane, detail pane] pairs that should share the row on a fold screen
PANES = {
    "note": ("#note .note-grid > .section-head", "#note .note"),
    "career": (".career-intro", ".career-grid .timeline"),
    "stack": ("#stack .chips", "#stack .tags"),
    "answers": (".answers-intro", ".answers-grid > :last-child"),
}

SIDEWAYS_JS = """() => {
  const vw = document.documentElement.clientWidth, out = [];
  const clips = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      if (getComputedStyle(p).overflowX !== 'visible') return true;
    }
    return false;
  };
  for (const el of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.position === 'fixed') continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if ((r.right > vw + 1 || r.left < -1) && !clips(el))
      out.push(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')} [${Math.round(r.left)}..${Math.round(r.right)}]`);
  }
  return out;
}"""

TAP_JS = """() => {
  const out = [];
  const sel = 'a[href], button, summary, input, select, textarea, [role=button], [tabindex]:not([tabindex="-1"])';
  for (const el of document.querySelectorAll(sel)) {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('[aria-hidden="true"], [hidden]')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (r.right < 0 || r.left > innerWidth) continue;           // off-canvas (skip link, carousel overflow)
    if (r.width < 44 || r.height < 44) {
      const name = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 28);
      out.push(`${el.tagName.toLowerCase()} "${name}" ${Math.round(r.width)}x${Math.round(r.height)}`);
    }
  }
  return out;
}"""

PANES_JS = """(pairs) => {
  const out = {};
  for (const [k, [a, b]] of Object.entries(pairs)) {
    const A = document.querySelector(a), B = document.querySelector(b);
    if (!A || !B) { out[k] = 'missing'; continue; }
    const ra = A.getBoundingClientRect(), rb = B.getBoundingClientRect();
    const side = rb.left >= ra.right - 1 && rb.top < ra.bottom;
    out[k] = side ? 'ok' : `stacked (list ${Math.round(ra.width)}w, detail starts ${Math.round(rb.top - ra.top)}px below)`;
  }
  return out;
}"""

# is the point at the centre of el actually el (not a fixed bar on top of it)?
HIT_JS = """(el) => {
  const r = el.getBoundingClientRect();
  const hit = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 12));
  return !!hit && (el === hit || el.contains(hit) || hit.contains(el));
}"""

SAFE_JS = """() => {
  const wrap = document.querySelector('.wrap');
  const found = { left: false, right: false };
  const walk = rules => {
    for (const r of rules) {
      if (r.media) { if (matchMedia(r.media.mediaText).matches) walk(r.cssRules); continue; }
      if (!r.selectorText || !wrap.matches(r.selectorText)) continue;
      const s = r.style.cssText;
      if (/padding(-left|-inline)?[^;]*safe-area-inset-left/.test(s)) found.left = true;
      if (/padding(-right|-inline)?[^;]*safe-area-inset-right/.test(s)) found.right = true;
    }
  };
  for (const sh of document.styleSheets) { try { walk(sh.cssRules); } catch (e) {} }
  return found;
}"""


def check_size(browser, base, w, h):
    ctx = browser.new_context(viewport={"width": w, "height": h},
                              reduced_motion="reduce", has_touch=w < 1000)
    page = ctx.new_page()
    page.goto(base, wait_until="networkidle")
    page.wait_for_timeout(400)
    results = {}

    bad = page.evaluate(SIDEWAYS_JS)
    results["no-sideways"] = bad

    if (w, h) in FOLD:
        tiny = page.evaluate(TAP_JS)
        menu = page.locator(".menu-btn")
        if menu.is_visible():                                  # check the opened menu too
            menu.click()
            page.wait_for_timeout(400)
            tiny += [f"(menu) {t}" for t in page.evaluate(TAP_JS) if t not in tiny]
            menu.click()
            page.wait_for_timeout(400)
        results["tap-44"] = sorted(set(tiny))

        panes = page.evaluate(PANES_JS, PANES)
        results["two-panes"] = [f"{k}: {v}" for k, v in panes.items() if v != "ok"]

        covered = []
        for sid in page.eval_on_selector_all("main section[id]", "els => els.map(e => e.id)"):
            page.evaluate(f"location.hash = '#{sid}'")
            page.wait_for_timeout(150)
            heading = page.locator(f"#{sid} h2").first
            if heading.count() and not page.evaluate(HIT_JS, heading.element_handle()):
                covered.append(f"#{sid} h2 under a fixed bar")
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        page.wait_for_timeout(400)
        for el in page.query_selector_all("footer a, #contact a, #contact button"):
            if not el.is_visible():
                continue
            # park it on the bottom edge, where a fixed bottom bar would sit
            page.evaluate("el => el.scrollIntoView({block: 'end'})", el)
            page.wait_for_timeout(250)
            if not page.evaluate(HIT_JS, el):
                name = " ".join(el.inner_text().split())[:20]
                covered.append(f"footer/contact '{name}' under a fixed bar")
        results["not-covered"] = covered

        safe = page.evaluate(SAFE_JS)
        results["safe-area"] = [f"no safe-area-inset-{s} in .wrap padding" for s, ok in safe.items() if not ok]

    ctx.close()
    return results


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8090/"
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in ALL_SIZES:
            res = check_size(browser, base, w, h)
            for rule, problems in res.items():
                status = "PASS" if not problems else "FAIL"
                failed += bool(problems)
                print(f"{status}  {w}x{h:<4} {rule:<12} {'' if not problems else f'{len(problems)} issue(s)'}")
                for item in problems[:6]:
                    print(f"        - {item}")
                if len(problems) > 6:
                    print(f"        - ...and {len(problems) - 6} more")
        browser.close()
    print(f"\n{'FAILED' if failed else 'ALL PASSED'}: {failed} rule check(s) failing")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
