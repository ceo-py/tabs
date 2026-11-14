"""b14b_trim.py - private helper: tight, clean panel crops.

b13_survey.py returns the whole overlay region of the frame.  For several of
these videos the sheet is much taller than its content, which would leave a big
empty white band on the card.  This helper crops the region and then trims the
BOTTOM to the last row that really carries ink (the notation), ignoring
one-pixel frame borders and the panel's own edge shading.

Usage:
    py -3.14 b14b_trim.py <video> <outdir> --box x,y,w,h --times 84,168 \
        [--pad 14] [--minh 120] [--edge 10] [--minink 4]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def trim(video, t, box, out, pad=14, minh=120, edge=10, minink=4):
    tmp = out + '.raw.png'
    x, y, w, h = box
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    H, W = a.shape[:2]
    core = a[:, edge:W - edge] if W > 2 * edge else a
    ink = core.min(axis=2) < 235
    counts = ink.sum(axis=1)
    rows = np.flatnonzero(counts >= minink)
    if not len(rows):
        os.remove(tmp)
        return None
    bottom = min(h, int(rows[-1]) + pad + 1)
    # the red header bar must stay complete
    red = (a[..., 0] > 110) & (a[..., 1] < 100) & (a[..., 2] < 100)
    rrows = np.flatnonzero(red.sum(axis=1) > 0.3 * w)
    if len(rrows):
        bottom = max(bottom, min(h, int(rrows[-1]) + 2))
    bottom = max(bottom, minh)
    newbox = '%d:%d:%d:%d' % (w, bottom, x, y)
    cmd2 = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
            '-frames:v', '1', '-vf', 'crop=%s' % newbox, out]
    r2 = subprocess.run(cmd2, capture_output=True)
    os.remove(tmp)
    if r2.returncode != 0 or not os.path.exists(out):
        return None
    return [x, y, w, bottom]


def main():
    argv = sys.argv[1:]
    video, outdir = argv[0], argv[1]
    rest = argv[2:]
    box = None
    times = []
    pad = 14
    minh = 120
    edge = 10
    minink = 4
    i = 0
    while i < len(rest):
        if rest[i] == '--box':
            box = [int(v) for v in rest[i + 1].split(',')]
            i += 2
        elif rest[i] == '--times':
            times = [float(v) for v in rest[i + 1].split(',')]
            i += 2
        elif rest[i] == '--pad':
            pad = int(rest[i + 1]); i += 2
        elif rest[i] == '--minh':
            minh = int(rest[i + 1]); i += 2
        elif rest[i] == '--edge':
            edge = int(rest[i + 1]); i += 2
        elif rest[i] == '--minink':
            minink = int(rest[i + 1]); i += 2
        else:
            times.append(float(rest[i])); i += 1
    os.makedirs(outdir, exist_ok=True)
    tag = '_'.join(str(v) for v in box)
    for t in times:
        out = os.path.join(outdir, 'tr_%s_%s.png' % (str(t).replace('.', '_'), tag))
        res = trim(video, t, box, out, pad=pad, minh=minh, edge=edge, minink=minink)
        print('t=%s -> %s' % (t, res))


if __name__ == '__main__':
    main()
