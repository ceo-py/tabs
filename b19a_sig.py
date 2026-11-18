"""b19a_sig.py - private helper (batch b19a): group frames of a video by the
content of a rectangular region.

Usage: py -3.14 b19a_sig.py <id> <x> <y> <w> <h> <mode> [start] [end] [step]
        mode = white | red | gray | any
Prints the time ranges of each distinct content group and writes one
representative crop per group as frames/b19a_<id>/sig_<nn>.png
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def video_for(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    raise SystemExit('no video for ' + vid)


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    mode = sys.argv[6]
    t0 = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
    t1 = float(sys.argv[8]) if len(sys.argv) > 8 else 1e9
    step = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0
    video = video_for(vid)
    base = 'frames/b19a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sigtmp.png')
    runs = []
    t = t0
    while t <= t1:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        if mode == 'white':
            m = (r > 170) & (g > 170) & (b > 170)
        elif mode == 'red':
            m = (r > 90) & (r - g > 40) & (r - b > 40)
        elif mode == 'gray':
            m = (abs(r - g) < 25) & (abs(g - b) < 25) & (r > 90)
        else:
            m = (r + g + b) > 120
        sig = m.tobytes()
        if runs and runs[-1]['sig'] == sig:
            runs[-1]['t1'] = t
        else:
            runs.append({'t0': t, 't1': t, 'sig': sig, 'rep': t})
        t += step
    merged = []
    for r in runs:
        if merged and np.sum(np.frombuffer(merged[-1]['sig'], np.uint8) !=
                             np.frombuffer(r['sig'], np.uint8)) < 300:
            merged[-1]['t1'] = r['t1']
        else:
            merged.append(r)
    for i, r in enumerate(merged):
        p = os.path.join(base, 'sig_%02d.png' % i)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % r['rep'], '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), p],
                       check=True, capture_output=True)
        frac = float(np.frombuffer(r['sig'], np.uint8).mean())
        print('#%d  %g-%gs  fill=%.3f  %s' % (i, r['t0'], r['t1'], frac, p))


if __name__ == '__main__':
    main()
