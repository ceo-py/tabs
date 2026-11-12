"""Tile a set of crop images into one labelled montage for visual verification.

Usage:
  py -3.14 vcheck.py <out.png> <tile_width> <img1> <img2> ...
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont


def main():
    out = sys.argv[1]
    tilew = int(sys.argv[2])
    paths = sys.argv[3:]
    tiles = []
    for p in paths:
        im = Image.open(p).convert('RGB')
        h = int(im.size[1] * tilew / im.size[0])
        tiles.append((p, im.resize((tilew, h))))
    if not tiles:
        print('NO IMAGES')
        return
    cols = 3
    maxh = max(t[1].size[1] for t in tiles)
    LAB = 26
    rows = (len(tiles) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * tilew, rows * (maxh + LAB)), (25, 25, 30))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
    for i, (p, im) in enumerate(tiles):
        x = (i % cols) * tilew
        y = (i // cols) * (maxh + LAB)
        canvas.paste(im, (x, y))
        d.rectangle([x, y + maxh, x + tilew, y + maxh + LAB], fill=(0, 0, 0))
        d.text((x + 5, y + maxh + 3), os.path.basename(p), font=fnt, fill=(255, 220, 0))
    canvas.save(out)
    print('saved', out, canvas.size, len(tiles))


main()
