"""b18a_probe.py - text probe of a video frame.

Reports, for a given time and an x range, the horizontal bands that contain
red pixels.  Used to find the exact edges of the section-title bar and of the
CHORD / STRUM table without eyeballing whole frames.

Usage: py -3.14 b18a_probe.py <video_id> <t> <x0> <x1>
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    vid, t, x0, x1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    video = 'dl/w4_%s.mp4' % vid
    tmp = os.path.join(ROOT, 'frames', 'b18a_probe.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 200) & (g > 200) & (b > 200)
    print('--- red rows in x=%d..%d' % (x0, x1))
    rows = red[:, x0:x1].sum(axis=1)
    inb = False
    for y in range(a.shape[0]):
        if rows[y] > 0 and not inb:
            start, inb = y, True
        elif rows[y] == 0 and inb:
            print('  red band y=%d..%d  (max %d px wide)' % (start, y - 1, rows[start:y].max()))
            inb = False
    if inb:
        print('  red band y=%d..end' % start)
    print('--- bright rows in x=%d..%d' % (x0, x1))
    rows = white[:, x0:x1].sum(axis=1)
    inb = False
    for y in range(a.shape[0]):
        if rows[y] > 0 and not inb:
            start, inb = y, True
        elif rows[y] == 0 and inb:
            print('  white band y=%d..%d  (max %d px wide)' % (start, y - 1, rows[start:y].max()))
            inb = False
    if inb:
        print('  white band y=%d..end' % start)


if __name__ == '__main__':
    main()
