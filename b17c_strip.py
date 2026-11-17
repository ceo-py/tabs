"""b17c_strip.py - tile a fixed crop of the video over a time range (my namespace).

Usage: py -3.14 b17c_strip.py <video> <out.png> <t0> <t1> <step> <x> <y> <w> <h> [cols]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    video, out = sys.argv[1], sys.argv[2]
    t0, t1, step = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    x, y, w, h = (int(v) for v in sys.argv[6:10])
    cols = int(sys.argv[10]) if len(sys.argv) > 10 else 4
    tmp = out + '.tmp.png'
    tiles = []
    t = t0
    while t <= t1:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       capture_output=True)
        if os.path.exists(tmp):
            im = Image.open(tmp).convert('RGB')
            sw = 460
            im = im.resize((sw, max(1, int(im.size[1] * sw / im.size[0]))))
            tiles.append((t, im))
        t += step
    if not tiles:
        print('none')
        return
    rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0][1].size
    canvas = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + 30) + 8), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    for i, (t, im) in enumerate(tiles):
        cx = 8 + (i % cols) * (tw + 8)
        cy = 8 + (i // cols) * (th + 30)
        d.text((cx, cy), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 22))
    canvas.save(out)
    print('%s tiles=%d size=%s' % (out, len(tiles), canvas.size))


if __name__ == '__main__':
    main()
