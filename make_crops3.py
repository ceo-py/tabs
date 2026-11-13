# -*- coding: utf-8 -*-
"""
Inspection crops for the chord-diagram classification of the new cards.

The legend under a card must only appear when the card does NOT already show a
fretboard diagram.  So every new card has to be classified:

    DIAGRAM  - the card already contains a fretboard / chord diagram
    LETTERS  - the card shows chord names (letters) only
    NONE     - the card shows no chords at all

The decision needs eyes on the lower part of the card, where the TAB / CHORD
PATTERN / STRUMMING panels live.

    py -3.14 make_crops3.py            # crops + contact sheets for every
                                       # card that is not classified yet

Writes dbg_crops3/<slug>.png        (bottom 60% of the card, 1000 px wide)
       dbg_crops3_sheets/sheet_01.png (6 columns, labelled with the slug)
"""
import json
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
    os.makedirs(CROPS, exist_ok=True)
    os.makedirs(SHEETS, exist_ok=True)

    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    known_path = os.path.join(ROOT, 'chords_has_diagram.json')
    known = json.load(open(known_path, encoding='utf-8')) if os.path.exists(known_path) else {}

    todo = []
    for e in catalog:
        card = e['card']
        if not card.startswith('out_gz/'):
            continue
        if card in known:
            continue
        src = os.path.join(ROOT, card.replace('/', os.sep))
        if not os.path.exists(src):
            continue
        todo.append((card, src))

    print('cards to classify: %d' % len(todo))
    made = []
    for card, src in todo:
        slug = os.path.splitext(os.path.basename(card))[0]
        dst = os.path.join(CROPS, slug + '.png')
        crop(src, dst)
        made.append(dst)

    n = 0
    for i in range(0, len(made), PER_SHEET):
        n += 1
        chunk = made[i:i + PER_SHEET]
        out = os.path.join(SHEETS, 'sheet_%02d.png' % n)
        size = sheet(chunk, out)
        print('  %s  (%d crops, %s)' % (os.path.basename(out), len(chunk), size))
    print('crops: %d in %s' % (len(made), CROPS))


if __name__ == '__main__':
    main()
