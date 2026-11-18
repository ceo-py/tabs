"""b19c_grid.py - private helper (batch b19c): crop one region of a video at
many timestamps and tile the results in a labelled grid (no rotation).

Usage: py -3.14 b19c_grid.py <id> <x y w h> <t1> [t2 ...] [name]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    times, name = [], None
    for a in sys.argv[6:]:
        try:
            times.append(float(a))
        except ValueError:
            name = a
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b19c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_grid_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        tiles.append((t, Image.open(tmp).convert('RGB')))
    scale = min(3.0, 1400.0 / max(i.size[0] for _, i in tiles))
    tiles = [(t, i.resize((int(i.size[0] * scale), int(i.size[1] * scale))))
             for t, i in tiles]
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    tw = max(i.size[0] for _, i in tiles)
    th = max(i.size[1] for _, i in tiles)
    W = cols * (tw + 10) + 10
    H = rows * (th + 26) + 10
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 18)
    for i, (t, im) in enumerate(tiles):
        cx = 10 + (i % cols) * (tw + 10)
        cy = 10 + (i // cols) * (th + 26)
        d.rectangle([cx, cy, cx + tw, cy + 24], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 25))
    name = name or 'grid.png'
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
