"""b20d_scan2.py - private helper (batch b20d): second-opinion detector for a
TAB panel of any colour (not only white).

For every sampled second it reports the largest fraction of the frame that is
bright and unsaturated (a printed tab page is bright paper; guitar wood is
strongly saturated amber).  A TAB overlay shows up as a sudden spike.

Usage:
  py -3.14 b20d_scan2.py <id> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20d_%s' % vid
    os.makedirs(base, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    tmp = os.path.join(base, '_scan2_tmp.png')
    t = 0.5
    out = []
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], capture_output=True)
        if os.path.exists(tmp):
            a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
            mx = a.max(axis=2)
            mn = a.min(axis=2)
            bright = (mx > 170) & ((mx - mn) < 55)
            out.append((round(t, 1), round(float(bright.mean()), 4)))
        t += step
    vals = [v for _, v in out]
    if not vals:
        print('NO DATA', vid)
        return
    med = float(np.median(vals))
    print('%s median=%.4f' % (vid, med))
    for tt, v in out:
        if v > max(0.08, med * 2.0):
            print('  t=%-7s bright_frac=%.4f' % (tt, v))


if __name__ == '__main__':
    main()
