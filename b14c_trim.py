"""b14c_trim.py - report the drawn-content bbox inside a panel PNG.

Usage: py -3.14 b14c_trim.py <png> [bg r g b]
Prints x0,y0,x1,y1 of the non-background content and the offsets relative
to the panel origin (so a tighter crop bbox can be derived).
"""
import sys

import numpy as np
from PIL import Image


def main():
    p = sys.argv[1]
    im = Image.open(p).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 235) & (g > 235) & (b > 235)
    ink = ~bg
    # ignore the red header band (rows that are >50% saturated red)
    red = (r > 110) & (g < 100) & (b < 100)
    redrows = red.sum(axis=1) > 0.5 * im.size[0]
    ink[redrows, :] = False
    cols = np.where(ink.sum(axis=0) > 4)[0]
    rows = np.where(ink.sum(axis=1) > 4)[0]
    if len(cols) == 0 or len(rows) == 0:
        print('EMPTY')
        return
    print('png size', im.size)
    print('content x %d..%d  y %d..%d' % (cols[0], cols[-1], rows[0], rows[-1]))
    print('content bottom offset from panel top: %d' % rows[-1])


if __name__ == '__main__':
    main()
