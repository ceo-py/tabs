"""b20c_geom.py - private helper (batch b20c, channel 'ike'): measure the
horizontal split between the printed sheet (top) and the video footage (bottom),
and find the vertical bands of ink inside the sheet.

Usage: py -3.14 b20c_geom.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_geom.png')
    for t in sys.argv[2:]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        # "white sheet" = rows where most pixels are near white
        white = (a.min(axis=2) > 235).mean(axis=1)
        rows_white = white > 0.55
        # last row index where the sheet is still dominant
        idx = [i for i, v in enumerate(rows_white) if v]
        sheet_bottom = max(idx) if idx else -1
        # find the last contiguous run of sheet rows
        run_start = None
        for i in range(len(rows_white)):
            if rows_white[i]:
                if run_start is None:
                    run_start = i
            else:
                if run_start is not None and i - run_start > 100:
                    sheet_bottom = i - 1
                run_start = None
        print('t=%-6s sheet_bottom=%d  (rows %d..%d white-ish)' %
              (t, sheet_bottom, min(idx) if idx else -1, sheet_bottom))
        # ink profile inside the sheet
        ink = (a[:sheet_bottom].min(axis=2) < 200).sum(axis=1)
        bands, start = [], None
        for i, v in enumerate(ink):
            if v > 3 and start is None:
                start = i
            elif v <= 3 and start is not None:
                bands.append((start, i - 1))
                start = None
        if start is not None:
            bands.append((start, len(ink) - 1))
        print('   ink bands (y0,y1):', bands)


if __name__ == '__main__':
    main()
