"""b18b_fit.py - measure the bottom of the printed content of a panel.

For every timestamp it looks at the white sheet under the red title bar and
finds the last row that still carries ink (dark text / staff lines), so the
card crop can stop there instead of padding the panel with blank white.

Usage: py -3.14 b18b_fit.py <video> <id> <x0> <t1> <t2> ...
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video, vid = sys.argv[1], sys.argv[2]
    x0 = int(sys.argv[3])
    y0 = int(sys.argv[4])
    ts = [float(a) for a in sys.argv[5:]]
    base = 'frames/b18b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = base + '/_fit.png'
    for t in ts:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (1920 - x0, 1080 - 624, x0, 624),
               tmp]
        subprocess.run(cmd, check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('L')).astype(np.int16)
        ink = (a < 235).sum(axis=1)
        rows = [i for i, v in enumerate(ink) if v >= 3]
        if not rows:
            print('t=%g  EMPTY' % t)
            continue
        bot = 624 + rows[-1] + 1
        # 25 px of breathing room under the last line of ink
        h = min(1080 - y0, bot + 25 - y0)
        print('t=%g  bbox=[%d, %d, %d, %d]   ink_bottom=%d' % (t, x0, y0, 1920 - x0, h, bot))


if __name__ == '__main__':
    main()
