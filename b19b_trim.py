"""b19b_trim.py - private helper: find where the sheet content actually ends.

For a candidate panel (video id + timestamp + crop box) it reports the last
row of the crop that still carries ink, so the panel can be trimmed to the
content instead of showing a big empty white sheet.

Usage: py -3.14 b19b_trim.py <id> <t> <x> <y> <w> <h> [<id> <t> <x> <y> <w> <h> ...]
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


def main():
    args = sys.argv[1:]
    tmpdir = 'frames/b19b_trim'
    os.makedirs(tmpdir, exist_ok=True)
    for i in range(0, len(args), 6):
        vid, ts, x, y, w, h = args[i:i + 6]
        t = float(ts)
        x, y, w, h = int(x), int(y), int(w), int(h)
        tmp = os.path.join(tmpdir, '_t.png')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                        video_path(vid), '-frames:v', '1', tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB').crop((x, y, x + w, y + h))
        a = np.asarray(im).astype(np.int16)
        ink = (a.min(axis=2) < 238)
        counts = ink.sum(axis=1)
        rows = np.nonzero(counts > 4)[0]
        if not len(rows):
            print('%s t=%s  no ink' % (vid, ts))
            continue
        last = int(rows[-1])
        # the last contiguous band of ink, so a half-scrolled system is visible
        band_start = last
        while band_start > 0 and counts[band_start - 1] > 4:
            band_start -= 1
        print('%s t=%-7s ink_bottom=%d (crop y %d..%d)  band=%d..%d  rows=%d'
              % (vid, ts, last, y + last, y + h, band_start, last, len(rows)))


if __name__ == '__main__':
    main()
