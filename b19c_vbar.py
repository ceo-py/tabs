"""b19c_vbar.py - private helper (batch b19c): scan a vertical red side bar for
the section title, e.g. Slipknot's right-hand "BREAK LEAD" / "POST CHORUS RIFF".

Usage: py -3.14 b19c_vbar.py <id> <x> <y> <w> <h> <t1> [t2 ...]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    times = [float(a) for a in sys.argv[6:]]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b19c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_vbar_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB').rotate(-90, expand=True)
        tiles.append((t, im))
    tw = max(i.size[0] for _, i in tiles)
    th = max(i.size[1] for _, i in tiles)
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (tw + 12) + 12
    H = rows * (th + 30) + 12
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (t, im) in enumerate(tiles):
        cx = 12 + (i % cols) * (tw + 12)
        cy = 12 + (i // cols) * (th + 30)
        d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 28))
    out = os.path.join(base, 'vbar.png')
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
