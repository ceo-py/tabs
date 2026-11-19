"""b21b_probe.py - private helper (namespace b21b): row/column profile of a video
frame so the panel geometry can be measured by hand.

Usage:
  py -3.14 b21b_probe.py <id> <t> [x]
    -> prints per-row mean luminance, white-fraction and dark-fraction for the
       extracted frame frames/b21b_<id>/_probe_tmp.png
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_probe_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    im = Image.open(tmp).convert('L')
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape
    print('frame size', w, h)
    for y in range(h):
        row = a[y]
        print('%4d  mean=%6.1f  white=%.3f  dark=%.3f  min=%3d max=%3d'
              % (y, row.mean(), (row > 235).mean(), (row < 90).mean(), row.min(), row.max()))


if __name__ == '__main__':
    main()
