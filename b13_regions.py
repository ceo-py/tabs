"""b13_regions.py - print every large white / red region of a frame with its
fill ratio (source pixels).  Diagnostic helper used to design the crop boxes.

Usage: py -3.14 b13_regions.py <frame.png>
"""
import sys

import numpy as np
from PIL import Image, ImageFilter


def bands(flags, min_run=1):
    out, start = [], None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_run:
                out.append((start, i - 1))
            start = None
    if start is not None and len(flags) - start >= min_run:
        out.append((start, len(flags) - 1))
    return out


def report(path):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 205) & (g > 205) & (b > 205)
    red = (r > 120) & (g < 95) & (b < 95)
    for name, mask, minf in (('WHITE', white, 0.0008), ('RED', red, 0.0004)):
        im2 = Image.fromarray((mask * 255).astype(np.uint8), 'L').filter(ImageFilter.MinFilter(5))
        e = np.asarray(im2) > 0
        orig = mask
        print('--', name)
        for y0, y1 in bands(e.sum(axis=1) > 0, 2):
            sub = e[y0:y1 + 1]
            for x0, x1 in bands(sub.sum(axis=0) > 0, 2):
                area = (y1 - y0 + 1) * (x1 - x0 + 1)
                if area < minf * W * H:
                    continue
                fill = orig[y0:y1 + 1, x0:x1 + 1].mean()
                print('   x=%4d-%4d y=%4d-%4d  area=%7d fill=%.2f' % (x0, x1, y0, y1, area, fill))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('==', p)
        report(p)
