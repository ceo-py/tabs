"""b20b_intro.py - private helper (batch b20b): stack the score-sheet header
(tempo / capo / first bars) of several videos into one image.

Usage: py -3.14 b20b_intro.py <id>:<top>[:<t>] [...]
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
    items = []
    for a in sys.argv[1:]:
        parts = a.split(':')
        vid = parts[0]
        top = int(parts[1])
        t = float(parts[2]) if len(parts) > 2 else 5.0
        items.append((vid, top, t))
    rows = []
    for vid, top, t in items:
        base = BASE % vid
        os.makedirs(base, exist_ok=True)
        tmp = os.path.join(base, '_intro_tmp.png')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video_path(vid),
                        '-frames:v', '1', '-vf', 'crop=1920:200:0:%d' % top, tmp],
                       check=True, capture_output=True)
        rows.append((vid, t, Image.open(tmp).convert('RGB')))
    W = 1920
    H = len(rows) * (200 + 24) + 6
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (vid, t, im) in enumerate(rows):
        cy = 6 + i * (200 + 24)
        d.text((6, cy), '%s  t=%gs' % (vid, t), font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (0, cy + 22))
    out = 'frames/b20b_intro.png'
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
