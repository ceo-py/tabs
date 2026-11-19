"""b20a_strum.py - private helper (batch b20a): list the up / down strum arrow
heads inside a notation band and print them as an arrow sequence.

An arrow head is a solid triangle, so its horizontal dark runs are much wider
than the thin strokes of the printed digits - that is what separates them.

Usage:
  py -3.14 b20a_strum.py <id> <t> <x0,y0,x1,y1> <upY0,upY1> <downY0,downY1> [minrun]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def clusters(cols, gap=8):
    out = []
    for c in cols:
        if out and c - out[-1][-1] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return [int(round(sum(g) / len(g))) for g in out]


def heads(band, minrun):
    """x centres of solid horizontal dark runs (arrow heads) in the window"""
    xs = []
    for row in band:
        dark = row < 90
        i = 0
        n = len(dark)
        while i < n:
            if dark[i]:
                j = i
                while j < n and dark[j]:
                    j += 1
                if j - i >= minrun:
                    xs.append((i + j - 1) // 2)
                i = j
            else:
                i += 1
    return clusters(sorted(set(xs)), gap=12)


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    x0, y0, x1, y1 = [int(v) for v in sys.argv[3].split(',')]
    uy0, uy1 = [int(v) for v in sys.argv[4].split(',')]
    dy0, dy1 = [int(v) for v in sys.argv[5].split(',')]
    minrun = int(sys.argv[6]) if len(sys.argv) > 6 else 11
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_strum_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf',
                    'crop=%d:%d:%d:%d' % (x1 - x0, y1 - y0, x0, y0), tmp],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('L')).astype(np.int16)
    up = heads(a[uy0 - y0:uy1 - y0], minrun)
    dn = heads(a[dy0 - y0:dy1 - y0], minrun)
    events = sorted([(x, 'U') for x in up] + [(x, 'D') for x in dn])
    print('up   x=%s' % up)
    print('down x=%s' % dn)
    print('seq  %s' % ' '.join('%s@%d' % (k, x) for x, k in events))


if __name__ == '__main__':
    main()
