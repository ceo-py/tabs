"""b17a_pill.py - private helper: does the classic-layout video ever show the
dark-red "Strumming Pattern" pill / chord-name sheet?

Scans the video for a wide dark-red rounded pill in the lower sheet area and
reports the timestamps where it appears.

Usage: py -3.14 b17a_pill.py <video> <id> [interval]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b17a_survey import bands  # noqa: E402


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    base = 'frames/b17a_%s' % vid
    tmpd = base + '/pl2'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f' % interval, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    hits = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        # dark saturated red (the pill is #B01E24-ish)
        pill = (r > 140) & (r < 215) & (g < 60) & (b < 60)
        sub = pill[int(860 * im.size[1] / 1080):int(960 * im.size[1] / 1080),
                   int(820 * im.size[0] / 1920):int(1250 * im.size[0] / 1920)]
        rows = bands(sub.sum(axis=1) > 0.5 * sub.shape[1], 2)
        if rows:
            hits.append(i * interval)
    # collapse
    out = []
    for h in hits:
        if not out or h - out[-1][-1] > interval * 1.5:
            out.append([h])
        else:
            out[-1].append(h)
    print('%s  pill at: %s' % (vid, ' '.join('%g-%gs' % (r[0], r[-1]) for r in out) or 'NONE'))


if __name__ == '__main__':
    main()
