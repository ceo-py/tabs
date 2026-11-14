"""b14a_mont.py - private helper: crop the chosen panels of one video and stack
them into a single montage so they can be checked with one image read.

Usage:
    py -3.14 b14a_mont.py <video> <id> "t:x,y,w,h|LABEL" ["t:x,y,w,h|LABEL" ...]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 1200


def main():
    video, vid = sys.argv[1], sys.argv[2]
    base = 'frames/b14a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tiles = []
    for spec in sys.argv[3:]:
        head, label = spec.split('|')
        t, box = head.split(':')
        x, y, w, h = [int(v) for v in box.split(',')]
        png = os.path.join(base, '_m_%s.png' % t)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i', video,
                        '-frames:v', '1', '-vf',
                        'crop=%d:%d:%d:%d' % (w, h, x, y), png], check=True)
        im = Image.open(png).convert('RGB')
        if im.size[0] > TILE_W:
            im = im.resize((TILE_W, max(1, int(im.size[1] * TILE_W / im.size[0]))))
        tiles.append((t, label, im))
    W = TILE_W + 16
    H = sum(t[2].size[1] + 30 for t in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, label, im in tiles:
        d.rectangle([0, y, W, y + 29], fill=(0, 0, 0))
        d.text((5, y + 4), 't=%s  %s' % (t, label), font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (8, y + 30))
        y += im.size[1] + 30
    out = os.path.join(base, 'mont.png')
    canvas.save(out)
    print(out)


if __name__ == '__main__':
    main()
