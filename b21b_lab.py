"""b21b_lab.py - private helper (namespace b21b): find the section-label row of
the TAB strip (the "[X] Name" text that sits at the top-left of the strip) and
report when it is on screen.

Usage:
  py -3.14 b21b_lab.py <id> <band_top> <t0> <t1> <step> [x0 x1]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    top = int(sys.argv[2])
    a = float(sys.argv[3]); b = float(sys.argv[4]); step = float(sys.argv[5])
    x0, x1 = (0, 700)
    if len(sys.argv) > 7:
        x0, x1 = int(sys.argv[6]), int(sys.argv[7])
    base = 'frames/b21b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_lab_tmp.png')
    t = a
    while t <= b:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t,
                        '-i', 'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
                       check=True, capture_output=True)
        a2 = np.asarray(Image.open(tmp).convert('L')).astype(np.float32)
        reg = a2[top + 18:top + 62, x0:x1]
        dark = (reg < 120).sum()
        cols = (reg < 120).sum(axis=0)
        # left-most column with ink
        first = int(np.argmax(cols > 0)) if (cols > 0).any() else -1
        print('t=%-7s ink=%-6d firstx=%d' % (t, dark, first + x0))
        t += step


if __name__ == '__main__':
    main()
