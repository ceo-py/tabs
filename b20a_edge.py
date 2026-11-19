"""b20a_edge.py - private helper (batch b20a): print the mean brightness of
every row in a y-range, so the exact edge of a notation panel can be found.

Usage: py -3.14 b20a_edge.py <id> <t> <y0> <y1> [x0] [x1]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    y0, y1 = int(sys.argv[3]), int(sys.argv[4])
    x0 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    x1 = int(sys.argv[6]) if len(sys.argv) > 6 else 1920
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_edge_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('L')).astype(np.float32)
    for y in range(y0, y1):
        row = a[y, x0:x1]
        print('y=%4d mean=%6.1f  p05=%5.1f p95=%5.1f' % (
            y, row.mean(), np.percentile(row, 5), np.percentile(row, 95)))


if __name__ == '__main__':
    main()
