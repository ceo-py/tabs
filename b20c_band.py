"""b20c_band.py - private helper (batch b20c, channel 'ike'): montage the chord
row band of the scrolling score over the whole video so that every printed
chord label can be read.

Usage: py -3.14 b20c_band.py <id> <y0> <y1> <t_start> <t_end> <step> <out.png>
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    y0 = int(sys.argv[2])
    y1 = int(sys.argv[3])
    t0 = sys.argv[4]
    t1 = float(sys.argv[5])
    step = float(sys.argv[6])
    out = sys.argv[7]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_band_tmp.png')

    rows = []
    if ',' in sys.argv[4]:
        times = [float(v) for v in sys.argv[4].split(',')]
    else:
        times = []
        t = t0
        while t <= t1:
            times.append(t)
            t += step
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf',
                        'crop=1920:%d:0:%d' % (y1 - y0, y0), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        rows.append((t, im))

    lblw = 70
    W = 1920 + lblw
    rh = (y1 - y0)
    H = rh * len(rows)
    canvas = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 26)
    y = 0
    for t, im in rows:
        d.text((4, y + 4), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (lblw, y))
        y += rh
    canvas.save(out)
    print(out, canvas.size, len(rows))


if __name__ == '__main__':
    main()
