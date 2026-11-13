"""b13_labels.py - private helper: list the on-screen section titles of a video.

Samples the video, finds the red section-title bar and renders every distinct
title at FULL resolution, upright, one row per sample time.  Reading that one
image tells me the sections of the video and when they appear.

Usage: py -3.14 b13_labels.py <video> <id> [max_rows]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13_survey import bar_text_mask, bands, red_bars, size  # noqa: E402

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
STEP = 6


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    max_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 18
    base = 'frames/b13_%s' % vid
    tmpd = base + '/pl'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%d,scale=480:-1' % STEP, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    SW, SH = size(video)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())

    hits = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 120) & (g < 95) & (b < 95)
        bars = red_bars(red, im.size[0], im.size[1])
        if not bars:
            continue
        px = SW / im.size[0]
        py = SH / im.size[1]
        bars.sort(key=lambda bb: -(bb[2] * bb[3]))
        bb = bars[0]
        if bb[3] > 0.8 * SH or bb[2] > 0.9 * SW:
            continue
        hits.append((i * STEP, [int(bb[0] * px), int(bb[1] * py),
                                int(bb[2] * px), int(bb[3] * py)]))

    # keep a bounded number of evenly spread samples
    if len(hits) > max_rows:
        step = len(hits) / float(max_rows)
        hits = [hits[int(k * step)] for k in range(max_rows)]

    tiles = []
    for t, bb in hits:
        strip = strip_at(video, t, bb, base)
        if strip is not None:
            tiles.append((t, strip))
    if not tiles:
        print('NO LABELS', vid)
        return
    W = max(s.size[0] for _, s in tiles) + 16
    H = sum(s.size[1] + 26 for _, s in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, s in tiles:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%ds' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(s, (8, y + 26))
        y += s.size[1] + 26
    canvas.save(base + '/labels.png')
    print('%s labels=%d  %s' % (vid, len(tiles), ' '.join(str(t) for t, _ in tiles)))


def strip_at(video, t, bb, base):
    tmp = base + '/_strip.png'
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
    h = 36
    if im.size[1] != h:
        im = im.resize((max(1, int(im.size[0] * h / max(1, im.size[1]))), h))
    return im


if __name__ == '__main__':
    main()
