"""b19b_mont.py - private helper: stack already-cropped panels into one sheet so
they can be inspected together.

Usage: py -3.14 b19b_mont.py <out.png> <img1> <img2> ...
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    out = sys.argv[1]
    paths = sys.argv[2:]
    tiles = []
    for p in paths:
        im = Image.open(p).convert('RGB')
        if im.size[0] > 1500:
            im = im.resize((1500, max(1, int(im.size[1] * 1500 / im.size[0]))))
        tiles.append((p, im))
    W = max(t.size[0] for _, t in tiles) + 16
    H = sum(t.size[1] + 26 for _, t in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for p, t in tiles:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), os.path.basename(p), font=fnt, fill=(255, 210, 0))
        canvas.paste(t, (8, y + 26))
        y += t.size[1] + 26
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
