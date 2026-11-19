"""b20a_probe.py - private helper (batch b20a): find the horizontal white
notation bands (TAB strips) in a video frame.

Usage:
  py -3.14 b20a_probe.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def bands(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im).astype(np.float32)
    # "white" rows: most pixels of the row are near-white
    white = (a > 235).mean(axis=1)
    dark = (a < 90).mean(axis=1)
    out = []
    run = None
    for y in range(a.shape[0]):
        if white[y] > 0.55:
            if run is None:
                run = [y, y]
            else:
                run[1] = y
        else:
            if run is not None:
                out.append(tuple(run))
                run = None
    if run is not None:
        out.append(tuple(run))
    return out, white, dark


def main():
    vid = sys.argv[1]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_probe_tmp.png')
    for a in sys.argv[2:]:
        t = float(a)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        b, white, dark = bands(tmp)
        print('t=%-7s size=%s  whitebands=%s' % (t, Image.open(tmp).size, b))


if __name__ == '__main__':
    main()
