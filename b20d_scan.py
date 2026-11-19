"""b20d_scan.py - private helper (batch b20d / Sparky Guitar): find the frames
where the TAB strip is on screen.

The Sparky Guitar TAB strip is a pale cream horizontal band.  For every
sampled second we look for rows that contain a long run of that cream colour
and report the band.

Usage:
  py -3.14 b20d_scan.py <id> [step] [minrun]
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
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    minrun = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20d_%s' % vid
    os.makedirs(base, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    tmp = os.path.join(base, '_scan_tmp.png')
    t = 0.5
    hits = []
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], capture_output=True)
        if not os.path.exists(tmp):
            t += step
            continue
        a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        mx = a.max(axis=2)
        mn = a.min(axis=2)
        cream = (mx > 232) & ((mx - mn) <= 14)
        rows = cream.sum(axis=1)
        best = None
        for y0, y1 in bands(rows > minrun, 3):
            if best is None or (y1 - y0) > (best[1] - best[0]):
                best = (y0, y1)
        if best:
            y0, y1 = best
            xs = np.where(cream[y0:y1 + 1].sum(axis=0) > (y1 - y0 + 1) * 0.5)[0]
            hits.append((round(t, 1), y0, y1, int(xs.min()), int(xs.max())))
        t += step
    if not hits:
        print('NO TAB BAND', vid)
        return
    print('%s hits=%d' % (vid, len(hits)))
    for h in hits:
        print('  t=%-7s rows %4d..%4d  cols %4d..%4d' % h)


if __name__ == '__main__':
    main()
