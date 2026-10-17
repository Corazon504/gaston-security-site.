"""Render og.png, apple-touch-icon.png and phone/desktop preview screenshots.
Run from the repo root:  python3 tools/render.py
"""
import http.server, threading, functools, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
OUT = sys.argv[1] if len(sys.argv) > 1 else ROOT
PORT = 8765

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{PORT}"

with sync_playwright() as p:
    b = p.chromium.launch()
    # Open Graph image
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    pg.set_content(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "og.html")).read()); pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(ROOT, "og.png"))
    # Apple touch icon: logo on red, 180x180
    pg = b.new_page(viewport={"width": 180, "height": 180})
    pg.set_content('<body style="margin:0;background:#B23A20;display:flex;align-items:center;justify-content:center;height:180px">'
                   '<svg viewBox="0 0 24 24" width="120" height="120" fill="none" stroke="#F5EDD8" stroke-width="1.6" stroke-linecap="round"><circle cx="8" cy="12" r="3"/><path d="M11 12h9M17 12v3M20 12v3"/></svg></body>')
    pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(ROOT, "apple-touch-icon.png"))
    # Previews
    for name, w, h, scale in (("preview-phone", 390, 844, 2), ("preview-desktop", 1280, 900, 1)):
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.goto(f"{base}/index.html"); pg.wait_for_timeout(1500)
        pg.screenshot(path=os.path.join(OUT, f"{name}.png"), full_page=True)
    b.close()
srv.shutdown()
print("rendered og.png, apple-touch-icon.png, previews ->", OUT)
