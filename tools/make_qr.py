"""Generate print-ready QR codes for the /scan short link.
Run from the repo root:  python3 tools/make_qr.py https://gastonsecurity.com/scan

Outputs in qr/:
  qr-plain.svg / qr-plain.png          bare code, level H, 4-module quiet zone, 1200 px
  qr-card.svg  / qr-card.png           business-card size (~1 in / 300 dpi) + "Scan for service"
  qr-sticker.svg / qr-sticker.png      door / van sticker (~3 in / 300 dpi) + "Scan for service"
Then decodes every PNG with OpenCV and checks it reads back as the URL.
"""
import sys, os, io
import segno
from PIL import Image, ImageDraw, ImageFont
import cv2, numpy as np

URL = sys.argv[1] if len(sys.argv) > 1 else "https://gastonsecurity.com/scan"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qr"); os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

qr = segno.make(URL, error="h")   # level H: 30% damage tolerance
modules = qr.symbol_size(border=0)[0]

# 1) bare code
qr.save(os.path.join(OUT, "qr-plain.svg"), scale=10, border=4, dark="#000000", light="#ffffff")
scale = max(1, 1200 // (modules + 8))
qr.save(os.path.join(OUT, "qr-plain.png"), scale=scale, border=4, dark="#000000", light="#ffffff")

def labeled(name, inches, dpi=300, caption="Scan for service", pad_in=0.08):
    """Code at `inches` wide, caption below, quiet zone included. PNG + SVG."""
    code_px = int(inches * dpi)
    cap_px = int(code_px * 0.17)
    pad = int(pad_in * dpi)
    W = code_px + 2 * pad
    H = code_px + cap_px + 2 * pad
    # PNG
    buf = io.BytesIO(); qr.save(buf, kind="png", scale=max(1, code_px // (modules + 8)), border=4); buf.seek(0)
    code = Image.open(buf).convert("RGB").resize((code_px, code_px), Image.NEAREST)
    img = Image.new("RGB", (W, H), "white"); img.paste(code, (pad, pad))
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FONT, int(cap_px * 0.62))
    tw = d.textlength(caption, font=f)
    d.text(((W - tw) / 2, pad + code_px + cap_px * 0.12), caption, fill="black", font=f)
    img.save(os.path.join(OUT, f"{name}.png"), dpi=(dpi, dpi))
    # SVG (vector; sized in inches so it prints at true size)
    inner = qr.svg_inline(scale=1, border=4, dark="#000000", light="#ffffff", omitsize=True, svgclass=None, lineclass=None)
    cell = code_px / (modules + 8)
    font_px = cap_px * 0.62
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W/dpi:.3f}in" height="{H/dpi:.3f}in" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="#fff"/>'
           f'<g transform="translate({pad},{pad}) scale({cell:.4f})">{inner}</g>'
           f'<text x="{W/2}" y="{pad + code_px + cap_px*0.78:.1f}" text-anchor="middle" '
           f'font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="{font_px:.1f}" fill="#000">{caption}</text></svg>')
    with open(os.path.join(OUT, f"{name}.svg"), "w") as fh: fh.write(svg)

labeled("qr-card", 1.0)
labeled("qr-sticker", 3.0)

# 2) decode test
det = cv2.QRCodeDetector()
ok = True
for fn in ("qr-plain.png", "qr-card.png", "qr-sticker.png"):
    img = cv2.imread(os.path.join(OUT, fn))
    data, _, _ = det.detectAndDecode(img)
    print(f"{fn:16s} -> {data!r}", "OK" if data == URL else "MISMATCH")
    ok &= data == URL
print("version", qr.version, "modules", modules, "error level H")
sys.exit(0 if ok else 1)
