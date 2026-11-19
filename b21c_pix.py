"""b21c_pix.py - private: print pixel colours along a column/row of a frame.

Usage: py -3.14 b21c_pix.py <id> <t> col <x> <y0> <y1>
       py -3.14 b21c_pix.py <id> <t> row <y> <x0> <x1>
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid, t = sys.argv[1], float(sys.argv[2])
tmp = 'frames/b21c_%s/_pix.png' % vid
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
               check=True, capture_output=True)
a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)

if sys.argv[3] == 'col':
    x, y0, y1 = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    for y in range(y0, y1):
        print(y, a[y, x])
else:
    y, x0, x1 = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    for x in range(x0, x1):
        print(x, a[y, x])
