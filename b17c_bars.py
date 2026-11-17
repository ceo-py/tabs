"""b17c_bars.py - one sheet that shows the section-title bar of the video at
every sampled second, so the exact section timestamps can be read off.

Layout A (wide horizontal bar) and layout B (narrow vertical bar) are both
supported; the vertical bar is rotated upright.

Usage: py -3.14 b17c_bars.py <video> <id> [interval]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b17c_scan import analyze  # noqa: E402

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    video, vid = sys.argv[1], sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    base = 'frames/b17c_%s' % vid
    tmpd = base + '/s'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=480:-1' % interval,
                    os.path.join(tmpd, 'b_%04d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd)
                   if f.startswith('b_') and f.endswith('.png'))
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                         capture_output=True, text=True).stdout.strip().split(',')
    SW, SH = int(out[0]), int(out[1])

    tiles = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        info = analyze(im, SW, SH)
        if not info:
            continue
        bar = info['bar']
        tmp = base + '/_b.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % (i * interval),
                        '-i', video, '-frames:v', '1', '-vf',
                        'crop=%d:%d:%d:%d' % (bar[2], bar[3], bar[0], bar[1]), tmp],
                       capture_output=True)
        if not os.path.exists(tmp):
            continue
        b = Image.open(tmp).convert('RGB')
        if b.size[1] > b.size[0]:
            b = b.rotate(-90, expand=True)
        h = 34
        if b.size[1] != h:
            b = b.resize((max(1, int(b.size[0] * h / max(1, b.size[1]))), h))
        tiles.append((i * interval, b))
    if not tiles:
        print('no bars for', vid)
        return
    Wl = max(b.size[0] for _, b in tiles) + 16
    Hl = sum(b.size[1] + 28 for _, b in tiles) + 8
    canvas = Image.new('RGB', (Wl, Hl), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 4
    for t, b in tiles:
        d.text((6, y), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(b, (6, y + 22))
        y += b.size[1] + 28
    canvas.save(base + '/bars.png')
    print('%s bars=%d -> %s' % (vid, len(tiles), base + '/bars.png'))


if __name__ == '__main__':
    main()
