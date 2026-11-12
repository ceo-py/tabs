"""Stack crop PNGs vertically into one sheet for a single verification read.

Usage: py -3.14 b5_sheet.py out.png crop1.png [crop2.png ...]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1]
paths = sys.argv[2:]
TW = 1500
imgs = []
for p in paths:
    im = Image.open(p).convert('RGB')
    h = int(im.size[1] * TW / im.size[0])
    imgs.append((p, im.resize((TW, h), Image.LANCZOS)))
total = sum(i.size[1] for _, i in imgs) + 30 * (len(imgs) - 1) + 24 * len(imgs)
canvas = Image.new('RGB', (TW, total), (25, 25, 25))
d = ImageDraw.Draw(canvas)
fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
y = 0
for p, im in imgs:
    d.rectangle([0, y, TW - 1, y + 24], fill=(0, 0, 0))
    d.text((6, y + 3), p.split('\\')[-1], font=fnt, fill=(255, 220, 0))
    y += 24
    canvas.paste(im, (0, y))
    y += im.size[1] + 30
canvas.save(out)
print('saved', out, canvas.size)
