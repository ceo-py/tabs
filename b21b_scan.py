"""b21b_scan.py - private helper (namespace b21b): find the white notation
band(s) in a video frame and report their exact pixel geometry.

Usage:
  py -3.14 b21b_scan.py <id> <t0> <t1> <step> [more t ...]
    -> for every timestamp: white bands (y0,y1) + dark-ink profile of the
       band, so panels can be measured instead of guessed.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def frame(vid, t, tmp):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t,
                    '-i', 'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
                   check=True, capture_output=True)
    return np.asarray(Image.open(tmp).convert('L')).astype(np.float32)


def bands(a, thr=0.5, minlen=40):
    white = (a > 235).mean(axis=1)
    out = []
    run = None
    for y in range(a.shape[0]):
        if white[y] > thr:
            if run is None:
                run = [y, y]
            else:
                run[1] = y
        else:
            if run is not None:
                if run[1] - run[0] + 1 >= minlen:
                    out.append(tuple(run))
                run = None
    if run is not None and run[1] - run[0] + 1 >= minlen:
        out.append(tuple(run))
    return out, white


def main():
    vid = sys.argv[1]
    ts = []
    if len(sys.argv) > 4:
        a = float(sys.argv[2]); b = float(sys.argv[3]); step = float(sys.argv[4])
        t = a
        while t <= b:
            ts.append(round(t, 2))
            t += step
    ts += [float(x) for x in sys.argv[5:]]
    base = 'frames/b21b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_scan_tmp.png')
    for t in ts:
        a = frame(vid, t, tmp)
        h, w = a.shape
        bs, white = bands(a)
        if not bs:
            print('t=%-7s  NO BAND  (mean=%.1f)' % (t, a.mean()))
            continue
        y0, y1 = bs[0]
        y0, y1 = bs[-1] if len(bs) == 1 else bs[0]
        sub = a[y0:y1 + 1]
        ink = (sub < 120).mean(axis=0)
        # report left-most 700 px ink density per 50 px bucket (section labels
        # live at the very left of the band)
        head = ['%3d' % (ink[i:i + 50].mean() * 100)
                for i in range(0, 700, 50)]
        print('t=%-7s size=%dx%d bands=%s  band=%d..%d  inkhead=%s'
              % (t, w, h, bs, y0, y1, ' '.join(head)))


if __name__ == '__main__':
    main()
