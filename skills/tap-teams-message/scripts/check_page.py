#!/usr/bin/env python3
"""Render a built Teams message page and test its Copy button.

Usage:
  python3 check_page.py page.html [--out-dir shots]

Saves light.png and mobile.png (full page) in --out-dir, clicks the copy
button, and prints what landed on the clipboard (text/html size, text/plain text)
plus any console errors. Needs Playwright with a Chromium browser.
The page is served over http://127.0.0.1 because the clipboard is blocked on file://.
"""
import argparse
import functools
import glob
import http.server
import os
import socketserver
import sys
import threading
from pathlib import Path

READ_CLIPBOARD = """async () => {
  const out = {};
  for (const item of await navigator.clipboard.read())
    for (const t of item.types) out[t] = await (await item.getType(t)).text();
  return out;
}"""


def launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        candidates = [os.environ.get("CHROMIUM_PATH", "")] + glob.glob("/opt/pw-browsers/chromium-*/chrome-linux64/chrome")
        for path in candidates:
            if path and Path(path).exists():
                return p.chromium.launch(executable_path=path)
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--out-dir", default="shots")
    args = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed: pip install playwright && python3 -m playwright install chromium")
        return 2

    page = Path(args.page).resolve()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=str(page.parent))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    url = f"{base}/{page.name}"

    errors = []
    with sync_playwright() as p:
        browser = launch(p)
        ctx = browser.new_context(viewport={"width": 1366, "height": 768}, color_scheme="light")
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(url)
        page_scroll = pg.evaluate("document.documentElement.scrollHeight > innerHeight + 1 || document.documentElement.scrollWidth > innerWidth + 1")
        inner = pg.evaluate("""() => [...document.querySelectorAll('.pane, .canvas .teams, .col')]
            .filter(e => e.offsetParent && e.scrollHeight > e.clientHeight + 1).map(e => e.className.split(' ').slice(-1)[0])""")
        pg.screenshot(path=str(out / "light.png"), full_page=True)
        fields = pg.eval_on_selector_all(".field label", "els => els.map(e => e.textContent)")
        pg.click("#btn-copy")
        if fields:
            pg.wait_for_timeout(200)
            pg.click("#btn-copy")   # empty fields make the first click a warning
        pg.wait_for_timeout(400)
        clip = pg.evaluate(READ_CLIPBOARD)
        notes = pg.eval_on_selector_all("#notes li", "els => els.map(e => e.textContent.trim())")
        size = pg.inner_text("#size-chip")
        ctx.close()

        mob = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        mp = mob.new_page()
        mp.goto(url)
        overflow = mp.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        mp.screenshot(path=str(out / "mobile.png"), full_page=True)
        mob.close()
        browser.close()
    httpd.shutdown()

    print(f"Screenshots: {out / 'light.png'}, {out / 'mobile.png'}")
    print(f"Clipboard types: {', '.join(sorted(clip)) or 'NONE'}")
    print(f"text/html: {len(clip.get('text/html', ''))} chars | size meter: {size}")
    print(f"Placeholder fields: {fields or 'none'}")
    print(f"Page notes: {notes or 'none'}")
    print(f"Page scroll at 1366x768: {'YES (fix it)' if page_scroll else 'no'}")
    print(f"Panels scrolling inside at 1366x768: {inner or 'none'}")
    print(f"Horizontal scroll on mobile: {'YES (fix it)' if overflow else 'no'}")
    print(f"Console errors: {errors or 'none'}")
    print("---- text/plain ----")
    print(clip.get("text/plain", ""))
    ok = "text/html" in clip and "text/plain" in clip and not errors and not overflow and not page_scroll
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
