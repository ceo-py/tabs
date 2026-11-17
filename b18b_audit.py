"""b18b_audit.py - build one audit sheet per card: header + whole card + footer.

The rendered cards are ~5000 px tall, so the read tool would shrink them far
too much.  The audit sheet stacks a full-width header strip, a scaled copy of
the whole card and a full-width footer strip into one image that stays legible.

Usage: py -3.14 b18b_audit.py <card.png> [<card.png> ...]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
HDR = 320
FTR = 380
FULL_W = 640


def audit(path):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    head = im.crop((0, 0, W, HDR)).resize((1400, int(HDR * 1400 / W)))
    foot = im.crop((0, H - FTR, W, H)).resize((1400, int(FTR * 1400 / W)))
    full = im.resize((FULL_W, int(H * FULL_W / W)))
    out = Image.new('RGB', (1400, head.size[1] + full.size[1] + foot.size[1] + 60),
                    (40, 40, 40))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(F_BOLD, 20)
    y = 0
    d.text((6, y + 2), 'HEADER  ' + os.path.basename(path), font=f, fill=(255, 210, 0))
    y += 26
    out.paste(head, (0, y))
    y += head.size[1] + 4
    d.text((6, y + 2), 'FULL CARD  %dx%d' % (W, H), font=f, fill=(255, 210, 0))
    y += 26
    out.paste(full, (400, y))
    y += full.size[1] + 4
    d.text((6, y + 2), 'FOOTER', font=f, fill=(255, 210, 0))
    y += 26
    out.paste(foot, (0, y))
    dest = 'frames/b18b_audit_%s.png' % os.path.splitext(os.path.basename(path))[0]
    out.save(dest)
    print(dest, out.size)


for p in sys.argv[1:]:
    audit(p)
