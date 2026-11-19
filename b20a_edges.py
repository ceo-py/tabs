"""b20a_edges.py - private helper (batch b20a): list the dark->bright row
transitions of a video frame (the edges of the notation panels).

Usage: py -3.14 b20a_edges.py <id> <t> [t2 ...]
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
    tmp = os.path.join(base, '_edges_tmp.png')
    for a in sys.argv[2:]:
        t = float(a)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        arr = np.asarray(Image.open(tmp).convert('L')).astype(np.float32)
        means = arr.mean(axis=1)
        bright = means > 190
        trans = []
        for y in range(1, arr.shape[0]):
            if bright[y] != bright[y - 1]:
                trans.append((y, 'bright' if bright[y] else 'dark'))
        print('t=%-7s transitions: %s' % (t, trans))


if __name__ == '__main__':
    main()
