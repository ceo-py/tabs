"""b21a_sweep.py - private helper (namespace b21a): sweep a horizontal band of
the video (the chord-name row) over the whole video and stack the frames so
every chord name that appears on screen can be read.

Usage:
  py -3.14 b21a_sweep.py <id> <y> <h> <step> <start> <end> <name> [zoom]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    y, h, step = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    start, end = float(sys.argv[5]), float(sys.argv[6])
    name = sys.argv[7]
    zoom = float(sys.argv[8]) if len(sys.argv) > 8 else 2.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sweep_tmp.png')
    rows = []
    t = start
    while t <= end:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', '-vf',
               'crop=1280:%d:0:%d,scale=%d:%d:flags=lanczos'
               % (h, y, int(1280 * zoom), int(h * zoom))]
        subprocess.run(cmd + [tmp], check=True, capture_output=True)
        rows.append((t, Image.open(tmp).convert('RGB')))
        t += step
    lw = 26
    W = max(i.size[0] for _, i in rows) + lw
    H = sum(i.size[1] for _, i in rows) + len(rows) * 22
    c = Image.new('RGB', (W, H), (20, 20, 20))
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(F_BOLD, 18)
    yy = 0
    for t, i in rows:
        d.text((2, yy + 2), '%ds' % t, font=f, fill=(255, 210, 0))
        yy += 22
        c.paste(i, (lw, yy))
        yy += i.size[1]
    out = os.path.join(base, name + '.png')
    c.save(out)
    print(out, c.size, len(rows))


if __name__ == '__main__':
    main()
