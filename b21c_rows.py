"""b21c_rows.py - private: row profile of non-white content in a frame region.

Usage: py -3.14 b21c_rows.py <id> <t> [x0] [y0] [x1] [y1]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid, t = sys.argv[1], float(sys.argv[2])
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7]) if len(sys.argv) > 6 else (0, 0, 1920, 1080)

tmp = 'frames/b21c_%s/_rows.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)
reg = a[y0:y1, x0:x1]
dark = reg.mean(axis=2) < 200
rows = np.where(dark.sum(axis=1) > 0)[0]
print('dark rows (abs y):', (rows.min() + y0, rows.max() + y0) if len(rows) else None)
# print contiguous row groups
if len(rows):
    s = p = rows[0]
    for y in rows[1:]:
        if y - p > 3:
            print('  group y %d..%d' % (s + y0, p + y0))
            s = y
        p = y
    print('  group y %d..%d' % (s + y0, p + y0))
cols = np.where(dark.sum(axis=0) > 0)[0]
print('dark cols (abs x):', (cols.min() + x0, cols.max() + x0) if len(cols) else None)
