"""b17c_bbox.py - find the tight bounding box of bright (text) pixels.

Used for the black "chord pattern & strumming" overlays, where the text block
has to be cropped exactly.

Usage: py -3.14 b17c_bbox.py <video> <t> <x> <y> <w> <h>
"""
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video, t = sys.argv[1], float(sys.argv[2])
    x0, y0, w, h = (int(v) for v in sys.argv[3:7])
    tmp = 'frames/b17c_bbox_tmp.png'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], capture_output=True)
    im = Image.open(tmp).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    sub = a[y0:y0 + h, x0:x0 + w]
    lum = sub.max(axis=2)
    red = (sub[..., 0] > 110) & (sub[..., 1] < 110) & (sub[..., 2] < 110)
    mask = (lum > 90) | red
    rows = np.where(mask.sum(axis=1) > 2)[0]
    cols = np.where(mask.sum(axis=0) > 2)[0]
    if not len(rows) or not len(cols):
        print('nothing')
        return
    # report the row bands so separate text blocks can be picked
    bands = []
    for r in rows:
        if bands and r == bands[-1][1] + 1:
            bands[-1][1] = r
        else:
            bands.append([r, r])
    print('video=%s t=%g  search=[%d,%d,%d,%d]' % (video, t, x0, y0, w, h))
    print('  tight bbox = [%d, %d, %d, %d]' % (
        x0 + cols[0], y0 + rows[0], cols[-1] - cols[0] + 1, rows[-1] - rows[0] + 1))
    for b in bands:
        if b[1] - b[0] < 2:
            continue
        sub2 = mask[b[0]:b[1] + 1]
        c = np.where(sub2.sum(axis=0) > 0)[0]
        print('    band y %d..%d  x %d..%d' % (y0 + b[0], y0 + b[1],
                                              x0 + c[0], x0 + c[-1]))


if __name__ == '__main__':
    main()
