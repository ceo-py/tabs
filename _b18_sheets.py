# -*- coding: utf-8 -*-
"""
Scratch helper: contact sheets of a card list — the header strip (title +
subtitle) and the footer strip (YouTube link + note) of every card, scaled to a
readable width. Catches clipped titles, clipped notes and wrong subtitles at a
glance, without reading 25 full-resolution PNGs.

    py -3.14 _b18_sheets.py <card-path> [<card-path> ...]

Writes dbg_b18_sheets/head_XX.png and dbg_b18_sheets/foot_XX.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'dbg_b18_sheets')
F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
PER_SHEET = 8
W = 1200
LAB = 24


def strips(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    if w > W:
        im = im.resize((W, max(1, int(h * W / w))), Image.LANCZOS)
        w, h = im.size
    head = im.crop((0, 0, w, min(h, 210)))
    foot = im.crop((0, max(0, h - 150), w, h))
    return head, foot


def sheet(items, out_path, which):
    canvas = Image.new('RGB', (W, len(items) * (160 + LAB)), (18, 18, 24))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 16)
    y = 0
    for name, im in items:
        canvas.paste(im, (0, y))
        d.rectangle([0, y + im.size[1], W, y + im.size[1] + LAB], fill=(0, 0, 0))
        d.text((5, y + im.size[1] + 4), name, font=fnt, fill=(255, 220, 0))
        y += im.size[1] + LAB
    canvas.save(out_path)
    return canvas.size


def main():
    cards = sys.argv[1:]
    if len(cards) == 1 and cards[0].endswith('.json'):
        import json
        rows = json.load(open(os.path.join(ROOT, cards[0]), encoding='utf-8'))
        cards = [r['out'] for r in rows]
    if not cards:
        print('usage: _b18_sheets.py <card> [<card> ...] | _b18_sheets.py gz_batches/batch18.json')
        return
    os.makedirs(OUT, exist_ok=True)
    heads, foots = [], []
    for card in cards:
        src = os.path.join(ROOT, card.replace('/', os.sep))
        if not os.path.exists(src):
            print('MISS %s' % card)
            continue
        h, f = strips(src)
        heads.append((os.path.basename(card), h))
        foots.append((os.path.basename(card), f))
        print('strip %s' % os.path.basename(card))

    for i in range(0, max(len(heads), len(foots)), PER_SHEET):
        n = i // PER_SHEET + 1
        hc = heads[i:i + PER_SHEET]
        fc = foots[i:i + PER_SHEET]
        if hc:
            print('  head_%02d.png %s' % (n, sheet(hc, os.path.join(OUT, 'head_%02d.png' % n), 'head')))
        if fc:
            print('  foot_%02d.png %s' % (n, sheet(fc, os.path.join(OUT, 'foot_%02d.png' % n), 'foot')))


if __name__ == '__main__':
    main()
