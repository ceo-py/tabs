"""b19d_bar.py - private helper for batch b19d.

Scans a video for the on-screen section header and reports, for every distinct
header, its time range and the crop box of the panel underneath it.

Two header flavours are handled:

  bar  - a full width RED strip (white lettering).  Used by the Offspring /
         Verve / Tracy Chapman clips.  The strip is located in every frame by
         looking for rows where saturated red covers most of the width.
  red  - RED lettering on a dark background (Wheatus).  The letters are found
         by colour inside a given search window.

Usage:
  py -3.14 b19d_bar.py <video> <id> <mode> <x> <y> <w> <h> [step] [name]

mode 'bar': x y w h = the region that is allowed to contain the graphic
            (the strip is searched inside it).
mode 'red': x y w h = the window in which the red lettering lives.

Output: frames/b19d_<id>/<name>.png  and a printed table of groups.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def dur_of(video):
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())


def grab(video, t, box, tmp):
    x, y, w, h = box
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    return Image.open(tmp).convert('RGB')


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


def red_mask(a):
    return (a[..., 0] > 110) & (a[..., 1] < 100) & (a[..., 2] < 100)


def white_mask(a):
    return (a[..., 0] > 185) & (a[..., 1] > 185) & (a[..., 2] > 185)


def strip_of_white_in_red(im):
    """White glyphs of a red strip -> tight crop."""
    a = np.asarray(im).astype(np.int16)
    red = red_mask(a)
    white = white_mask(a)
    if red.sum() == 0:
        return None
    rows_red = red.sum(axis=1) > 0
    nrows = max(1, int(rows_red.sum()))
    keep = (red.sum(axis=0) / nrows) > 0.5
    if keep.sum() < 2:
        keep = (red.sum(axis=0) / nrows) > 0.2
    m = white.copy()
    if keep.sum() >= 2:
        m[:, ~keep] = False
    return tight(m, im)


def strip_of_red_text(im):
    """Red glyphs on a dark background -> tight crop."""
    a = np.asarray(im).astype(np.int16)
    m = red_mask(a)
    if m.sum() < 30:
        return None
    return tight(m, im)


def tight(m, im):
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    box = (cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1)
    return im.crop(box)


def sig_of(strip):
    if strip is None:
        return None
    a = np.asarray(strip.convert('L'))
    b = (a > 150)
    cols = bands(b.sum(axis=0) > 0, 1)
    rows = bands(b.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    b = b[rows[0][0]:rows[-1][1] + 1, cols[0][0]:cols[-1][1] + 1]
    return b


def same(a, b):
    if a is None or b is None or a.shape != b.shape:
        return False
    return int((a != b).sum()) <= 0.14 * a.size


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    mode = sys.argv[3]
    x, y, w, h = [int(v) for v in sys.argv[4:8]]
    step = float(sys.argv[8]) if len(sys.argv) > 8 else 2.0
    name = sys.argv[9] if len(sys.argv) > 9 else 'bars'
    base = 'frames/b19d_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = base + '/_bar_tmp.png'
    d = dur_of(video)
    hits = []
    for i in range(int(d / step) + 1):
        t = round(i * step, 2)
        if t > d - 0.2:
            break
        im = grab(video, t, (x, y, w, h), tmp)
        if im is None:
            continue
        if mode == 'bar':
            a = np.asarray(im).astype(np.int16)
            red = red_mask(a)
            rows = bands(red.sum(axis=1) > 0.55 * im.size[0], 6)
            if not rows:
                continue
            r0, r1 = rows[0]
            band = im.crop((0, r0, im.size[0], r1 + 1))
            s = strip_of_white_in_red(band)
            if s is None:
                continue
            hits.append((t, s, (x, y + r0, w, r1 - r0 + 1)))
        else:
            s = strip_of_red_text(im)
            if s is None:
                continue
            hits.append((t, s, (x, y, w, h)))
    if not hits:
        print('NO HITS', vid, mode)
        return
    groups = []
    for t, s, box in hits:
        sig = sig_of(s)
        if groups and same(sig, groups[-1]['sig']):
            groups[-1]['t1'] = t
            groups[-1]['strip'] = s
            groups[-1]['box'] = box
            continue
        groups.append({'t0': t, 't1': t, 'sig': sig, 'strip': s, 'box': box})
    merged = []
    for g in groups:
        if merged and g['t0'] - merged[-1]['t1'] <= step * 1.6 and same(g['sig'], merged[-1]['sig']):
            merged[-1]['t1'] = g['t1']
            merged[-1]['strip'] = g['strip']
            merged[-1]['box'] = g['box']
        else:
            merged.append(g)
    W = 1300
    canvas = Image.new('RGB', (W, 2000 * 60), (18, 18, 18))
    d2 = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for g in merged:
        d2.rectangle([0, y, W, y + 24], fill=(0, 0, 0))
        d2.text((5, y + 3), 't=%g-%g  bar=%s' % (g['t0'], g['t1'], g['box']),
                font=fnt, fill=(255, 210, 0))
        im = g['strip']
        sc = min(1.0, (W - 20) / im.size[0])
        if sc < 1.0:
            im = im.resize((int(im.size[0] * sc), max(1, int(im.size[1] * sc))))
        canvas.paste(im, (10, y + 25))
        y += 25 + im.size[1] + 3
    canvas.crop((0, 0, W, max(1, y))).save(base + '/%s.png' % name)
    print('%s %s groups=%d' % (vid, mode, len(merged)))
    for g in merged:
        print('  t=%g-%g bar=%s' % (g['t0'], g['t1'], g['box']))


if __name__ == '__main__':
    main()
