"""b19b_probe.py - private helper: measure the on-screen overlay geometry.

For a few timestamps it reports the red section-title bar (its row range and
its horizontal extent) and the white sheet below it, so the crop boxes in the
spec can be measured instead of guessed.

Usage: py -3.14 b19b_probe.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for %s' % vid)


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
    video = video_path(vid)
    base = 'frames/b19b_%s' % vid
    tmp = os.path.join(base, '_pr.png')
    for ts in sys.argv[2:]:
        t = float(ts)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 110) & (g < 100) & (b < 100)
        white = (r > 225) & (g > 225) & (b > 225)
        H, W = red.shape
        print('== t=%s  %dx%d' % (ts, W, H))
        for y0, y1 in bands(red.sum(axis=1) > 0.35 * W, 3):
            sub = red[y0:y1 + 1]
            cols = bands(sub.sum(axis=0) > 0, 3)
            print('   RED  rows %d-%d (h=%d)  x-runs %s'
                  % (y0, y1, y1 - y0 + 1,
                     [(c[0], c[1]) for c in cols][:8]))
        for y0, y1 in bands(white.sum(axis=1) > 0.5 * W, 3):
            if y0 < 400:
                continue
            sub = white[y0:y1 + 1]
            cols = bands(sub.sum(axis=0) > 0, 3)
            print('   WHITE rows %d-%d  x-runs %s'
                  % (y0, y1, [(c[0], c[1]) for c in cols][:8]))


if __name__ == '__main__':
    main()
