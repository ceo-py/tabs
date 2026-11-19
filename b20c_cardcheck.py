"""b20c_cardcheck.py - private helper (batch b20c): split the rendered cards
into a header strip (title / subtitle), a footer strip (link + source + note)
and a scaled overview, so that every card can be inspected visually.

Usage: py -3.14 b20c_cardcheck.py
"""
import os

from PIL import Image

CARDS = [
    'out_gz/Oasis-Lyla.png',
    'out_gz/Oasis-Songbird.png',
    'out_gz/Oasis-Roll-With-It.png',
    'out_gz/Oasis-Stay-Young.png',
]

HDR_H = 250
FOOT_H = 300
OUT = 'frames/b20c_edge'


def strip(paths, box, name):
    ims = []
    for p in paths:
        im = Image.open(p).convert('RGB')
        if box == 'head':
            ims.append(im.crop((0, 0, im.size[0], HDR_H)))
        else:
            ims.append(im.crop((0, im.size[1] - FOOT_H, im.size[0], im.size[1])))
    W = max(i.size[0] for i in ims)
    H = sum(i.size[1] + 6 for i in ims)
    canvas = Image.new('RGB', (W, H), (0, 0, 0))
    y = 0
    for i in ims:
        canvas.paste(i, (0, y))
        y += i.size[1] + 6
    out = os.path.join(OUT, name)
    canvas.save(out)
    print(out, canvas.size)


def overview(paths):
    for p in paths:
        im = Image.open(p).convert('RGB')
        w = 1000
        h = int(im.size[1] * w / im.size[0])
        im2 = im.resize((w, h), Image.LANCZOS)
        out = os.path.join(OUT, 'ov_' + os.path.basename(p))
        im2.save(out)
        print(out, im2.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    strip(CARDS, 'head', 'cards_head.png')
    strip(CARDS, 'foot', 'cards_foot.png')
    overview(CARDS)


if __name__ == '__main__':
    main()
