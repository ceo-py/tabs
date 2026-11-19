"""b20c_rows.py - private helper (batch b20c, channel 'ike'): full-frame row
profile so the panel bboxes of each video can be placed exactly.

For every sample time it prints:
  * the row where the printed score sheet ends and the video footage starts
    (found from the strong horizontal edge / dark separator row)
  * every band of rows that carries ink inside the sheet
  * the row extent of the TAB staff (the 6-line block in the lower half)

Usage: py -3.14 b20c_rows.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


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
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_rows.png')
    for t in sys.argv[2:]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        H, W = a.shape[:2]
        lum = a.min(axis=2)

        # separator: the dark horizontal line where the sheet meets the footage
        sep = (lum < 120).sum(axis=1)
        cand = [i for i in range(H) if sep[i] > 0.6 * W]
        sheet_end = cand[0] if cand else -1

        print('t=%-6s  separator_row=%s' % (t, cand[:4]))
        ink = (lum[:sheet_end + 1] < 170).sum(axis=1)
        for y0, y1 in bands(ink > 2, 1):
            print('    ink y=%4d..%4d  h=%3d  max=%5d' % (y0, y1, y1 - y0 + 1, ink[y0:y1 + 1].max()))
        # tab staff: rows in the lower part of the sheet that contain a wide run
        # of ink (the tab numbers sit in a narrow column band, the staff lines
        # run across the whole width)
        print()


if __name__ == '__main__':
    main()
