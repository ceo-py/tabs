"""b21c_probe2.py - private geometry probe #2: rectangular white box in a region.

Usage:
  py -3.14 b21c_probe2.py <id> <t> <x0> <y0> <x1> <y1>
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid, t = sys.argv[1], float(sys.argv[2])
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]

tmp = 'frames/b21c_%s/_probe2.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)

reg = a[y0:y1, x0:x1]
mask = (reg[:, :, 0] > 225) & (reg[:, :, 1] > 225) & (reg[:, :, 2] > 225)
rows = np.where(mask.sum(axis=1) > 30)[0]
cols = np.where(mask.sum(axis=0) > 30)[0]
print('region rows(y):', (rows.min() + y0, rows.max() + y0) if len(rows) else None)
print('region cols(x):', (cols.min() + x0, cols.max() + x0) if len(cols) else None)
# per-row white counts near edges to find box borders
for y in range(y0, min(y1, y0 + 420)):
    c = mask[y - y0].sum()
    if c > 0:
        xs = np.where(mask[y - y0])[0]
        print('y=%d white=%d x %d..%d' % (y, c, xs.min() + x0, xs.max() + x0))
