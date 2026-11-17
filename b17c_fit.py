"""b17c_fit.py - tighten a crop box to the content that is really on screen.

For the white tab sheets the lower part of the sheet is empty.  This finds the
last row (and last column) that still carries ink, so the crop can stop there.

Usage: py -3.14 b17c_fit.py <video> <t> <x> <y> <w> <h>
"""
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video, t = sys.argv[1], float(sys.argv[2])
    x0, y0, w, h = (int(v) for v in sys.argv[3:7])
    tmp = 'frames/b17c_fit_tmp.png'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    sub = a[y0:y0 + h, x0:x0 + w]
    lum = sub.max(axis=2)
    ink = lum < 235                     # anything darker than paper
    rows = np.where(ink.sum(axis=1) > 3)[0]
    cols = np.where(ink.sum(axis=0) > 3)[0]
    if not len(rows):
        print('no ink')
        return
    r1 = rows[-1]
    c1 = cols[-1]
    print('video=%s t=%g' % (video, t))
    print('  content rows %d..%d (of %d..%d), cols %d..%d (of %d..%d)' % (
        y0 + rows[0], y0 + r1, y0, y0 + h - 1,
        x0 + cols[0], x0 + c1, x0, x0 + w - 1))
    print('  tight = [%d, %d, %d, %d]' % (x0, y0, w, min(h, r1 + 12)))


if __name__ == '__main__':
    main()
