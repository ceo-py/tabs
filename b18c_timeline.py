"""b18c_timeline.py - private helper: exact section timeline for one video.

Samples the red title bar every STEP seconds, groups the frames by the
white lettering in the bar and renders one montage of the distinct titles
with their time ranges.

Usage: py -3.14 b18c_timeline.py <id> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def bar_text_mask(lbl):
    """White lettering inside the red bar."""
    a = np.asarray(lbl).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 190) & (g > 190) & (b > 190)
    rows_red = red.sum(axis=1) > 0
    nrows = max(1, int(rows_red.sum()))
    colfrac = red.sum(axis=0) / nrows
    keep = colfrac > 0.5
    if keep.sum() < 2:
        keep = colfrac > 0.25
    if keep.sum() < 2:
        return white
    m = white.copy()
    m[:, ~keep] = False
    return m


def sig_of(im):
    m = bar_text_mask(im)
    if m.sum() < 12:
        return None
    tall = m.sum(axis=0) > 0.8 * m.shape[0]
    m[:, tall] = False
    if m.sum() < 12:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    m = m[rows[0][0]:rows[-1][1] + 1, cols[0][0]:cols[-1][1] + 1]
    return m


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmpd = os.path.join(base, 'tl')
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=480:-1' % step,
                    os.path.join(tmpd, 'p_%04d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    SW, SH = 1920, 1080

    # locate the red bar per frame
    samples = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 120) & (g < 95) & (b < 95)
        px = SW / im.size[0]
        py = SH / im.size[1]
        rows = red.sum(axis=1)
        best = None
        for y0, y1 in bands(rows > 0.4 * im.size[0], 3):
            sub = red[y0:y1 + 1]
            cols = bands(sub.sum(axis=0) > 0, 3)
            if not cols:
                continue
            x0, x1 = cols[0][0], cols[-1][1]
            if (x1 - x0) < 0.3 * im.size[0]:
                continue
            area = (x1 - x0) * (y1 - y0)
            if best is None or area > best[4]:
                best = (x0, y0, x1 - x0 + 1, y1 - y0 + 1, area)
        if best is None:
            continue
        bb = [int(best[0] * px), int(best[1] * py),
              int(best[2] * px), int(best[3] * py)]
        samples.append((i * step, bb))

    # group consecutive samples whose lettering matches
    groups = []
    for t, bb in samples:
        strip = crop_bar(video, t, bb, base)
        if strip is None:
            continue
        s = sig_of(strip)
        if s is None:
            continue
        if groups and same(s, groups[-1]['sig']):
            groups[-1]['t1'] = t
            groups[-1]['bb'] = bb
            continue
        groups.append({'t0': t, 't1': t, 'sig': s, 'bb': bb})
    # merge groups separated by a short gap (bar animation)
    merged = []
    for g in groups:
        if merged and g['t0'] - merged[-1]['t1'] <= step * 2 and same(g['sig'], merged[-1]['sig']):
            merged[-1]['t1'] = g['t1']
        else:
            merged.append(g)

    tiles = []
    for g in merged:
        strip = crop_bar(video, g['t0'], g['bb'], base)
        if strip is None:
            continue
        tiles.append((g, strip))
    if not tiles:
        print('NO SECTIONS', vid)
        return
    W = max(s.size[0] for _, s in tiles) + 16
    H = sum(s.size[1] + 26 for _, s in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 18)
    y = 0
    for g, s in tiles:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%gs-%gs  bb=%s' % (g['t0'], g['t1'], g['bb']),
               font=fnt, fill=(255, 210, 0))
        canvas.paste(s, (8, y + 26))
        y += s.size[1] + 26
    out = os.path.join(base, 'timeline.png')
    canvas.save(out)
    print(out, canvas.size)
    for g in merged:
        print('  t=%g-%g' % (g['t0'], g['t1']))


def diff(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def same(a, b):
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    n = max(1, a.size)
    return diff(a.ravel(), b.ravel()) <= 0.15 * n


def crop_bar(video, t, bb, base):
    tmp = os.path.join(base, '_tlbar.png')
    x0, y0, w, h = bb
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1',
           '-vf', 'crop=%d:%d:%d:%d' % (w, h, x0, y0), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    im = Image.open(tmp).convert('RGB')
    m = bar_text_mask(im)
    if m.sum() < 12:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    im = im.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
    if im.size[1] > im.size[0]:
        im = im.rotate(-90, expand=True)
    hh = 34
    if im.size[1] != hh:
        im = im.resize((max(1, int(im.size[0] * hh / max(1, im.size[1]))), hh))
    return im


if __name__ == '__main__':
    main()
