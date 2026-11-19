"""b21c_textbox.py - private: bounding box of bright (white) pixels inside a region.

Usage: py -3.14 b21c_textbox.py <id> <t> <x0> <y0> <x1> <y1> [thr]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid, t = sys.argv[1], float(sys.argv[2])
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
thr = int(sys.argv[7]) if len(sys.argv) > 7 else 200

tmp = 'frames/b21c_%s/_tb.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)
reg = a[y0:y1, x0:x1]
mask = reg.min(axis=2) > thr
ys, xs = np.where(mask)
if len(ys) == 0:
    print('no bright pixels')
else:
    print('bright bbox: x %d..%d  y %d..%d' % (xs.min() + x0, xs.max() + x0,
                                               ys.min() + y0, ys.max() + y0))
    rows = np.where(mask.sum(axis=1) > 0)[0]
    groups = []
    s = p = rows[0]
    for y in rows[1:]:
        if y - p > 4:
            groups.append((s + y0, p + y0))
            s = y
        p = y
    groups.append((s + y0, p + y0))
    print('text row groups:', groups)
