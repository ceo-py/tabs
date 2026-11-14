"""b14d_glyph.py - private helper: dump the glyphs of a strumming row as ASCII
so the letters can be identified exactly (D / U / dash, dark vs grey).

Usage: py -3.14 b14d_glyph.py <png> [y0] [y1] [x0] [x1]
"""
import sys

import numpy as np
from PIL import Image

from b14d_strum import segments


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
    for i, (c0, c1) in enumerate(segs):
        sub = ink[:, c0:c1 + 1]
        ys = np.flatnonzero(sub.any(axis=1))
        if not len(ys):
            continue
        r0, r1 = ys.min(), ys.max()
        blk = sub[r0:r1 + 1]
        step = max(1, blk.shape[1] // 18)
        print('glyph %d  x=%d..%d w=%d h=%d  min=%d'
              % (i, c0, c1, c1 - c0 + 1, r1 - r0 + 1, band[:, c0:c1 + 1].min()))
        for r in range(blk.shape[0]):
            print('   ' + ''.join('#' if blk[r, c] else '.'
                                  for c in range(0, blk.shape[1], step)))


if __name__ == '__main__':
    main()
