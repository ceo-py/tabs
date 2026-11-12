# -*- coding: utf-8 -*-
"""Analyse every link-blue group in the lower part of each card -> pick the rule."""
import os
import sys
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
BG = (17, 17, 33)
THRESH = 40


def link_mask(im):
    r, g, b = im.split()
    bog = ImageChops.subtract(b, g).point(lambda v: 255 if v > THRESH else 0)
    gor = ImageChops.subtract(g, r).point(lambda v: 255 if v > THRESH else 0)
    return ImageChops.multiply(bog, gor)


def groups(mask, top, gap=4):
    """contiguous row groups of the mask -> list of (y0,y1,x0,x1,pixels)"""
    w, h = mask.size
    px = mask.load()
    rows = []
    for y in range(h):
        n = 0
        for x in range(w):
            if px[x, y]:
                n += 1
        rows.append(n)
    out, cur = [], []
    for y, n in enumerate(rows):
        if n:
            cur.append(y)
        elif cur and (y - cur[-1]) > gap:
            out.append((cur[0], cur[-1]))
            cur = []
    if cur:
        out.append((cur[0], cur[-1]))
    res = []
    for y0, y1 in out:
        xs = [x for y in range(y0, y1 + 1) for x in range(w) if px[x, y]]
        if not xs:
            continue
        res.append((top + y0, top + y1, min(xs), max(xs), len(xs)))
    return res


def analyse(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    top = int(h * 0.30)
    m = link_mask(im.crop((0, top, w, h)))
    out = []
    for y0, y1, x0, x1, n in groups(m, top):
        bw = x1 - x0 + 1
        bh = y1 - y0 + 1
        fill = n / float(bw * bh)
        out.append(dict(y0=y0, y1=y1, x0=x0, x1=x1, n=n, fill=round(fill, 3),
                        w=bw, h=bh, fromBottom=h - y1))
    return im.size, out


if __name__ == '__main__':
    files = []
    for d in ('out_gz', 'out'):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith('.png')]
    for f in files:
        rel = os.path.relpath(f, ROOT)
        size, gs = analyse(f)
        print('== %-56s %s' % (rel, size))
        for g in gs:
            print('     y=%5d..%-5d x=%4d..%-4d w=%4d h=%3d fill=%.3f bottom=%4d n=%d'
                  % (g['y0'], g['y1'], g['x0'], g['x1'], g['w'], g['h'], g['fill'], g['fromBottom'], g['n']))
