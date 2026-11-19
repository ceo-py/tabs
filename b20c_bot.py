"""b20c_bot.py - private helper (batch b20c, channel 'ike'): for each panel
timestamp find the last row that still belongs to the printed score sheet, so
the crop bbox never picks up a strip of video footage.

The sheet is a flat page of one colour; the footage below is a busy picture, so
the split row is where the share of page-coloured pixels falls apart.

Usage: py -3.14 b20c_bot.py <id> <t1> [t2 ...]
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
    tmp = os.path.join(base, '_bot.png')
    for t in sys.argv[2:]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
        H = a.shape[0]
        page = np.median(a[:30].reshape(-1, 3), axis=0)
        d = np.abs(a - page).max(axis=2)
        frac = (d < 14).mean(axis=1)
        lum = a.min(axis=2)
        dark = (lum < 110).sum(axis=1)
        # first row from 400 down where the page stops dominating and a wide
        # dark band (the player / guitar) begins
        bot = H - 1
        for y in range(400, H):
            if frac[y] < 0.25 and dark[y] > 0.25 * a.shape[1]:
                bot = y
                break
        print('t=%-6s  sheet_bottom=%d   (rows %d..%d)  frac=%s'
              % (t, bot - 1, bot - 1, bot,
                 [round(float(frac[y]), 2) for y in range(bot - 6, bot + 4, 2)]))


if __name__ == '__main__':
    main()
