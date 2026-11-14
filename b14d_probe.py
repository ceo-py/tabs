"""b14d_probe.py - private helper for the b14 batch (John Mayer videos).

Reports, for a given frame of a video, the geometry of the on-screen notation
overlay:

  * the white notation sheet (the TAB / chord table)
  * the red section-label bar (horizontal header or vertical strip)

Used for the layout-B videos (vertical red label) where the generic survey
gets the box wrong.

Usage: py -3.14 b14d_probe.py <video> <t> [t ...]
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
        p = os.path.join(OUT, '_p.png')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', p], check=True, capture_output=True)
        a = np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
        H, W = a.shape[:2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        white = (r > 205) & (g > 205) & (b > 205)
        red = (r > 120) & (g < 95) & (b < 95)
        # white sheet: rows/cols with many white pixels, ignoring the top-left
        # fretboard diagram (x < 300)
        sub = white[:, 300:]
        rows = np.flatnonzero(sub.sum(axis=1) > 0.2 * (W - 300))
        cols = np.flatnonzero(sub.sum(axis=0) > 0.2 * max(1, len(rows)))
        sheet = None
        if len(rows) and len(cols):
            sheet = [int(cols.min()) + 300, int(rows.min()),
                     int(cols.max()) + 300, int(rows.max())]
        # red bar
        rc = np.flatnonzero(red.sum(axis=0) > 0.25 * H)
        rr = np.flatnonzero(red.sum(axis=1) > 0.25 * W)
        bar = None
        if len(rc) and len(rr):
            bar = [int(rc.min()), int(rr.min()), int(rc.max()), int(rr.max())]
        print('t=%.1f  sheet=%s  redbar=%s' % (t, sheet, bar))


if __name__ == '__main__':
    main()
