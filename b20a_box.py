"""b20a_box.py - private helper (batch b20a): find the bright notation strips
of a frame and print ready-to-use crop boxes (x=0, full width, even height).

Usage: py -3.14 b20a_box.py <id> <t> [t2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_box_tmp.png')
    for a in sys.argv[2:]:
        t = float(a)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        arr = np.asarray(Image.open(tmp).convert('L')).astype(np.float32)
        means = arr.mean(axis=1)
        bright = means > 190
        runs = []
        s = None
        for y in range(arr.shape[0]):
            if bright[y] and s is None:
                s = y
            elif not bright[y] and s is not None:
                runs.append((s, y - 1))
                s = None
        if s is not None:
            runs.append((s, arr.shape[0] - 1))
        out = []
        for (s, e) in runs:
            if e - s < 20:
                continue
            h = e - s + 1
            if h % 2:
                e += 1
                h = e - s + 1
            out.append('[0, %d, 1920, %d]' % (s, h))
        print('t=%-7s %s' % (t, '  '.join(out)))


if __name__ == '__main__':
    main()
