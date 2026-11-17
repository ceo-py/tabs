"""b18c_ww.py - private helper: timeline for the Wonderwall overlay.

The Wonderwall video has no red bar.  Its overlay is:
  header  x 1130-1815  y 0-235   (WONDERWALL / OASIS / <section> / chord row)
  table   x 936-1905   y 380-556  (CHORD | STRUM | TIMING)

This script samples the video every N seconds and reports, for each sample,
a signature of the red section name and of the table band, so the distinct
on-screen states and their time ranges can be recovered exactly.

Usage: py -3.14 b18c_ww.py <id> [interval] [scale]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

VIDS = {
    'MmmhEd7j8K8': 'dl/w4_MmmhEd7j8K8.mp4',
    'jmNmAnr_Vr4': 'dl/w4_jmNmAnr_Vr4.mp4',
    'YXHCL2Y-e0U': 'dl/w4_YXHCL2Y-e0U.mp4',
    'mbnmB_hTfiM': 'dl/w4_mbnmB_hTfiM.mp4',
    'LRXRm0eMZZY': 'dl/w4_LRXRm0eMZZY.mp4',
    'JvRLYuiyURk': 'dl/w4_JvRLYuiyURk.mp4',
    '_YrDIC5tZcA': 'dl/w4__YrDIC5tZcA.mp4',
}

# full-res regions of interest (1920x1080)
HDR_NAME = (1130, 100, 600, 70)     # red section name
HDR_CHORD = (1130, 160, 690, 75)    # big chord row
TABLE = (936, 380, 969, 176)        # CHORD / STRUM / TIMING table


def frames(video, base, interval, scale):
    tmpd = os.path.join(base, 'wwp')
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=%d:-1' % (interval, scale),
                    os.path.join(tmpd, 'p_%04d.png')], check=True, capture_output=True)
    return sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))


def sig(im, box, scale, mode):
    x, y, w, h = box
    sx, sy = im.size[0] / 1920.0, im.size[1] / 1080.0
    c = im.crop((int(x * sx), int(y * sy), int((x + w) * sx), int((y + h) * sy)))
    a = np.asarray(c.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if mode == 'red':
        m = (r > 110) & (g < 90) & (b < 90)
    else:
        # white lettering; the green "current chord" highlight is not content
        m = (r > 150) & (g > 150) & (b > 150)
        green = (g > 90) & (r < 140) & (b < 140)
        m = m & ~green
    if m.sum() < 8:
        return None, 0
    rows = m.sum(axis=1)
    nz = np.nonzero(rows)[0]
    m = m[nz[0]:nz[-1] + 1]
    cols = m.sum(axis=0)
    nz = np.nonzero(cols)[0]
    m = m[:, nz[0]:nz[-1] + 1]
    return m, int(m.sum())


def same(a, b, tol=0.14):
    if a is None or b is None:
        return a is None and b is None
    if a.shape != b.shape:
        return False
    n = max(1, int(a.sum()))
    return int((a != b).sum()) <= tol * n


def main():
    vid = sys.argv[1]
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 960
    name_box = tuple(int(v) for v in sys.argv[4:8]) if len(sys.argv) > 7 else HDR_NAME
    tbl_box = tuple(int(v) for v in sys.argv[8:12]) if len(sys.argv) > 11 else TABLE
    video = VIDS[vid]
    base = 'frames/b18c_%s' % vid
    groups = {'name': [], 'table': []}
    for i, f in enumerate(frames(video, base, interval, scale)):
        im = Image.open(f)
        t = round(i * interval, 2)
        for key, box, mode in (('name', name_box, 'red'), ('table', tbl_box, 'white')):
            m, npx = sig(im, box, scale, mode)
            hit = None
            for g in groups[key]:
                if same(m, g['m']):
                    hit = g
                    break
            if hit is None:
                groups[key].append({'m': m, 'ranges': [[t, t]], 'rep': t, 'px': npx})
            else:
                if t - hit['ranges'][-1][1] > interval * 1.6:
                    hit['ranges'].append([t, t])
                else:
                    hit['ranges'][-1][1] = t
                if npx > hit['px']:
                    hit['px'] = npx
    for key in ('name', 'table'):
        print('--- %s groups' % key)
        for g in groups[key]:
            rng = ','.join('%g-%g' % (a, b) for a, b in g['ranges'])
            print('  rep=%-7s px=%-7d t=%s' % (g['rep'], g['px'], rng))


if __name__ == '__main__':
    main()
