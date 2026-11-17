"""b17a_meas.py - private helper: measure the on-screen graphic boxes of a frame.

Usage: py -3.14 b17a_meas.py <png> [png ...]
Prints the bounding boxes of the saturated-red bars and the bright-white
regions found in each frame, in full-resolution pixel coordinates.
"""
import sys

import numpy as np
from PIL import Image


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
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 200) & (g > 200) & (b > 200)
    print('==', path, im.size)
    print(' red rows:')
    for y0, y1 in bands(red.sum(axis=1) > im.size[0] * 0.08, 3):
        sub = red[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 1)
        print('   y=%d..%d  x=%d..%d' % (y0, y1, cols[0][0], cols[-1][1]))
    print(' white rows:')
    for y0, y1 in bands(white.sum(axis=1) > im.size[0] * 0.20, 3):
        sub = white[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 1)
        print('   y=%d..%d  x=%d..%d' % (y0, y1, cols[0][0], cols[-1][1]))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        report(p)
