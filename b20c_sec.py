"""b20c_sec.py - private helper (batch b20c, channel 'ike'): find the section
titles of a scrolling MuseScore-style score.

Inside the printed sheet the rows are
    y=  0.. 25   page margin
    y= 25.. 70   section title      ("Intro", "Verse 1", "Chorus", ...)
    y= 85..120   chord names        ("A", "Dadd9/A", "Fmaj7/A", ...)
    y=140..330   standard notation staff
    y=380..560   TAB staff
(the exact offsets differ per song because the score is rendered at a
different zoom, and the whole system slides up and down while it scrolls).

A section title is therefore a row of text that sits ABOVE the row of chord
names.  This script finds the two rows (ignoring the full-width staff rules)
and, when a second row is present above the chord row, treats it as the title.
The distinct titles are written into a montage with their time ranges.

Usage: py -3.14 b20c_sec.py <id> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

TOP = 0          # top of the inspected band
BOTTOM = 340     # bottom of the inspected band
RULE_FRAC = 0.55  # a row with ink on this share of the width is a staff rule


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


def same(a, b):
    if a is None or b is None or a.shape != b.shape:
        return False
    n = max(1, a.size)
    return int((a != b).sum()) <= 0.10 * n


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sec.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    hits = []
    t = 1.0
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf',
                        'crop=1920:%d:0:%d' % (BOTTOM - TOP, TOP), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        m = a.min(axis=2) < 170
        rule = m.sum(axis=1) > RULE_FRAC * 1920
        keep = m.copy()
        keep[rule] = False
        rows = bands(keep.sum(axis=1) > 0, 2)
        if len(rows) >= 2:
            r0, r1 = rows[0]
            sub = keep[r0:r1 + 1]
            cols = bands(sub.sum(axis=0) > 0, 1)
            if cols:
                x0, x1 = cols[0][0], cols[-1][1]
                crop = im.crop((x0, r0, x1 + 1, r1 + 1))
                hits.append((t, crop, [x0, TOP + r0, x1 - x0 + 1, r1 - r0 + 1]))
        t += step

    merged = []
    for t, crop, box in hits:
        if merged and t - merged[-1]['t1'] <= step * 1.8 and same(
                np.asarray(crop.convert('L')) < 170,
                np.asarray(merged[-1]['crop'].convert('L')) < 170):
            merged[-1]['t1'] = t
            merged[-1]['crop'] = crop
            merged[-1]['box'] = box
            continue
        merged.append({'t0': t, 't1': t, 'crop': crop, 'box': box})

    if not merged:
        print('NO SECTIONS', vid)
        return
    W = max(g['crop'].size[0] for g in merged) + 24
    H = sum(g['crop'].size[1] + 32 for g in merged) + 10
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 20)
    y = 5
    for g in merged:
        d.rectangle([0, y, W, y + 29], fill=(0, 0, 0))
        d.text((5, y + 4), 't=%g-%g   box=%s' % (g['t0'], g['t1'], g['box']),
               font=fnt, fill=(255, 210, 0))
        canvas.paste(g['crop'], (6, y + 31))
        y += g['crop'].size[1] + 32
    out = os.path.join(base, 'sections.png')
    canvas.save(out)
    print(out, canvas.size)
    for g in merged:
        print('  t=%g-%g  box=%s' % (g['t0'], g['t1'], g['box']))


if __name__ == '__main__':
    main()
