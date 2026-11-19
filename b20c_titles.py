"""b20c_titles.py - private helper (batch b20c, channel 'ike'): find the
section titles of a scrolling MuseScore-style score.

The score sheet occupies the top of the frame.  Inside it the vertical layout
is stable:
    y= 60..185   section titles ("Intro", "Verse 1", "Chorus", ...)
    y=185..235   chord names      ("A", "Dadd9/A", "Fmaj7/A", "G6/A", ...)
    y=235..400   standard notation staff
    y=430..590   TAB staff
    y=620..1080  video footage

So every text group found in the 60..185 band is a section title.  The titles
scroll with the score, so the detector groups consecutive samples whose title
looks the same and prints a montage of the distinct titles with their time
ranges.

Usage: py -3.14 b20c_titles.py <id> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

BAND = (60, 185)


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


def groups(mask, gap=14):
    """horizontal text groups separated by at least `gap` blank columns"""
    cols = mask.sum(axis=0) > 0
    out, start = [], None
    last = None
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


def same(a, b):
    if a is None or b is None or a.shape != b.shape:
        return False
    n = max(1, a.size)
    return int((a != b).sum()) <= 0.12 * n


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_t_band.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    y0, y1 = BAND
    hits = []
    t = 1.0
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
            gs = groups(sub)
            if not gs:
                continue
            x0, x1 = gs[0][0], gs[-1][1]
            crop = im.crop((x0, r0, x1 + 1, r1 + 1))
            hits.append((t, len(gs), crop, [x0 + 0, y0 + r0, x1 - x0 + 1, r1 - r0 + 1]))
        t += step

    # keep only rows where a single group carries a title: title bands sit
    # higher than the chord row, so a group whose top is above the chord row
    # baseline and which is the only group in its row band is a title
    titles = []
    for t, ng, crop, box in hits:
        if ng >= 2:
            titles.append((t, crop, box))
    merged = []
    for t, crop, box in titles:
        if merged and t - merged[-1]['t1'] <= step * 1.6 and same(
                np.asarray(crop.convert('L')) < 170,
                np.asarray(merged[-1]['crop'].convert('L')) < 170):
            merged[-1]['t1'] = t
            merged[-1]['crop'] = crop
            merged[-1]['box'] = box
            continue
        merged.append({'t0': t, 't1': t, 'crop': crop, 'box': box})

    if not merged:
        print('NO TITLES', vid)
        return
    W = max(g['crop'].size[0] for g in merged) + 20
    H = sum(g['crop'].size[1] + 30 for g in merged) + 10
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 20)
    y = 5
    for g in merged:
        d.rectangle([0, y, W, y + 27], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%g-%g  box=%s' % (g['t0'], g['t1'], g['box']),
               font=fnt, fill=(255, 210, 0))
        canvas.paste(g['crop'], (5, y + 28))
        y += g['crop'].size[1] + 30
    out = os.path.join(base, 'titles.png')
    canvas.save(out)
    print(out, canvas.size)
    for g in merged:
        print('  t=%g-%g  box=%s' % (g['t0'], g['t1'], g['box']))


if __name__ == '__main__':
    main()
