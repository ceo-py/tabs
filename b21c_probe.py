"""b21c_probe.py - private geometry probe: measure panels in a video frame.

Usage:
  py -3.14 b21c_probe.py <id> <t> [mode]
modes:
  whitebox  - find near-white rectangular regions (fret-diagram boxes)
  blueband  - find dark-blue band rows (chord/lyric banners)
  rows      - dump per-row stats for a column range
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid = sys.argv[1]
t = float(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else 'whitebox'

tmp = 'frames/b21c_%s/_probe.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
im = Image.open(tmp).convert('RGB')
a = np.asarray(im).astype(int)
H, W, _ = a.shape
print('frame', W, H, 't=', t)

if mode == 'whitebox':
    mask = (a[:, :, 0] > 225) & (a[:, :, 1] > 225) & (a[:, :, 2] > 225)
    # column profile on the right half
    cols = mask.sum(axis=0)
    xs = [x for x in range(W) if cols[x] > 40]
    if xs:
        # contiguous groups
        groups = []
        s = xs[0]
        p = xs[0]
        for x in xs[1:]:
            if x - p > 5:
                groups.append((s, p))
                s = x
            p = x
        groups.append((s, p))
        print('white column groups:', groups)
        for g in groups:
            sub = mask[:, g[0]:g[1] + 1]
            rows = np.where(sub.sum(axis=1) > 20)[0]
            if len(rows):
                print('  x %d..%d  y %d..%d' % (g[0], g[1], rows.min(), rows.max()))
    else:
        print('no white box found')

elif mode == 'blueband':
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    blue = (b > 60) & (b < 190) & (r < 60) & (g < 60)
    rowsum = blue.sum(axis=1)
    for y in range(H):
        if rowsum[y] > 50:
            print('row', y, 'count', rowsum[y])
    # for the strongest row band, find x extent
    ys = [y for y in range(H) if rowsum[y] > 200]
    if ys:
        x = np.where(blue[ys[0]:ys[-1] + 1].sum(axis=0) > 5)[0]
        print('band rows %d..%d x %d..%d' % (ys[0], ys[-1], x.min(), x.max()))
    else:
        # find any blue pixels
        ys = np.where(rowsum > 5)[0]
        print('weak blue rows', ys[:5], ys[-5:] if len(ys) else None)

elif mode == 'rows':
    x0, x1 = int(sys.argv[4]), int(sys.argv[5])
    sub = a[:, x0:x1]
    for y in range(H):
        px = sub[y]
        print(y, px.mean(axis=0).round(1), px.min(axis=0), px.max(axis=0))
