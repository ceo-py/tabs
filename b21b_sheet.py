"""b21b_sheet.py - private helper (namespace b21b): tile full frames or crops of
a video into one readable contact sheet (captions = timestamp).

Usage:
  py -3.14 b21b_sheet.py <id> <bbox x y w h> <t1> [t2 ...] [--name out.png] [--cols N]
  py -3.14 b21b_sheet.py <id> --full <t1> [t2 ...] [--name out.png] [--cols N]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    args = sys.argv[2:]
    full = False
    if args and args[0] == '--full':
        full = True
        args = args[1:]
    name = None
    cols = 2
    args2 = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--name':
            name = args[i + 1]
            i += 2
            continue
        if a == '--cols':
            cols = int(args[i + 1])
            i += 2
            continue
        args2.append(a)
        i += 1
    args = args2

    x = y = w = h = 0
    if not full:
        x, y, w, h = [int(v) for v in args[:4]]
        args = args[4:]
    times = []
    for a in args:
        try:
            times.append(float(a))
        except ValueError:
            name = name or a
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sheet_tmp.png')
    tiles = []
    for t in times:
        vf = 'crop=%d:%d:%d:%d' % (w, h, x, y) if not full else 'null'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', vf, tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        tiles.append((t, im))
    scale = 1180.0 / max(t.size[0] for _, t in tiles)
    tiles = [(t, im.resize((int(im.size[0] * scale), int(im.size[1] * scale))))
             for t, im in tiles]
    rows = (len(tiles) + cols - 1) // cols
    tw = max(t.size[0] for _, t in tiles)
    th = max(t.size[1] for _, t in tiles)
    W = cols * tw + (cols + 1) * 12
    H = rows * (th + 28) + 12
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 20)
    for i, (t, im) in enumerate(tiles):
        cx = 12 + (i % cols) * (tw + 12)
        cy = 12 + (i // cols) * (th + 28)
        d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 27))
    name = name or 'sheet.png'
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
