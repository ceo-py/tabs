"""b17b_grid.py - private helper for the Nirvana (b17b) batch.

Samples the video, crops a fixed region from every sample and tiles the crops
into a GRID (several columns) so a whole video's notation can be read from one
image.  Each tile carries its timestamp.

    py -3.14 b17b_grid.py <video> <id> <x> <y> <w> <h> <step> <cols> <name>

Writes frames/b17b_<id>/grid_<name>.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 470


def main():
    video, vid = sys.argv[1], sys.argv[2]
    x, y, w, h = (int(v) for v in sys.argv[3:7])
    step = float(sys.argv[7])
    cols = int(sys.argv[8])
    name = sys.argv[9]
    base = 'frames/b17b_%s' % vid
    tmpd = base + '/pg_' + name
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f' % step, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))

    tiles = []
    for i, f in enumerate(files):
        out = os.path.join(tmpd, 'c_%04d.png' % i)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f, '-frames:v', '1',
                        '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out],
                       check=True, capture_output=True)
        if not os.path.exists(out):
            continue
        im = Image.open(out).convert('RGB')
        if im.size[0] > TILE_W:
            im = im.resize((TILE_W, max(1, int(im.size[1] * TILE_W / im.size[0]))))
        tiles.append((round(i * step, 2), im))

    if not tiles:
        print('NO TILES', vid, name)
        return
    tw = max(t.size[0] for _, t in tiles)
    th = max(t.size[1] for _, t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (tw + 6)
    H = rows * (th + 22)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 15)
    for i, (t, im) in enumerate(tiles):
        cx = (i % cols) * (tw + 6)
        cy = (i // cols) * (th + 22)
        d.rectangle([cx, cy, cx + tw, cy + 20], fill=(0, 0, 0))
        d.text((cx + 3, cy + 2), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 21))
    canvas.save(base + '/grid_%s.png' % name)
    print('%s grid_%s tiles=%d size=%s' % (vid, name, len(tiles), canvas.size))


if __name__ == '__main__':
    main()
