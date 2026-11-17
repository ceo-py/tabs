"""b17c_geom.py - measure the exact edges of the bottom-sheet panel.

For a layout-A video it reports (full-res pixels):
  * the first and last row of the wide red section bar
  * the leftmost column of the red bar
  * the rightmost column of the wooden fretboard next to it

Usage: py -3.14 b17c_geom.py <video> <t>
"""
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video, t = sys.argv[1], float(sys.argv[2])
    tmp = 'frames/b17c_geom_tmp.png'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 200) & (g > 200) & (b > 200)
    H, W = red.shape
    rows = red[:, 300:].sum(axis=1)
    hit = [y for y in range(H) if rows[y] > 0.5 * (W - 300)]
    # group
    bands = []
    for y in hit:
        if bands and y == bands[-1][1] + 1:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    bands = [bb for bb in bands if bb[1] - bb[0] > 15]
    print('video=%s t=%g size=%dx%d' % (video, t, W, H))
    for bb in bands:
        y0, y1 = bb
        sub = red[y0:y1 + 1]
        cols = [x for x in range(W) if sub[:, x].mean() > 0.8]
        if not cols:
            cols = [x for x in range(W) if sub[:, x].mean() > 0.5]
        print('  red bar rows %d..%d  cols %d..%d' % (y0, y1, cols[0], cols[-1]))
        # what is immediately left of the bar?
        for dx in (-2, -6, -12, -30):
            x = cols[0] + dx
            if x >= 0:
                print('     col %d rgb=%s' % (x, tuple(a[y0 + 5, x])))
    print('  sheet left edge:')
    for y in range(H):
        if white[y, 300:1900].mean() > 0.6:
            yy = y
            break
    col = None
    for x in range(0, 500):
        if white[yy + 5:min(H, yy + 400), x].mean() > 0.8:
            col = x
            break
    print('     sheet left column=%s (row %d)' % (col, yy))


if __name__ == '__main__':
    main()
