"""b20b_csheet.py - private helper (batch b20b): crop one region of a video at
many timestamps and tile the crops into a labelled grid (like b19c_grid.py but
writes into the b20b namespace).

Usage: py -3.14 b20b_csheet.py <id> <x y w h> <t1> [t2 ...] [--name N] [--cols N]
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
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    args = sys.argv[6:]
    name, cols = 'csheet.png', 2
    times = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--name':
            name = args[i + 1]
            i += 2
            continue
        if a == '--cols':
            cols = int(args[i + 1])
            i += 2
            continue
        times.append(float(a))
        i += 1
    video = video_path(vid)
    base = BASE % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_csheet_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        tiles.append((t, Image.open(tmp).convert('RGB')))
    scale = 1180.0 / max(i.size[0] for _, i in tiles)
    tiles = [(t, im.resize((int(im.size[0] * scale), int(im.size[1] * scale))))
             for t, im in tiles]
    rows = (len(tiles) + cols - 1) // cols
    tw = max(im.size[0] for _, im in tiles)
    th = max(im.size[1] for _, im in tiles)
    W = cols * (tw + 12) + 12
    H = rows * (th + 28) + 12
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (t, im) in enumerate(tiles):
        cx = 12 + (i % cols) * (tw + 12)
        cy = 12 + (i // cols) * (th + 28)
        d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 27))
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
