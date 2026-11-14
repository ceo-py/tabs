"""b14d_timeline.py - private helper: accurate section-title timeline for the
layout-A videos of the b14 batch (horizontal red header bar above the sheet).

Crops the CENTRE of the red header bar (where the title is drawn) at a fixed
step over the whole video and stacks the crops, each labelled with its
timestamp.  Reading that one image gives the exact section boundaries.

Usage:
  py -3.14 b14d_timeline.py <video> <id> --bar x,y,w,h [--start 0] [--step 4]
                                   [--count 80] [--frac 0.4]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
ROW_H = 40


def main():
    argv = sys.argv[1:]
    video, vid = argv[0], argv[1]
    bar = None
    start, step, count, frac = 0.0, 4.0, 80, 0.45
    i = 2
    while i < len(argv):
        if argv[i] == '--bar':
            bar = [int(v) for v in argv[i + 1].split(',')]
            i += 2
        elif argv[i] == '--start':
            start = float(argv[i + 1]); i += 1
        elif argv[i] == '--step':
            step = float(argv[i + 1]); i += 1
        elif argv[i] == '--count':
            count = int(argv[i + 1]); i += 1
        elif argv[i] == '--frac':
            frac = float(argv[i + 1]); i += 1
        else:
            i += 1
    base = 'frames/b14d_%s' % vid
    os.makedirs(base, exist_ok=True)
    x, y, w, h = bar
    cw = int(w * frac)
    cx = x + (w - cw) // 2
    tmp = base + '/_tl.png'
    rows = []
    for k in range(count):
        t = round(start + k * step, 1)
        r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                            '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (cw, h, cx, y), tmp],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            continue
        im = Image.open(tmp).convert('RGB')
        if im.size[1] != ROW_H:
            im = im.resize((max(1, int(im.size[0] * ROW_H / max(1, im.size[1]))), ROW_H))
        rows.append((t, im))
    if not rows:
        print('NO ROWS', vid)
        return
    W = max(im.size[0] for _, im in rows) + 90
    H = sum(im.size[1] + 4 for _, im in rows)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, im in rows:
        d.text((5, y + 8), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (86, y))
        y += im.size[1] + 4
    out = os.path.join(base, 'timeline.png')
    canvas.save(out)
    print('%s rows=%d -> %s' % (vid, len(rows), out))


if __name__ == '__main__':
    main()
