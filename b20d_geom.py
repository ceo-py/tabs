"""b20d_geom.py - private helper (batch b20d): measure the geometry of the
printed TAB page inside a video frame.

For the Sparky Guitar videos the TAB is a white / cream printed strip that
sits inside one of the camera panels.  This script takes a frame, looks at a
column window and reports for every row how many pixels of that row are
"paper" (bright and almost colourless).  The rows with a long run of paper
are the TAB page.

Usage:
  py -3.14 b20d_geom.py <id> <t> [x0] [x1]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    x0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    x1 = int(sys.argv[4]) if len(sys.argv) > 4 else 1920
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20d_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_geom_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    win = a[:, x0:x1]
    mx = win.max(axis=2)
    mn = win.min(axis=2)
    paper = (mx > 205) & ((mx - mn) <= 18)
    rows = paper.sum(axis=1)
    thr = (x1 - x0) * 0.45
    print('%s t=%s window x=%d..%d  paper_thr=%d' % (vid, t, x0, x1, thr))
    run = None
    for y in range(a.shape[0]):
        if rows[y] >= thr and run is None:
            run = y
        elif rows[y] < thr and run is not None:
            print('  paper rows %4d..%4d  (h=%d)  peak=%d' % (run, y - 1, y - run, int(rows[run:y].max())))
            run = None
    if run is not None:
        print('  paper rows %4d..%4d  (h=%d)' % (run, a.shape[0] - 1, a.shape[0] - run))
    print('  row profile (every 4 rows, y:count):')
    for y in range(0, a.shape[0], 4):
        print('    %4d %5d' % (y, int(rows[y])))


if __name__ == '__main__':
    main()
