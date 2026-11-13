"""Tell, for every prepared section, whether the panel is a TAB staff or a
CHORD / STRUMMING panel.

The chord-and-strumming panels of this channel print their headings in dark
red inside the white sheet ("STRUMMING PATTERN"), while the TAB sheets are pure
black on white.  So the amount of dark red below the section bar tells the two
apart.

Usage: py -3.14 b16_kind.py <frames_dir>
"""
import json, os, sys
import numpy as np
from PIL import Image


def main():
    d = sys.argv[1]
    scan = json.load(open(os.path.join(d, 'scan.json'), encoding='utf-8'))
    for s in scan['sections']:
        p = s['png']
        if not os.path.exists(p):
            continue
        a = np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
        h, w = a.shape[:2]
        r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        redrow = ((r > 125) & (g < 80) & (b < 80)).sum(axis=1)
        redcol = ((r > 125) & (g < 80) & (b < 80)).sum(axis=0)
        rows = np.flatnonzero(redrow > 0.4 * w)
        cols = np.flatnonzero(redcol > 0.12 * h)
        if len(rows) and len(cols) and redcol[cols[-1]] > 0.4 * h:
            sheet = a[:, :max(1, int(cols[-1]) - 2)]     # vertical label on the right
        elif len(rows):
            sheet = a[int(rows[-1]) + 1:, :]             # horizontal bar on top
        else:
            sheet = a
        sr, sg, sb = sheet[:, :, 0], sheet[:, :, 1], sheet[:, :, 2]
        dark_red = int(((sr > 110) & (sr < 200) & (sg < 90) & (sb < 90)).sum())
        white = int(((sr > 200) & (sg > 200) & (sb > 200)).sum())
        dark = int((sr < 110).sum())
        kind = 'CHORD' if dark_red > 300 else 'TAB'
        print('%s sec%-2d t=%-4d-%-4d %-5s darkred=%-7d dark=%-8d white=%-8d' %
              (os.path.basename(d), s['i'], s['t0'], s['t1'], kind, dark_red, dark, white))


if __name__ == '__main__':
    main()
