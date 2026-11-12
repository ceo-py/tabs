# -*- coding: utf-8 -*-
"""Contact sheet of the bottom strip of every built site card (link check)."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(ROOT, 'site', 'cards')
OUT = os.path.join(ROOT, 'dbg_footers.png')

STRIP = 130          # px from the bottom
COLW = 520
PAD = 4

files = sorted(f for f in os.listdir(CARDS) if f.endswith('.webp'))
rows = []
for f in files:
    im = Image.open(os.path.join(CARDS, f)).convert('RGB')
    w, h = im.size
    strip = im.crop((0, h - STRIP, w, h))
    sw = COLW
    sh = max(1, int(STRIP * sw / w))
    strip = strip.resize((sw, sh), Image.LANCZOS)
    rows.append((f, strip))

cols = 2
per = cols
colw = COLW + 150
n = len(rows)
rowcount = (n + cols - 1) // cols
rowh = rows[0][1].size[1] + PAD + 16

sheet = Image.new('RGB', (colw * cols, rowh * rowcount + 20), (25, 25, 45))
d = ImageDraw.Draw(sheet)
for i, (name, strip) in enumerate(rows):
    cx = (i % cols) * colw
    cy = (i // cols) * rowh + 16
    sheet.paste(strip, (cx + 145, cy))
    d.text((cx + 4, cy + 4), name[:30], fill=(255, 255, 255))
sheet.save(OUT)
print('saved', OUT, sheet.size, 'cards:', len(files))
