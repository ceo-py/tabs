"""b18c_sheet_on.py - private helper: find when a white overlay sheet is on screen.

For every STEP seconds the region <x y w h> is sampled and the fraction of
near-white pixels is reported; frames whose fraction is above the threshold are
grouped into runs.  Used for videos where the tab sheet covers the whole
lower half of the frame.

Usage: py -3.14 b18c_sheet_on.py <id> <x> <y> <w> <h> [step] [thresh]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    step = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
    thresh = float(sys.argv[7]) if len(sys.argv) > 7 else 0.5
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sow_tmp.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    runs = []
    cur = None
    for i in range(int(dur / step) + 1):
        t = i * step
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        white = ((r > 235) & (g > 235) & (b > 235)).mean()
        on = white >= thresh
        if on and cur is None:
            cur = [t, t]
        elif on:
            cur[1] = t
        elif cur is not None:
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    print('%s runs:' % vid)
    for a, b in runs:
        if b - a >= step:
            print('  t=%g-%g' % (a, b))


if __name__ == '__main__':
    main()
