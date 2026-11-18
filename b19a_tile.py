"""b19a_tile.py - tile the already-extracted survey frames of a video
(frames/b19a_<id>/p/p_*.png) into one contact sheet with timestamps.

Usage: py -3.14 b19a_tile.py <id> [--cols N] [--name out.png]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    args = sys.argv[2:]
    cols = 6
    name = 'tile.png'
    i = 0
    while i < len(args):
        if args[i] == '--cols':
            cols = int(args[i + 1]); i += 2
        elif args[i] == '--name':
            name = args[i + 1]; i += 2
        else:
            i += 1
    base = 'frames/b19a_%s' % vid
    pd = os.path.join(base, 'p')
    files = sorted(f for f in os.listdir(pd) if f.endswith('.png'))
    tiles = []
    for n, f in enumerate(files):
        im = Image.open(os.path.join(pd, f)).convert('RGB')
        tiles.append((n * 4.0, im))
    tw = max(t.size[0] for _, t in tiles)
    th = max(t.size[1] for _, t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (tw + 8) + 8
    H = rows * (th + 24) + 8
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 16)
    for i, (t, im) in enumerate(tiles):
        cx = 8 + (i % cols) * (tw + 8)
        cy = 8 + (i // cols) * (th + 24)
        d.rectangle([cx, cy, cx + tw, cy + 21], fill=(0, 0, 0))
        d.text((cx + 4, cy + 2), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 22))
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
