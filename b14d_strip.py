"""b14d_strip.py - private helper: stack the vertical section-label strip over
time for the layout-B videos of the b14 batch.

Crops a given box at a fixed step over the whole video, rotates it upright and
stacks the crops vertically, each labelled with its timestamp.

Usage: py -3.14 b14d_strip.py <video> <id> --box x,y,w,h [--start 0] [--step 6] [--count 40]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
ROW_H = 34


def main():
    argv = sys.argv[1:]
    video, vid = argv[0], argv[1]
    box = None
    start, step, count = 0.0, 6.0, 40
    i = 2
    while i < len(argv):
        if argv[i] == '--box':
            box = [int(v) for v in argv[i + 1].split(',')]
            i += 2
        elif argv[i] == '--start':
            start = float(argv[i + 1]); i += 1
        elif argv[i] == '--step':
            step = float(argv[i + 1]); i += 1
        elif argv[i] == '--count':
            count = int(argv[i + 1]); i += 1
        else:
            i += 1
    base = 'frames/b14d_%s' % vid
    os.makedirs(base, exist_ok=True)
    x, y, w, h = box
    tmp = base + '/_strip.png'
    rot = '--rot' in argv
    argv = [a for a in argv if a != '--rot']
    rows = []
    for k in range(count):
        t = round(start + k * step, 1)
        r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                            '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            continue
        im = Image.open(tmp).convert('RGB')
        if rot:
            im = im.rotate(-90, expand=True)
        if im.size[1] != ROW_H:
            im = im.resize((max(1, int(im.size[0] * ROW_H / max(1, im.size[1]))), ROW_H))
        rows.append((t, im))
    if not rows:
        print('NO STRIPS', vid)
        return
    W = max(im.size[0] for _, im in rows) + 90
    H = sum(im.size[1] + 6 for _, im in rows)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, im in rows:
        d.text((5, y + 6), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (86, y))
        y += im.size[1] + 6
    out = os.path.join(base, 'strip.png')
    canvas.save(out)
    print('%s strips=%d -> %s' % (vid, len(rows), out))


if __name__ == '__main__':
    main()
