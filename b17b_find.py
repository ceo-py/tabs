"""b17b_find.py - private helper for the Nirvana (b17b) batch.

Scans the video area (above the red section bar) for saturated-red boxes and
reports their positions over time - used to locate panels that live INSIDE the
video footage (e.g. the Lithium strumming pattern) instead of on the sheet.

Usage: py -3.14 b17b_find.py <video> <step> [y0 y1]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

TMP = 'frames/b17b_probe/_f.png'


def bands(flags, min_run=2):
    flags = [bool(v) for v in flags]
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
    video, step = sys.argv[1], float(sys.argv[2])
    y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    y1 = int(sys.argv[4]) if len(sys.argv) > 4 else 550
    x0 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    x1 = int(sys.argv[6]) if len(sys.argv) > 6 else 1920
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    t = 0.0
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
                        '-frames:v', '1', TMP], check=True, capture_output=True)
        a = np.asarray(Image.open(TMP).convert('RGB')).astype(int)
        H, W = a.shape[:2]
        reg = a[y0:y1, x0:x1]
        red = (reg[..., 0] > 110) & (reg[..., 1] < 95) & (reg[..., 2] < 95)
        rows = bands(red.sum(axis=1) > 3, 2)
        boxes = []
        for r0, r1 in rows:
            sub = red[r0:r1 + 1]
            cols = bands(sub.sum(axis=0) > (r1 - r0) * 0.5, 2)
            if not cols:
                continue
            boxes.append((int(cols[0][0]) + x0, y0 + r0, int(cols[-1][1] - cols[0][0]),
                          int(r1 - r0 + 1)))
        print('t=%6.1f  %s' % (t, boxes))
        t += step


if __name__ == '__main__':
    main()
