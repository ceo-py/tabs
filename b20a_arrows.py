"""b20a_arrows.py - private helper (batch b20a): locate strum arrows in the
chord panel.  Prints the row-darkness profile of a band and the x positions of
up-arrow heads (clean band above the staff).

Usage:
  py -3.14 b20a_arrows.py <id> <t> <y0> <y1> [x0] [x1]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def clusters(cols, gap=6):
    out = []
    for c in cols:
        if out and c - out[-1][-1] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return [int(round(sum(g) / len(g))) for g in out]


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    y0, y1 = int(sys.argv[3]), int(sys.argv[4])
    x0 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    x1 = int(sys.argv[6]) if len(sys.argv) > 6 else 1920
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_arrows_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (x1 - x0, y1 - y0, x0, y0),
                    tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('L')).astype(np.int16)
    print('== row profile (y: darkcount) for y %d..%d' % (y0, y1))
    for i, row in enumerate(a):
        print('  y=%d dark=%d' % (y0 + i, int((row < 120).sum())))
    for lo, hi, tag in ((936, 952, 'UP-heads'), (1040, 1051, 'DOWN-heads')):
        if lo < y0 or hi > y1:
            continue
        band = a[lo - y0:hi - y0]
        cols = np.where((band < 120).sum(axis=0) >= 3)[0] + x0
        print('== %s  x=%s' % (tag, clusters(list(cols), gap=8)))


if __name__ == '__main__':
    main()
