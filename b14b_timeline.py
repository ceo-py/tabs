"""b14b_timeline.py - private helper: compact section-title timeline.

Crops the section-title region of the panel at a fixed step over the whole
video and lays the crops out in a GRID (several columns), so a whole video's
section timeline fits in one readable image.

Usage:
    py -3.14 b14b_timeline.py <video> <id> --box x,y,w,h [--start 0] [--step 4]
        [--count 60] [--cols 4] [--rot]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
CELL_H = 34
PAD = 6
COLS = 4


def main():
    argv = sys.argv[1:]
    video, vid = argv[0], argv[1]
    box = None
    start, step, count = 0.0, 4.0, 60
    cols = COLS
    i = 2
    while i < len(argv):
        if argv[i] == '--box':
            box = [int(v) for v in argv[i + 1].split(',')]
            i += 2
        elif argv[i] == '--start':
            start = float(argv[i + 1]); i += 2
        elif argv[i] == '--step':
            step = float(argv[i + 1]); i += 2
        elif argv[i] == '--count':
            count = int(argv[i + 1]); i += 2
        elif argv[i] == '--cols':
            cols = int(argv[i + 1]); i += 2
        else:
            i += 1
    base = 'frames/b14b_%s' % vid
    os.makedirs(base, exist_ok=True)
    x, y, w, h = box
    tmp = base + '/_tl.png'
    rot = '--rot' in argv
    cells = []
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
        if im.size[1] != CELL_H:
            im = im.resize((max(1, int(im.size[0] * CELL_H / max(1, im.size[1]))), CELL_H))
        cells.append((t, im))
    if not cells:
        print('NO CELLS', vid)
        return
    tw = max(im.size[0] for _, im in cells)
    rows = (len(cells) + cols - 1) // cols
    cw = tw + 78
    ch = CELL_H + PAD
    canvas = Image.new('RGB', (cols * cw + 8, rows * ch + 8), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 16)
    for n, (t, im) in enumerate(cells):
        r, c = divmod(n, cols)
        x0 = 8 + c * cw
        y0 = 8 + r * ch
        d.text((x0 + 3, y0 + 6), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (x0 + 70, y0))
    out = os.path.join(base, 'timeline.png')
    canvas.save(out)
    print('%s cells=%d -> %s %s' % (vid, len(cells), out, canvas.size))


if __name__ == '__main__':
    main()
