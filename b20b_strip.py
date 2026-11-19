"""b20b_strip.py - private helper (batch b20b): crop the chord-name strip
(top of the white score sheet) of a video at several timestamps and stack the
strips into one readable image, so the chord letters can be read exactly.

Usage:
  py -3.14 b20b_strip.py <id> <top1>:<t1> <top2>:<t2> [...] [--name N]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = 'frames/b20b_%s'


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for ' + vid)


def main():
    vid = sys.argv[1]
    args = sys.argv[2:]
    name = 'strip.png'
    if '--name' in args:
        i = args.index('--name')
        name = args[i + 1]
        args = args[:i] + args[i + 2:]
    items = []
    for a in args:
        top, t = a.split(':')
        items.append((int(top), float(t)))
    video = video_path(vid)
    base = BASE % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_strip_tmp.png')
    strips = []
    for top, t in items:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=1920:150:0:%d' % top, tmp],
                       check=True, capture_output=True)
        strips.append((t, Image.open(tmp).convert('RGB')))
    W = 1920
    H = len(strips) * (150 + 26) + 6
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (t, im) in enumerate(strips):
        cy = 6 + i * (150 + 26)
        d.text((6, cy), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (0, cy + 24))
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
