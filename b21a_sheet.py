"""b21a_sheet.py - private helper (namespace b21a / G.S.N. Tabs).

Tile full-resolution frames of a video into one readable contact sheet
(captions = timestamp).  Same idea as b18c_sheet.py but writes into
frames/b21a_<id>/ so it stays inside this namespace.

Usage:
  py -3.14 b21a_sheet.py <id> <t1> [t2 ...] [--name x.png] [--cols 2]
                        [--crop x y w h]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    times, name, cols = [], 'sheet.png', 2
    crop = None
    a = sys.argv[2:]
    i = 0
    while i < len(a):
        tok = a[i]
        if tok == '--name':
            i += 1
            name = a[i]
        elif tok == '--cols':
            i += 1
            cols = int(a[i])
        elif tok == '--crop':
            i += 1
            crop = [int(v) for v in a[i].split(',')]
        elif tok == '--grid':
            pass
        else:
            times.append(float(tok))
        i += 1
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b21a_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sheet_tmp.png')
    grid = '--grid' in sys.argv
    tiles = []
    for t in times:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1']
        if crop:
            cmd += ['-vf', 'crop=%d:%d:%d:%d' % (crop[2], crop[3], crop[0], crop[1])]
        cmd += [tmp]
        subprocess.run(cmd, check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        if grid:
            from PIL import ImageDraw as _D
            d = _D.Draw(im)
            fn = ImageFont.truetype(F_BOLD, 14)
            ox = crop[1] if crop else 0
            for gy in range(0, im.size[1], 20):
                d.line([(0, gy), (im.size[0], gy)], fill=(255, 0, 0), width=1)
                d.text((2, gy + 1), str(ox + gy), font=fn, fill=(255, 0, 0))
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
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
