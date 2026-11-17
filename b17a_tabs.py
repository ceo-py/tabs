"""b17a_tabs.py - private helper for the Linkin Park cards.

The modern GuitarZero2HeroExpress videos put the TAB sheet on the right and
mark it with a tall saturated-red bar carrying the section name (rotated).
This finds every frame where such a bar is on screen, crops the lettering out
of it, turns it upright and stacks it with the timestamp.

Usage: py -3.14 b17a_tabs.py <video> <id> [interval] [x0]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b17a_survey import bands, size  # noqa: E402

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
    x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 1700
    base = 'frames/b17a_%s' % vid
    tmpd = base + '/tb'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f' % interval, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    SW, SH = size(video)
    hits = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 110) & (g < 100) & (b < 100)
        px = SW / im.size[0]
        cols = red.sum(axis=0)
        for cx0, cx1 in bands(cols > 0.10 * im.size[1], 3):
            if cx0 / px < x0:
                continue
            sub = red[:, cx0:cx1 + 1]
            rows = bands(sub.sum(axis=1) > 0.4 * (cx1 - cx0 + 1), 3)
            if not rows:
                continue
            y0, y1 = rows[0][0], rows[-1][1]
            if (y1 - y0) < 0.10 * im.size[1]:
                continue
            hits.append((i * interval, int(cx0 * px), int(y0 * py_of(SH, im.size[1])),
                         int((cx1 + 1 - cx0) * px),
                         int((y1 + 1 - y0) * py_of(SH, im.size[1]))))
            break
    # collapse consecutive hits with the same bar geometry
    uniq = []
    for h in hits:
        if uniq and abs(h[0] - uniq[-1][0]) <= interval * 1.1:
            continue
        uniq.append(h)
    tiles = []
    for t, bx0, by0, bw, bh in uniq:
        strip = strip_at(video, t, [bx0, by0, bw, bh], base)
        if strip is not None:
            tiles.append((t, strip))
    if not tiles:
        print('NO TAB BARS', vid)
        return
    W = max(s.size[0] for _, s in tiles) + 16
    H = sum(s.size[1] + 26 for _, s in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, s in tiles:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(s, (8, y + 26))
        y += s.size[1] + 26
    out = base + '/tabs.png'
    canvas.save(out)
    print('%s bars=%d -> %s %s' % (vid, len(tiles), out, canvas.size))


def py_of(SH, h):
    return SH / float(h)


def strip_at(video, t, bb, base):
    tmp = base + '/_strip.png'
    x0, y0, w, h = bb
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1',
           '-vf', 'crop=%d:%d:%d:%d' % (w, h, x0, y0), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    im = Image.open(tmp).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
    white = (r_ > 170) & (g_ > 170) & (b_ > 170)
    if white.sum() < 30:
        return None
    cols = bands(white.sum(axis=0) > 0, 1)
    rows = bands(white.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    im = im.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
    if im.size[1] > im.size[0]:
        im = im.rotate(-90, expand=True)
    h = 40
    if im.size[1] != h:
        im = im.resize((max(1, int(im.size[0] * h / max(1, im.size[1]))), h))
    return im


if __name__ == '__main__':
    main()
