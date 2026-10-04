#!/usr/bin/env python3
"""Generate the DEV cover image (1200x630) for A Voz da Avó."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# warm vertical gradient terracotta -> deep brown
top, bot = (199, 106, 58), (122, 56, 30)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))

# subtle sun/heart glow
for r in range(260, 0, -4):
    a = int(18 * (1 - r / 260))
    d.ellipse([W//2 - r, H//2 - r - 40, W//2 + r, H//2 + r - 40],
              outline=(255, 220, 180), width=1)

def font(sz, bold=True):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()

def center_text(y, txt, fnt, fill=(255, 248, 238)):
    bb = d.textbbox((0, 0), txt, font=fnt)
    d.text(((W - (bb[2] - bb[0])) // 2, y), txt, font=fnt, fill=fill)

center_text(150, "🧡", font(90))
center_text(270, "A Voz dos Meus", font(96))
center_text(410, "A voz de quem amamos. Para sempre.", font(44, bold=False), fill=(255, 232, 210))
center_text(500, "Their voices. Forever. — 100% local open-source AI", font(30, bold=False), fill=(240, 210, 185))

img.save("/opt/data/projet/avozdaavo/docs/cover.png")
print("cover saved")
