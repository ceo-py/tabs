"""b21c_sheet.py - private helper: tile full-resolution crops of a video into
one readable contact sheet (captions = timestamp).

Usage:
  py -3.14 b21c_sheet.py <id> <bbox x y w h> <t1> [t2 ...] [--name x.png] [--cols 2]
  py -3.14 b21c_sheet.py <id> --full <t1> [t2 ...] [--name x.png] [--cols 2]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    argv = sys.argv[1:]
    name = None
    cols = 2
    if '--name' in argv:
        i = argv.index('--name')
        name = argv[i + 1]
        del argv[i:i + 2]
    if '--cols' in argv:
        i = argv.index('--cols')
        cols = int(argv[i + 1])
        del argv[i:i + 2]

    vid = argv[0]
    if argv[1] == '--full':
        bbox = (0, 0, 1920, 1080)
        times = [float(a) for a in argv[2:]]
    else:
        x, y, w, h = [int(v) for v in argv[1:5]]
        bbox = (x, y, w, h)
        times = [float(a) for a in argv[5:]]

    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sheet_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (bbox[2], bbox[3], bbox[0], bbox[1]), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        tiles.append((t, im))
    scale = 1180.0 / max(t.size[0] for _, t in tiles)
    tiles = [(t, im.resize((int(im.size[0] * scale), int(im.size[1] * scale))))
             for t, im in tiles]
    rows = (len(tiles) + cols - 1) // cols
    tw = max(t.size[0] for _, t in tiles)
    th = max(t.size[1] for _, t in tiles)
    W = cols * tw + (cols + 1) * 12
    H = rows * (th + 28) + 12
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 20)
    for i, (t, im) in enumerate(tiles):
        cx = 12 + (i % cols) * (tw + 12)
        cy = 12 + (i // cols) * (th + 28)
        d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 27))
    name = name or 'sheet.png'
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
