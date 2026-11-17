"""b17b_glyphs.py - private helper for the Nirvana (b17b) batch.

Counts the glyph columns of an on-screen strumming row so the pattern string
is transcribed by counting characters, not by eye.

Usage: py -3.14 b17b_glyphs.py
"""
import subprocess

import numpy as np
from PIL import Image

TMP = 'frames/b17b_probe/_s.png'


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


def scan(vid, t, y0, y1, x0, x1, lo=0):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1', TMP],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(TMP).convert('L')).astype(int)
    seg = a[y0:y1, x0:x1]
    col = ((seg > lo) & (seg < 250)).sum(axis=0)
    b = bands(col > 0, 2)
    print('%s t=%s  glyphs=%d  cols=%s' % (vid, t, len(b), b))


if __name__ == '__main__':
    scan('RhumXNv5uuE', 104, 938, 985, 870, 1310)
    scan('RhumXNv5uuE', 56, 938, 985, 870, 1310)
    scan('6MoufnQTB6U', 20, 925, 985, 860, 1330)
    scan('6MoufnQTB6U', 112, 925, 985, 860, 1330)
    scan('NF7xSm-WC4c', 30, 462, 505, 1515, 1900)
    scan('NF7xSm-WC4c', 48, 462, 505, 1515, 1900)
    scan('NF7xSm-WC4c', 136, 462, 505, 1515, 1900)
