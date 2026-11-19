"""b20c_sheet_edge.py - private helper (batch b20c, channel 'ike'): find the row
where the printed score sheet ends and the video footage starts.

The sheet is a flat page of one colour; the footage below is a busy picture.
So the boundary is the row where the share of "page coloured" pixels drops.

Usage: py -3.14 b20c_sheet_edge.py <id> <t1> [t2 ...]
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
    tmp = os.path.join(base, '_edge.png')
    for t in sys.argv[2:]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
        H, W = a.shape[:2]
        # page colour = median of the top rows (that part is always page)
        page = np.median(a[:40].reshape(-1, 3), axis=0)
        d = np.abs(a - page).max(axis=2)
        frac = (d < 14).mean(axis=1)
        sheet = frac > 0.80
        end = 0
        for i in range(H):
            if sheet[i]:
                end = i
            elif i > 60 and end < i - 1:
                break
        # the boundary is the last row that still belongs to the page
        end = 0
        run = None
        for i in range(H):
            if sheet[i]:
                run = i
        print('t=%-6s page=%s  last_page_row=%d' % (t, page.round(0), run))
        print('    frac around:', [(r, round(float(frac[r]), 2)) for r in
                                    range(max(0, run - 12), min(H, run + 14), 3)])


if __name__ == '__main__':
    main()
