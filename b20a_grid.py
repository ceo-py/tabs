"""b20a_grid.py - private helper (batch b20a): crop a region, upscale it and
draw a labelled pixel grid on top so coordinates can be read off the image.

Usage:
  py -3.14 b20a_grid.py <id> <t> <x y w h> <scale> [name] [grid_step]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    t = float(sys.argv[2])
    x, y, w, h = [int(v) for v in sys.argv[3:7]]
    scale = int(sys.argv[7]) if len(sys.argv) > 7 else 4
    name = sys.argv[8] if len(sys.argv) > 8 else 'grid'
    step = int(sys.argv[9]) if len(sys.argv) > 9 else 20
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_grid_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                   check=True, capture_output=True)
    im = Image.open(tmp).convert('RGB').resize((w * scale, h * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(F_BOLD, 16)
    for gx in range(0, w + 1, step):
        d.line([(gx * scale, 0), (gx * scale, im.size[1])], fill=(255, 0, 0), width=1)
        d.text((gx * scale + 2, 2), str(x + gx), font=fnt, fill=(255, 0, 0))
    for gy in range(0, h + 1, step):
        d.line([(0, gy * scale), (im.size[0], gy * scale)], fill=(0, 160, 255), width=1)
        d.text((2, gy * scale + 2), str(y + gy), font=fnt, fill=(0, 140, 255))
    out = os.path.join(base, name + '.png')
    im.save(out)
    print(out, im.size)


if __name__ == '__main__':
    main()
