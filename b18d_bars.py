"""b18d_bars.py - private helper for the b18d batch.

The on-screen header bar of these videos is a full-width red strip that carries
the section name(s).  Two shapes exist:

  * a single CENTRED section name (stable state of the section)
  * "CURRENT > NEXT" during the hand-over between two sections, plus a
    "1st Chord | X" marker on the far right

This scanner samples the bar every N seconds, keeps only the WHITE lettering
(all of it, not just the longest run) and stacks the result into one image so
the whole timeline can be read in a single look.

Usage: py -3.14 b18d_bars.py <video> <id> [step] [max_rows]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
BAR = (0, 470, 1920, 220)   # wide search window around the red header strip


def dur_of(video):
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())


def grab(video, t, box, out):
    x, y, w, h = box
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(out):
        return None
    im = Image.open(out).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    red = (a[..., 0] > 110) & (a[..., 1] < 100) & (a[..., 2] < 100)
    rows = np.where(red.sum(axis=1) > 0.4 * im.size[0])[0]
    if rows.size == 0:
        return None
    r0, r1 = rows[0], rows[-1]
    band = a[r0:r1 + 1]
    white = (band[..., 0] > 185) & (band[..., 1] > 185) & (band[..., 2] > 185)
    cols = np.where(white.sum(axis=0) > 0)[0]
    wrows = np.where(white.sum(axis=1) > 0)[0]
    if cols.size == 0 or wrows.size == 0:
        return None
    im = im.crop((max(0, cols[0] - 6), max(0, r0 + wrows[0] - 4),
                  min(im.size[0], cols[-1] + 7),
                  min(im.size[1], r0 + wrows[-1] + 5)))
    return im


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    step = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    max_rows = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    base = 'frames/b18d_%s' % vid
    os.makedirs(base, exist_ok=True)
    d = dur_of(video)
    times = [round(x, 2) for x in np.arange(0.5, d - 0.3, step)]
    if len(times) > max_rows:
        idx = np.linspace(0, len(times) - 1, max_rows).round().astype(int)
        times = [times[i] for i in idx]
    tmp = base + '/_bar.png'
    rows = []
    for t in times:
        im = grab(video, t, BAR, tmp)
        if im is not None:
            rows.append((t, im))
    if not rows:
        print('NO BARS', vid)
        return
    W = 1300
    canvas = Image.new('RGB', (W, 1500 * 40), (18, 18, 18))
    d2 = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 17)
    y = 0
    for t, im in rows:
        d2.rectangle([0, y, W, y + 23], fill=(0, 0, 0))
        d2.text((5, y + 3), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        sc = min(1.0, (W - 20) / im.size[0])
        if sc < 1.0:
            im = im.resize((int(im.size[0] * sc), max(1, int(im.size[1] * sc))))
        canvas.paste(im, (10, y + 24))
        y += 24 + im.size[1] + 2
    canvas.crop((0, 0, W, y)).save(base + '/bars.png')
    print('%s bar rows=%d' % (vid, len(rows)))


if __name__ == '__main__':
    main()
