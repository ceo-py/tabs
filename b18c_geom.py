"""b18c_geom.py - private helper: geometry of the on-screen graphic overlay.

For a given frame it reports the horizontal bands of the red title bar and of
the white sheet, plus the x extent of the sheet, so a crop box can be derived
without eyeballing.

Usage: py -3.14 b18c_geom.py <id> <t> [x0] [x1]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

VIDS = {
    'MmmhEd7j8K8': 'dl/w4_MmmhEd7j8K8.mp4',
    'jmNmAnr_Vr4': 'dl/w4_jmNmAnr_Vr4.mp4',
    'YXHCL2Y-e0U': 'dl/w4_YXHCL2Y-e0U.mp4',
    'mbnmB_hTfiM': 'dl/w4_mbnmB_hTfiM.mp4',
    'LRXRm0eMZZY': 'dl/w4_LRXRm0eMZZY.mp4',
    'JvRLYuiyURk': 'dl/w4_JvRLYuiyURk.mp4',
    '_YrDIC5tZcA': 'dl/w4__YrDIC5tZcA.mp4',
}


def bands(flags, min_run=1):
    out, start = [], None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_run:
                out.append((start, i - 1))
            start = None
    if start is not None and len(flags) - start >= min_run:
        out.append((start, len(flags) - 1))
    return out


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    x0 = int(sys.argv[3]) if len(sys.argv) > 3 else 248
    x1 = int(sys.argv[4]) if len(sys.argv) > 4 else 1920
    video = VIDS[vid]
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_geom_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 90) & (b < 90)
    white = (r > 205) & (g > 205) & (b > 205)
    band = slice(x0, x1)
    print('t=%.1f  region x=%d..%d' % (t, x0, x1))
    rr = red[:, band].sum(axis=1) / float(x1 - x0)
    for y0, y1 in bands(rr > 0.45, 3):
        print('  RED bar rows  y=%d..%d' % (y0, y1))
    ww = white[:, band].sum(axis=1) / float(x1 - x0)
    for y0, y1 in bands(ww > 0.5, 3):
        row = white[y0:y1 + 1]
        cols = np.nonzero(row.mean(axis=0) > 0.5)[0]
        print('  WHITE sheet rows y=%d..%d  x=%d..%d' %
              (y0, y1, cols[0], cols[-1]))


if __name__ == '__main__':
    main()
