"""b19a_labels.py - private helper (batch b19a): group the red section label of a
video over time.

The overlay of these GuitarZero2HeroExpress videos puts a red section title
(e.g. VERSE / CHORUS 1 / BRIDGE) in a fixed box on the right of the frame.
This script crops that box once per second, hashes the red glyph mask and
groups the frames into runs, then writes one representative crop per run.

Usage: py -3.14 b19a_labels.py <id> <x> <y> <w> <h> [start] [end] [step]
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
    t0 = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
    t1 = float(sys.argv[7]) if len(sys.argv) > 7 else 1e9
    step = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
    video = video_for(vid)
    base = 'frames/b19a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_lbltmp.png')
    runs = []
    t = t0
    while t <= t1:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 90) & (r - g > 40) & (r - b > 40)
        sig = red.tobytes()
        if runs and runs[-1]['sig'] == sig:
            runs[-1]['t1'] = t
            runs[-1]['n'] += 1
        else:
            runs.append({'t0': t, 't1': t, 'sig': sig, 'n': 1, 'rep': t})
        t += step
    # merge runs that only differ by a couple of pixels (blink/highlight)
    merged = []
    for r in runs:
        if merged and np.sum(np.frombuffer(merged[-1]['sig'], np.uint8) !=
                             np.frombuffer(r['sig'], np.uint8)) < 250:
            merged[-1]['t1'] = r['t1']
            merged[-1]['n'] += r['n']
        else:
            merged.append(r)
    out = []
    for i, r in enumerate(merged):
        p = os.path.join(base, 'lbl_%02d.png' % i)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % r['rep'], '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), p],
                       check=True, capture_output=True)
        out.append((i, r['t0'], r['t1'], r['n'], p))
    for i, a, b, n, p in out:
        print('#%d  %g-%gs  n=%d  %s' % (i, a, b, n, p))


if __name__ == '__main__':
    main()
