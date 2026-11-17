"""b17b_ticks2.py - private helper for the Nirvana (b17b) batch.

Stacks the top-left chord-ticker crops taken at several timestamps so it can
be checked whether the ticker changes during the song.
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
ROOT = 'frames/b17b_probe/z/t'


def main():
    fs = sorted(glob.glob(os.path.join(ROOT, 'li_*.png'))) + \
        sorted(glob.glob(os.path.join(ROOT, 'hs_*.png')))
    ims = [(os.path.basename(p), Image.open(p)) for p in fs]
    W = max(i.size[0] for _, i in ims)
    H = sum(i.size[1] + 16 for _, i in ims)
    c = Image.new('RGB', (W, H), (20, 20, 20))
    d = ImageDraw.Draw(c)
    fo = ImageFont.truetype(F_BOLD, 13)
    y = 0
    for n, i in ims:
        d.text((3, y + 1), n, font=fo, fill=(255, 210, 0))
        c.paste(i, (0, y + 16))
        y += i.size[1] + 16
    c.save('frames/b17b_probe/z/ticks2.png')
    print(c.size)


if __name__ == '__main__':
    main()
