"""b17b_strip.py - private helper for the Nirvana (b17b) batch.

Tiles a FIXED crop region of the video over time into one montage image, so a
non-standard on-screen element (e.g. Polly's red section word in the top-right
title block) can be read off a single image.

    py -3.14 b17b_strip.py <video> <id> <x> <y> <w> <h> [step]

Writes frames/b17b_<id>/strip.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    video, vid = sys.argv[1], sys.argv[2]
    x, y, w, h = (int(v) for v in sys.argv[3:7])
    step = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
    base = 'frames/b17b_%s' % vid
    tmpd = base + '/ps'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f' % step, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))

    tiles = []
    for i, f in enumerate(files):
        out = os.path.join(tmpd, 'c_%04d.png' % i)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f, '-frames:v', '1',
                        '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out],
                       check=True, capture_output=True)
        if os.path.exists(out):
            tiles.append((round(i * step, 2), Image.open(out).convert('RGB')))

    Wt = max(s.size[0] for _, s in tiles) + 16
    Ht = sum(s.size[1] + 24 for _, s in tiles)
    canvas = Image.new('RGB', (Wt, Ht), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 17)
    y2 = 0
    for t, s in tiles:
        d.rectangle([0, y2, Wt, y2 + 23], fill=(0, 0, 0))
        d.text((5, y2 + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(s, (8, y2 + 24))
        y2 += s.size[1] + 24
    canvas.save(base + '/strip.png')
    print('%s strip tiles=%d' % (vid, len(tiles)))


if __name__ == '__main__':
    main()
