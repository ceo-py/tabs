# -*- coding: utf-8 -*-
"""
Scratch helper: crops for a given list of cards (batch 14), same layout as
make_crops3.py but with an explicit list instead of "not yet in songs.json".

    py -3.14 _c14_crops.py <card-path> [<card-path> ...]

Writes dbg_crops3/<slug>.png and dbg_crops3_sheets/sheet_XX.png
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
CROPS = os.path.join(ROOT, 'dbg_crops3')
SHEETS = os.path.join(ROOT, 'dbg_crops3_sheets')
PER_SHEET = 24
COLS = 6
TW, TH = 420, 300
LAB = 26


def crop(path, out_path, width=1000, bottom=0.6):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    if w > width:
        im = im.resize((width, int(h * width / w)), Image.LANCZOS)
        w, h = im.size
    top = int(h * (1 - bottom))
    im.crop((0, top, w, h)).save(out_path)
    return im.size


def sheet(files, out_path):
    rows = (len(files) + COLS - 1) // COLS
    canvas = Image.new('RGB', (COLS * TW, rows * (TH + LAB)), (18, 18, 24))
    d = ImageDraw.Draw(canvas)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB').resize((TW, TH))
        x = (i % COLS) * TW
        y = (i // COLS) * (TH + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + TH, x + TW, y + TH + LAB], fill=(0, 0, 0))
        name = os.path.splitext(os.path.basename(f))[0]
        d.text((x + 5, y + TH + 6), name[:56], fill=(255, 220, 0))
    canvas.save(out_path)
    return canvas.size


def main():
    cards = sys.argv[1:]
    if not cards:
        print('usage: _c14_crops.py <card> [<card> ...]')
        return
    os.makedirs(CROPS, exist_ok=True)
    os.makedirs(SHEETS, exist_ok=True)

    made = []
    for card in cards:
        src = os.path.join(ROOT, card.replace('/', os.sep))
        if not os.path.exists(src):
            print('MISS %s' % card)
            continue
        slug = os.path.splitext(os.path.basename(card))[0]
        dst = os.path.join(CROPS, slug + '.png')
        crop(src, dst)
        made.append(dst)
        print('crop %s' % slug)

    n = 0
    for i in range(0, len(made), PER_SHEET):
        n += 1
        chunk = made[i:i + PER_SHEET]
        out = os.path.join(SHEETS, 'sheet_%02d.png' % n)
        size = sheet(chunk, out)
        print('  %s  (%d crops, %s)' % (os.path.basename(out), len(chunk), size))


if __name__ == '__main__':
    main()
