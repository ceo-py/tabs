"""b13_count.py - private helper: read a strumming-pattern row of letters.

The strumming rows of these videos are a row of big letters (D / U) on a white
background.  Counting them by eye is error prone, so this helper segments the
row into glyphs, groups the glyphs by identical bitmap, and reports the
positions of each distinct shape.  The highlighted (dark) glyph is the one the
video is currently playing, so it identifies that shape.

Usage: py -3.14 b13_count.py <png> <y0> <y1> [x0] [x1]
"""
import sys

import numpy as np
from PIL import Image


def segments(ink):
    cols = ink.sum(axis=0) > 0
    runs = []
    st = None
    for i, v in enumerate(cols):
        if v and st is None:
            st = i
        elif not v and st is not None:
            runs.append((st, i - 1))
            st = None
    if st is not None:
        runs.append((st, len(cols) - 1))
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 2:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    return merged


def main():
    p = sys.argv[1]
    y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    x1 = int(sys.argv[5]) if len(sys.argv) > 5 else None
    im = Image.open(p).convert('L')
    W, H = im.size
    x1 = W if x1 is None else min(x1, W)
    y1 = min(y1, H)
    a = np.asarray(im).astype(np.int16)
    band = a[y0:y1, x0:x1]
    ink = band < 238
    segs = segments(ink)
    # group by shape signature
    groups = {}
    for i, (c0, c1) in enumerate(segs):
        sig = tuple((ink[:, c0:c1 + 1] > 0).astype(np.uint8).flatten())
        groups.setdefault(sig, []).append(i)
    print('%s y=%d-%d  glyphs=%d  distinct_shapes=%d' % (p, y0, y1, len(segs), len(groups)))
    for sig, idxs in groups.items():
        dark = [i for i in idxs
                if a[y0:y1, x0 + segs[i][0]:x0 + segs[i][1] + 1].min() < 120]
        print('   shape at glyph indexes %s%s  (dark/highlighted: %s)'
              % (idxs if len(idxs) <= 40 else str(idxs[:40]) + '...',
                 '' if len(idxs) <= 40 else '',
                 dark))
    # print the row as D/U assuming the glyph shapes alternate (D U D U ...)
    print('   segs:', segs)


if __name__ == '__main__':
    main()
