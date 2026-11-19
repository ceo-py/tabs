"""b21b_grid.py - private helper (namespace b21b): dense thumbnail grid of the
whole video to spot any on-screen notation overlay.

Usage:
  py -3.14 b21b_grid.py <id> <t0> <t1> <step> [--cols N] [--w 320] [--crop x y w h]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    a = float(sys.argv[2]); b = float(sys.argv[3]); step = float(sys.argv[4])
    rest = sys.argv[5:]
    cols, tw = 8, 320
    crop = None
    i = 0
    while i < len(rest):
        if rest[i] == '--cols':
            cols = int(rest[i + 1]); i += 2
        elif rest[i] == '--w':
            tw = int(rest[i + 1]); i += 2
        elif rest[i] == '--crop':
            crop = [int(v) for v in rest[i + 1:i + 5]]; i += 5
        else:
            i += 1
    base = 'frames/b21b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_grid_tmp.png')
    vf = 'null' if not crop else 'crop=%d:%d:%d:%d' % (crop[2], crop[3], crop[0], crop[1])
    tiles = []
    t = a
    while t <= b:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t,
                        '-i', 'dl/w4_%s.mp4' % vid, '-frames:v', '1', '-vf', vf, tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        sc = tw / im.size[0]
        tiles.append((t, im.resize((tw, int(im.size[1] * sc)))))
        t += step
    th = tiles[0][1].size[1]
    rows = (len(tiles) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * (tw + 4) + 4, rows * (th + 18) + 4), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 13)
    for i, (t, im) in enumerate(tiles):
        cx = 4 + (i % cols) * (tw + 4)
        cy = 4 + (i // cols) * (th + 18)
        d.text((cx + 2, cy), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 16))
    out = os.path.join(base, 'grid_%s_%g_%g.png' % (vid, a, b))
    canvas.save(out)
    print(out, canvas.size, len(tiles))


if __name__ == '__main__':
    main()
