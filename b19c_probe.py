"""b19c_probe.py - private helper (batch b19c): measure the on-screen overlay
geometry of a frame: the saturated-red section bar and the white sheet.

Usage: py -3.14 b19c_probe.py <id> <t> [<id> <t> ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def frame(video, t, tmp):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', tmp], check=True, capture_output=True)
    return Image.open(tmp).convert('RGB')


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
    args = sys.argv[1:]
    for i in range(0, len(args), 2):
        vid, t = args[i], float(args[i + 1])
        video = 'dl/w4_%s.mp4' % vid
        tmp = 'frames/b19c_%s/_probe.png' % vid
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        im = frame(video, t, tmp)
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 110) & (g < 100) & (b < 100)
        white = (r > 200) & (g > 200) & (b > 200)
        print('== %s t=%s size=%s' % (vid, t, im.size))
        for name, m in (('RED', red), ('WHITE', white)):
            rows = bands(m.sum(axis=1) > 0.5 * m.shape[1], 4)
            for y0, y1 in rows:
                sub = m[y0:y1 + 1]
                cols = bands(sub.sum(axis=0) > 0.5 * sub.shape[0], 4)
                if cols:
                    print('   %s band y=%d..%d  x=%d..%d  fill=%.2f' %
                          (name, y0, y1, cols[0][0], cols[-1][1], sub.mean()))


if __name__ == '__main__':
    main()
