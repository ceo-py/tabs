"""b17b_ticks.py - private helper for the Nirvana (b17b) batch.

Stacks the small top-left overlays (the chord ticker that some GuitarZero2HeroExpress
videos keep on screen) so they can be read in one go.
"""
import os

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
ROOT = 'frames/b17b_probe/z'

FILES = ['li_ticker20.png', 'li_ticker140.png', 'hs_ticker40.png', 'sl_ticker10.png',
         'ag_ticker20.png', 'mw_ticker30.png', 'ca_ticker30.png']


def main():
    ims = [(f, Image.open(os.path.join(ROOT, f))) for f in FILES
           if os.path.exists(os.path.join(ROOT, f))]
    W = max(i.size[0] for _, i in ims)
    H = sum(i.size[1] + 18 for _, i in ims)
    c = Image.new('RGB', (W, H), (20, 20, 20))
    d = ImageDraw.Draw(c)
    fo = ImageFont.truetype(F_BOLD, 14)
    y = 0
    for n, i in ims:
        d.text((3, y + 2), n, font=fo, fill=(255, 210, 0))
        c.paste(i, (0, y + 18))
        y += i.size[1] + 18
    c.save(os.path.join(ROOT, 'ticks.png'))
    print(c.size)


if __name__ == '__main__':
    main()
