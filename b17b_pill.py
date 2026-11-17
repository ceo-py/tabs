"""b17b_pill.py - private helper for the Nirvana (b17b) batch.

For every panel crop produced by b17b_build.py, finds the red
"Strumming Pattern" pill inside the sheet and saves a zoom crop of the pill
plus the pattern row under it, so the pattern can be transcribed reliably
(the layout shifts from panel to panel).

Usage: py -3.14 b17b_pill.py <id> ...
"""
import os
import sys

import numpy as np
from PIL import Image

ZOOM = 2
XL, XR = 380, 1520        # the pill / pattern row live in this panel column range


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
    for vid in sys.argv[1:]:
        base = 'frames/b17b_%s' % vid
        for f in sorted(os.listdir(base)):
            if not (f.startswith('p') and f.endswith('.png')
                    and not f.startswith('pill_')):
                continue
            path = os.path.join(base, f)
            im = Image.open(path).convert('RGB')
            a = np.asarray(im).astype(int)
            H, W = a.shape[:2]
            if W <= XR:
                print('%s %s: panel too narrow' % (vid, f))
                continue
            red = (a[..., 0] > 110) & (a[..., 1] < 95) & (a[..., 2] < 95)
            win = red[:, XL:XR]
            rows = bands(win.sum(axis=1) > (XR - XL) * 0.25, 3)
            pick = None
            for r0, r1 in rows:
                if r0 <= 2 and win[r0:r1 + 1].sum(axis=1).max() > (XR - XL) * 0.9:
                    continue          # the full-width section bar
                if pick is None or (r1 - r0) > (pick[1] - pick[0]):
                    pick = (r0, r1)
            if pick is None:
                print('%s %s: NO PILL' % (vid, f))
                continue
            r0, r1 = pick
            y0 = max(0, r0 - 4)
            y1 = min(H, r1 + 78)
            crop = im.crop((XL, y0, XR, y1))
            crop = crop.resize((crop.size[0] * ZOOM, crop.size[1] * ZOOM), Image.LANCZOS)
            out = os.path.join(base, 'pill_' + f)
            crop.save(out)
            # the chord row sits above the pill
            cy0 = max(0, r0 - 105)
            cy1 = max(0, r0 - 4)
            if cy1 > cy0:
                cc = im.crop((XL, cy0, XR, cy1))
                cc = cc.resize((cc.size[0] * ZOOM, cc.size[1] * ZOOM), Image.LANCZOS)
                cc.save(os.path.join(base, 'chord_' + f))
            print('%s %s: pill rows %d-%d -> %s' % (vid, f, r0, r1, out))


if __name__ == '__main__':
    main()
