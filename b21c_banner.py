"""b21c_banner.py - private: locate the exact navy banner rectangles (0,0,127).

Usage: py -3.14 b21c_banner.py <id> <t>
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid, t = sys.argv[1], float(sys.argv[2])
tmp = 'frames/b21c_%s/_bn.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
navy = (np.abs(r) < 30) & (np.abs(g) < 30) & (np.abs(b - 127) < 30)
rows = navy.sum(axis=1)
H = a.shape[0]
ys = [y for y in range(H) if rows[y] > 40]
if ys:
    s = p = ys[0]
    groups = []
    for y in ys[1:]:
        if y - p > 4:
            groups.append((s, p))
            s = y
        p = y
    groups.append((s, p))
    for (y0, y1) in groups:
        xs = np.where(navy[y0:y1 + 1].sum(axis=0) > (y1 - y0) * 0.4)[0]
        print('navy band y %d..%d (h=%d) x %d..%d (w=%d)' %
              (y0, y1, y1 - y0 + 1, xs.min(), xs.max(), xs.max() - xs.min() + 1))
else:
    print('no navy banner')
