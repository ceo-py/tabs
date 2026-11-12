# -*- coding: utf-8 -*-
"""
Make inspection crops of the new GZ cards (batches 5-8).

The chord-diagram detection needs to see the lower part of every card, where
the TAB / CHORD PATTERN / STRUMMING panels live.

    py -3.14 make_crops2.py [batch ...]      # default: all of 5,6,7,8

Writes dbg_crops2/<slug>.png  (bottom 60% of the card, 1000 px wide)
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'dbg_crops2')
BATCHES = [5, 6, 7, 8]


def crop(path, out_path, width=1000, bottom=0.6):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    if w > width:
        im = im.resize((width, int(h * width / w)), Image.LANCZOS)
        w, h = im.size
    top = int(h * (1 - bottom))
    im.crop((0, top, w, h)).save(out_path)
    return im.size


def main():
    batches = [int(a) for a in sys.argv[1:]] or BATCHES
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for bi in batches:
        p = os.path.join(ROOT, 'gz_batches', 'batch%d.json' % bi)
        if not os.path.exists(p):
            print('  missing batch', bi)
            continue
        items = json.load(open(p, encoding='utf-8'))
        for it in items:
            src = os.path.join(ROOT, it['out'].replace('/', os.sep))
            if not os.path.exists(src):
                continue
            dst = os.path.join(OUT, os.path.splitext(os.path.basename(src))[0] + '.png')
            crop(src, dst)
            n += 1
        print('  batch%d: %d crops' % (bi, n))
    print('crops in %s: %d' % (OUT, n))


if __name__ == '__main__':
    main()
