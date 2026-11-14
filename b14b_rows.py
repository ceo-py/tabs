"""b14b_rows.py - private helper: report the horizontal ink bands of a region.

Prints the y ranges of rows that contain ink, so a chord-name line or a
strumming line can be cropped exactly.

Usage:
    py -3.14 b14b_rows.py <png> [--x0 a] [--x1 b] [--y0 a] [--y1 b] [--thr 200]
"""
import sys

import numpy as np
from PIL import Image


def main():
    p = sys.argv[1]
    x0 = x1 = y0 = y1 = None
    thr = 200
    a = sys.argv[2:]
    i = 0
    while i < len(a):
        if a[i] == '--x0':
            x0 = int(a[i + 1]); i += 2
        elif a[i] == '--x1':
            x1 = int(a[i + 1]); i += 2
        elif a[i] == '--y0':
            y0 = int(a[i + 1]); i += 2
        elif a[i] == '--y1':
            y1 = int(a[i + 1]); i += 2
        elif a[i] == '--thr':
            thr = int(a[i + 1]); i += 2
        else:
            i += 1
    im = Image.open(p).convert('RGB')
    W, H = im.size
    x0 = 0 if x0 is None else x0
    x1 = W if x1 is None else x1
    y0 = 0 if y0 is None else y0
    y1 = H if y1 is None else y1
    arr = np.asarray(im.crop((x0, y0, x1, y1))).astype(np.int16)
    ink = arr.min(axis=2) < thr
    rows = ink.sum(axis=1)
    print('%s size=%s region x=%d-%d y=%d-%d thr=%d' % (p, im.size, x0, x1, y0, y1, thr))
    bands = []
    start = None
    for i, v in enumerate(rows):
        if v > 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            bands.append((start + y0, i - 1 + y0))
            start = None
    if start is not None:
        bands.append((start + y0, len(rows) - 1 + y0))
    for b in bands:
        print('   y %d-%d  (h=%d)  inkmax=%d' % (b[0], b[1], b[1] - b[0] + 1,
                                                 rows[b[0] - y0:b[1] - y0 + 1].max()))


if __name__ == '__main__':
    main()
