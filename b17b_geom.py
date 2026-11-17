"""b17b_geom.py - private helper for the Nirvana (b17b) batch.

Measures the on-screen notation area of a single frame:

  * the red section-title bar  -> its exact top/bottom rows
  * the white notation sheet   -> the last row that carries content

and prints the panel bbox to use in the spec:
    [x, bar_top, w, height]   (x = right edge of the wooden fretboard)

Usage: py -3.14 b17b_geom.py <video> <t> [<t> ...]
"""
import subprocess
import sys

import numpy as np
from PIL import Image


def bands(flags, min_run=2):
    out, start = [], None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_run:
                out.append((start, i - 1))
            start = None
    if start is not None and len(flags) - start >= min_run:
        out.append((start, len(flags) - 1))
    return out


def main():
    video = sys.argv[1]
    for t in sys.argv[2:]:
        tmp = 'frames/b17b_probe/_g.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 110) & (g < 95) & (b < 95)
        W, H = im.size
        xoff = 250
        cnt = red[:, xoff:].sum(axis=1)
        cands = [(y0, y1) for y0, y1 in bands(cnt > 0.5 * (W - xoff), 2)]
        if cands:
            by0, by1 = max(cands, key=lambda c: cnt[c[0]:c[1] + 1].max())
        else:
            by0 = by1 = None
        # last row carrying non-white content below the bar
        bot = H - 1
        if by1 is not None:
            sub = a[by1 + 1:, xoff:]
            dark = ((sub.max(axis=2) < 235).sum(axis=1) > 2)
            rows = bands(dark, 1)
            if rows:
                bot = by1 + rows[-1][1] + 1
        # left edge: where the wooden fretboard ends
        wood = ((r > 150) & (g > 120) & (b > 80) & (b < 220)).sum(axis=0)
        xs = [x for x in range(0, 400) if wood[x] > 300]
        xleft = (max(xs) + 1) if xs else 248
        print('t=%s  bar=%s..%s  content_bottom=%d  fretboard_right=%d  '
              'BBOX=[%d, %d, %d, %d]'
              % (t, by0, by1, bot, xleft, xleft, by0, W - xleft, bot - by0))


if __name__ == '__main__':
    main()
