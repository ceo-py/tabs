"""b18d_fit.py - private helper for the b18d batch.

Prints a tightened crop box for a video frame: the given search box is
cropped, then the white margins are trimmed so the card panel contains only
the section bar + the notation (no big empty white area, no black bars).

Usage: py -3.14 b18d_fit.py <video> <id> <t> <x> <y> <w> <h>
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    t = float(sys.argv[3])
    x, y, w, h = (int(v) for v in sys.argv[4:8])
    base = 'frames/b18d_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = base + '/_fit.png'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print('FAIL')
        return
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    # content = anything that is not near-white
    ink = ~((a[..., 0] > 244) & (a[..., 1] > 244) & (a[..., 2] > 244))
    rows = np.where(ink.sum(axis=1) > 2)[0]
    cols = np.where(ink.sum(axis=0) > 2)[0]
    if rows.size == 0 or cols.size == 0:
        print('EMPTY')
        return
    top = max(0, rows[0] - 4)
    bot = min(h - 1, rows[-1] + 6)
    left = max(0, cols[0] - 6)
    right = min(w - 1, cols[-1] + 7)
    print('[%d, %d, %d, %d]  (from [%d, %d, %d, %d])'
          % (x + left, y + top, right - left + 1, bot - top + 1, x, y, w, h))


if __name__ == '__main__':
    main()
