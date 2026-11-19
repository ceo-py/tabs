"""b20c_edgecmp.py - private helper (batch b20c): stack the sheet/footage
boundary region of several videos into one image so the split row can be read
off directly.

Usage: py -3.14 b20c_edgecmp.py <y0> <y1> <t> <id1> <id2> ...
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    y0, y1, t = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    ids = sys.argv[4:]
    base = 'frames/b20c_edge'
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_e.png')
    crops = []
    for vid in ids:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i',
                        'dl/w4_%s.mp4' % vid, '-frames:v', '1', '-vf',
                        'crop=1920:%d:0:%d' % (y1 - y0, y0), tmp],
                       check=True, capture_output=True)
        crops.append((vid, Image.open(tmp).convert('RGB')))
    W = 1920
    H = sum(c.size[1] + 30 for _, c in crops)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 22)
    y = 0
    for vid, c in crops:
        d.rectangle([0, y, W, y + 27], fill=(0, 0, 0))
        d.text((6, y + 3), '%s  t=%g  rows %d..%d' % (vid, t, y0, y1),
               font=fnt, fill=(255, 210, 0))
        canvas.paste(c, (0, y + 28))
        y += c.size[1] + 30
    out = os.path.join(base, 'edge.png')
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
