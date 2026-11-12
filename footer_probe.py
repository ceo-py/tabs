# -*- coding: utf-8 -*-
"""Analyse the footer band of the lesson cards -> find the video-link line."""
import os
import sys
from collections import Counter
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
LINK = (120, 190, 255)


def is_link(px):
    r, g, b = px[:3]
    return b - g > 40 and g - r > 40


def analyse(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    band = im.crop((0, h - 150, w, h))
    px = band.load()
    bw, bh = band.size

    rows = []
    for y in range(bh):
        n = sum(1 for x in range(bw) if is_link(px[x, y]))
        if n:
            rows.append((y, n))

    if not rows:
        return None

    # contiguous row groups
    groups = []
    cur = [rows[0]]
    for r in rows[1:]:
        if r[0] - cur[-1][0] <= 2:
            cur.append(r)
        else:
            groups.append(cur)
            cur = [r]
    groups.append(cur)

    out = []
    for g in groups:
        y0, y1 = g[0][0], g[-1][0]
        xs = [x for y, _ in g for x in range(bw) if is_link(px[x, y])]
        out.append((h - 150 + y0, h - 150 + y1, min(xs), max(xs), sum(n for _, n in g)))
    return out


if __name__ == '__main__':
    files = sys.argv[1:]
    if not files:
        for d in ('out_gz', 'out'):
            p = os.path.join(ROOT, d)
            if os.path.isdir(p):
                files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith('.png')]
    for f in files:
        rel = os.path.relpath(f, ROOT)
        res = analyse(f)
        if not res:
            print('%-58s NO LINK CLUSTER' % rel)
            continue
        for y0, y1, x0, x1, n in res:
            print('%-58s y=%d..%d x=%d..%d px=%d' % (rel, y0, y1, x0, x1, n))
