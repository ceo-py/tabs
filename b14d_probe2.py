"""b14d_probe2.py - private helper: precise geometry of the layout-B notation
overlay (white sheet + vertical red label) used by the b14 John Mayer batch.

For every requested timestamp it prints
  * the red label bar box
  * the white notation sheet box (longest horizontal white run in the panel
    row band, plus the vertical extent of that run)

Usage: py -3.14 b14d_probe2.py <video> <t> [t ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

OUT = 'frames/b14d_probe'


def main():
    video = sys.argv[1]
    times = [float(x) for x in sys.argv[2:]]
    os.makedirs(OUT, exist_ok=True)
    for t in times:
        p = os.path.join(OUT, '_p2.png')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', p], check=True, capture_output=True)
        a = np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
        H, W = a.shape[:2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 120) & (g > 30) & (g < 80) & (b > 35) & (b < 85)
        rc = np.flatnonzero(red.sum(axis=0) > 0.08 * H)
        rr = np.flatnonzero(red.sum(axis=1) > 0.03 * W)
        bar = ([int(rc.min()), int(rr.min()), int(rc.max()) + 1, int(rr.max()) + 1]
               if len(rc) and len(rr) else None)
        white = (r > 200) & (g > 200) & (b > 200)
        # row band = the vertical middle of the sheet (skip the title text
        # at the very top and the shirt at the bottom)
        y0 = int(0.22 * H)
        y1 = int(0.36 * H)
        band = white[y0:y1]
        colhits = band.sum(axis=0)
        # longest contiguous run of columns that are mostly white
        best = (0, 0, 0)
        i = 0
        while i < W:
            if colhits[i] > 0.6 * (y1 - y0):
                j = i
                while j < W and colhits[j] > 0.6 * (y1 - y0):
                    j += 1
                if j - i > best[0]:
                    best = (j - i, i, j)
                i = j
            else:
                i += 1
        _, sx0, sx1 = best
        colmask = white[:, sx0:sx1].sum(axis=1)
        rows = np.flatnonzero(colmask > 0.6 * (sx1 - sx0))
        sheet = ([int(sx0), int(rows.min()), int(sx1), int(rows.max()) + 1]
                 if len(rows) else None)
        print('t=%.1f  bar=%s  sheet=%s' % (t, bar, sheet))


if __name__ == '__main__':
    main()
