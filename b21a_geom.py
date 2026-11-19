"""b21a_geom.py - private helper (namespace b21a): print the row structure of
a video frame so the TAB strip / caption band can be measured exactly.

Usage:
  py -3.14 b21a_geom.py <id> <t> [--full]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid, t = sys.argv[1], float(sys.argv[2])
    full = '--full' in sys.argv
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_geom_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    H, W = a.shape[:2]
    print('frame %dx%d  t=%.3f' % (W, H, t))
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    white = (mn > 225)
    black = (mx < 40)
    color = ((mx - mn) > 40)
    rows = []
    for y in range(H):
        rows.append((float(a[y].mean()), int(white[y].sum()),
                     int(black[y].sum()), int(color[y].sum())))
    if full:
        for y, r in enumerate(rows):
            print('y=%4d mean=%6.1f white=%4d black=%4d color=%4d' % (y, r[0], r[1], r[2], r[3]))
        return
    # segment the frame into bands of similar character
    def sig(r):
        mean, w, b, c = r
        if c > 600:
            return 'VIDEO(colour)'
        if w > 1000:
            return 'WHITE'
        if b > 1000:
            return 'BLACK'
        if mean > 235:
            return 'light'
        if mean < 60:
            return 'dark'
        return 'mid'
    prev = None
    start = 0
    for y, r in enumerate(rows):
        s = sig(r)
        if s != prev:
            if prev is not None:
                print('%5d..%5d  %s' % (start, y - 1, prev))
            prev = s
            start = y
    print('%5d..%5d  %s' % (start, H - 1, prev))


if __name__ == '__main__':
    main()
