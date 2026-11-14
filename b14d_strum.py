"""b14d_strum.py - private helper: read a strumming-pattern row of letters.

The strumming rows of these videos are a row of big letters (D / U / -) on a
white background, with the currently-played glyph printed in black and the
others in light grey.  This helper segments the row into glyphs and classifies
each one:

  '-'   a dash (short horizontal stroke)
  'D'   a capital D (closed bowl, vertical stem on the left, ink at the top)
  'U'   a capital U (open at the top, ink only at the bottom)

A glyph printed in black (the "highlighted" strum) is marked with '*'.

Usage:
  py -3.14 b14d_strum.py <png> [y0] [y1] [x0] [x1]
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


def classify(sub):
    """sub: boolean ink block of one glyph -> '-', 'D' or 'U'."""
    ys = np.flatnonzero(sub.any(axis=1))
    if not len(ys):
        return '?'
    r0, r1 = ys.min(), ys.max()
    h = r1 - r0 + 1
    w = sub.shape[1]
    blk = sub[r0:r1 + 1]
    if h < 0.35 * 40 and w < 0.7 * 40:
        return '-'                      # a dash: short and wide
    top = blk[:max(1, int(h * 0.25))]
    # 'D' closes its bowl at the top -> the horizontal middle of the top band
    # carries ink.  'U' is open at the top -> the middle is empty.
    mid = top[:, int(w * 0.30):int(w * 0.70)]
    return 'D' if mid.mean() >= 0.12 else 'U'


def main():
    p = sys.argv[1]
    im = Image.open(p).convert('L')
    W, H = im.size
    y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    y1 = int(sys.argv[3]) if len(sys.argv) > 3 else H
    x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    x1 = int(sys.argv[5]) if len(sys.argv) > 5 else W
    a = np.asarray(im).astype(np.int16)
    band = a[y0:y1, x0:x1]
    ink = band < 238
    segs = segments(ink)
    out = []
    for (c0, c1) in segs:
        if c1 - c0 + 1 < 5:
            continue                     # panel border artefact
        sub = ink[:, c0:c1 + 1]
        ch = classify(sub)
        dark = band[:, c0:c1 + 1].min() < 120
        out.append((ch, dark))
    print('%s  glyphs=%d' % (p, len(out)))
    print('  pattern : %s' % ' '.join(c for c, _ in out))
    print('  compact : %s' % ''.join(c for c, _ in out))
    print('  dark    : %s' % ' '.join(str(i) for i, (c, d) in enumerate(out) if d))
    print('  segs    : %s' % segs)


if __name__ == '__main__':
    main()
