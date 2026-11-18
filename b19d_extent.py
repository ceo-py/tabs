"""b19d_extent.py - private helper: find the vertical extent of the printed
content inside a crop region, so panel bboxes can be tightened.

Usage: py -3.14 b19d_extent.py <video> <id> <x> <w> <y0> <y1> <t1> [t2 ...]
"""
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    video, vid = sys.argv[1], sys.argv[2]
    x, w, y0, y1 = [int(v) for v in sys.argv[3:7]]
    thr = int(sys.argv[7]) if len(sys.argv) > 7 else 235
    tmp = 'frames/b19d_%s/_ext.png' % vid
    for t in sys.argv[8:]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                        '-frames:v', '1', '-vf',
                        'crop=%d:%d:%d:%d' % (w, y1 - y0, x, y0), tmp],
                       check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('L')).astype(np.int16)
        # ink = anything clearly darker than the white sheet
        ink = (a < thr).sum(axis=1)
        rows = [i for i, v in enumerate(ink) if v > 2]
        if not rows:
            print('t=%s  EMPTY' % t)
            continue
        last = y0 + rows[-1] + 1
        h = last - y0
        if h % 2:
            h += 1
        print('t=%-6s content_bottom=%d  -> bbox=[%d, %d, %d, %d]'
              % (t, last, x, y0, w, h))


if __name__ == '__main__':
    main()
