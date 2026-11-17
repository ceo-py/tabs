"""b17b_ascii.py - private helper for the Nirvana (b17b) batch.

Renders an on-screen strumming row as ASCII art so each character of the
pattern can be read letter by letter (D / U / X / -) instead of guessed.

Usage: py -3.14 b17b_ascii.py <video> <t> <y0> <y1> <x0> <x1> [lo]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

TMP = 'frames/b17b_probe/_a.png'


def main():
    vid, t = sys.argv[1], sys.argv[2]
    y0, y1, x0, x1 = (int(v) for v in sys.argv[3:7])
    lo = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1', TMP],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(TMP).convert('L')).astype(int)
    seg = a[y0:y1, x0:x1]
    ink = (seg > lo) & (seg < 250)
    col = ink.sum(axis=0)
    # split into glyph groups
    groups = []
    st = None
    for i, v in enumerate(col > 0):
        if v and st is None:
            st = i
        elif not v and st is not None:
            groups.append((st, i - 1))
            st = None
    if st is not None:
        groups.append((st, len(col) - 1))
    print('glyph groups: %d' % len(groups))
    for gi, (g0, g1) in enumerate(groups):
        sub = ink[:, g0:g1 + 1]
        rows = np.where(sub.sum(axis=1) > 0)[0]
        if len(rows) == 0:
            continue
        sub = sub[rows[0]:rows[-1] + 1]
        print('--- glyph %d  x=%d..%d  w=%d' % (gi, g0 + x0, g1 + x0, g1 - g0 + 1))
        for r in range(0, sub.shape[0], 2):
            print(''.join('#' if sub[r:min(r + 2, sub.shape[0]), c].any() else '.'
                          for c in range(sub.shape[1])))


if __name__ == '__main__':
    main()
