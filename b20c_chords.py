"""b20c_chords.py - private helper (batch b20c, channel 'ike'): list the chord
labels printed on the chord row of the scrolling score.

The chord row sits at a stable y band (y0..y1) inside the sheet.  For every
sample time the band is cut out, split into horizontal text groups and each
group is compared with the groups seen so far, so that the montage shows every
distinct chord label exactly once together with the time range it is visible.

Usage: py -3.14 b20c_chords.py <id> <y0> <y1> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


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


def groups(mask, gap=25):
    cols = mask.sum(axis=0) > 0
    out, start, last = [], None, None
    for i, v in enumerate(cols):
        if v:
            if start is None:
                start = i
            last = i
        elif start is not None and i - last >= gap:
            out.append((start, last))
            start = None
    if start is not None:
        out.append((start, last))
    return out


def similar(a, b):
    """same glyph row (same height, similar ink) -> treat as the same label"""
    if a.shape != b.shape:
        return False
    return int((a != b).sum()) <= 0.18 * max(1, a.size)


def main():
    vid = sys.argv[1]
    y0 = int(sys.argv[2])
    y1 = int(sys.argv[3])
    step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_ch_band.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())

    known = []          # list of dicts: mask, t0, t1, crop
    t = 0.5
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf',
                        'crop=1920:%d:0:%d' % (y1 - y0, y0), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        m = a.min(axis=2) < 170
        rows = bands(m.sum(axis=1) > 0, 2)
        for r0, r1 in rows:
            sub = m[r0:r1 + 1]
            for g0, g1 in groups(sub):
                gm = sub[:, g0:g1 + 1]
                if gm.sum() < 40:
                    continue
                hit = None
                for k in known:
                    if similar(gm, k['mask']):
                        hit = k
                        break
                if hit is None:
                    known.append({'mask': gm, 't0': t, 't1': t,
                                  'crop': im.crop((g0, r0, g1 + 1, r1 + 1))})
                else:
                    hit['t1'] = t
        t += step

    W = 0
    for k in known:
        W = max(W, k['crop'].size[0])
    cellw = W + 20
    cellh = 62
    cols = 4
    rows_n = (len(known) + cols - 1) // cols
    canvas = Image.new('RGB', (cellw * cols + 10, cellh * rows_n + 10), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    for i, k in enumerate(known):
        cx = 5 + (i % cols) * cellw
        cy = 5 + (i // cols) * cellh
        d.text((cx, cy), 't=%g-%g' % (k['t0'], k['t1']), font=fnt, fill=(255, 210, 0))
        canvas.paste(k['crop'], (cx, cy + 22))
    out = os.path.join(base, 'chords_%d.png' % y0)
    canvas.save(out)
    print(out, canvas.size, len(known))
    for i, k in enumerate(known):
        print('%2d  t=%g-%g  w=%d h=%d' % (i, k['t0'], k['t1'],
                                           k['crop'].size[0], k['crop'].size[1]))


if __name__ == '__main__':
    main()
