"""b17b_mont.py - private helper for the Nirvana (b17b) batch.

Stacks a list of pill_*.png crops into one image so several strumming rows can
be read at once.
"""
import os

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
ROOT = 'frames'

ITEMS = [
    ('b17b_6MoufnQTB6U', 'p0'), ('b17b_6MoufnQTB6U', 'p1'), ('b17b_6MoufnQTB6U', 'p2'),
    ('b17b_6MoufnQTB6U', 'p3'), ('b17b_RhumXNv5uuE', 'p1'), ('b17b_RhumXNv5uuE', 'p2'),
    ('b17b_RhumXNv5uuE', 'p3'), ('b17b_CGKmmAPBwHw', 'p1'), ('b17b_CGKmmAPBwHw', 'p2'),
    ('b17b_CGKmmAPBwHw', 'p4'), ('b17b_3X_bVfjToV4', 'p0'), ('b17b_3X_bVfjToV4', 'p3'),
]
PREFIX = 'chord_'


def main():
    ims = []
    for d, f in ITEMS:
        p = os.path.join(ROOT, d, PREFIX + '%s.png' % f)
        if os.path.exists(p):
            ims.append((d + '/' + f, Image.open(p)))
    if not ims:
        print('NOTHING')
        return
    W = max(i.size[0] for _, i in ims)
    H = sum(i.size[1] + 18 for _, i in ims)
    c = Image.new('RGB', (W, H), (20, 20, 20))
    dr = ImageDraw.Draw(c)
    fo = ImageFont.truetype(F_BOLD, 14)
    y = 0
    for n, i in ims:
        dr.text((3, y + 2), n, font=fo, fill=(255, 210, 0))
        c.paste(i, (0, y + 18))
        y += i.size[1] + 18
    c.save(os.path.join(ROOT, 'b17b_probe', 'z', 'pills.png'))
    print(c.size, len(ims))


if __name__ == '__main__':
    main()
