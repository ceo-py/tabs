"""b18c_bar.py - private helper: scan a fixed red-bar strip for section titles.

For every STEP seconds the strip <x y w h> is cropped from the video, the white
lettering inside the red bar is extracted and grouped by shape; the montage
shows the distinct titles with their time ranges.

Usage: py -3.14 b18c_bar.py <id> <x> <y> <w> <h> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


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


def text_mask(im):
    """White lettering on the red bar."""
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 190) & (g > 190) & (b > 190)
    if red.sum() > 0.2 * red.size:
        rows_red = red.sum(axis=1) > 0
        nrows = max(1, int(rows_red.sum()))
        keep = (red.sum(axis=0) / nrows) > 0.5
        if keep.sum() < 2:
            keep = (red.sum(axis=0) / nrows) > 0.2
        if keep.sum() >= 2:
            m = white.copy()
            m[:, ~keep] = False
            return m
    return white


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    step = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_bar_tmp.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    n = int(dur / step)
    hits = []
    for i in range(n + 1):
        t = i * step
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        if not os.path.exists(tmp):
            continue
        im = Image.open(tmp).convert('RGB')
        m = text_mask(im)
        if m.sum() < 30:
            continue
        cols = bands(m.sum(axis=0) > 0, 1)
        rows = bands(m.sum(axis=1) > 0, 1)
        if not cols or not rows:
            continue
        m2 = m[rows[0][0]:rows[-1][1] + 1, cols[0][0]:cols[-1][1] + 1]
        hits.append((t, m2, im.crop((cols[0][0], rows[0][0],
                                      cols[-1][1] + 1, rows[-1][1] + 1))))
    groups = []
    for t, m2, strip in hits:
        if groups and same(m2, groups[-1]['m']):
            groups[-1]['t1'] = t
            groups[-1]['strip'] = strip
            continue
        groups.append({'t0': t, 't1': t, 'm': m2, 'strip': strip})
    merged = []
    for g in groups:
        if merged and g['t0'] - merged[-1]['t1'] <= step * 1.5 and same(g['m'], merged[-1]['m']):
            merged[-1]['t1'] = g['t1']
        else:
            merged.append(g)
    W = max(g['strip'].size[0] for g in merged) + 16
    H = sum(g['strip'].size[1] + 26 for g in merged)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 18)
    y = 0
    for g in merged:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%gs-%gs' % (g['t0'], g['t1']), font=fnt, fill=(255, 210, 0))
        s = g['strip']
        if s.size[1] > s.size[0]:
            s = s.rotate(-90, expand=True)
        canvas.paste(s, (8, y + 26))
        y += s.size[1] + 26
    out = os.path.join(base, 'bar.png')
    canvas.save(out)
    print(out, canvas.size)
    for g in merged:
        print('  t=%g-%g' % (g['t0'], g['t1']))


def same(a, b):
    if a is None or b is None or a.shape != b.shape:
        return False
    n = max(1, a.size)
    return int((a != b).sum()) <= 0.15 * n


if __name__ == '__main__':
    main()
