"""b20d_sheet.py - private helper (batch b20d / Sparky Guitar): tile crops of a
video into one readable contact sheet (captions = timestamp).

Usage:
  py -3.14 b20d_sheet.py <id> <bbox x y w h> <t1> [t2 ...] [name]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


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
    base = 'frames/b20d_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_sheet_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        tiles.append((t, im))
    scale = 1180.0 / max(t.size[0] for _, t in tiles)
    tiles = [(t, im.resize((int(im.size[0] * scale), int(im.size[1] * scale))))
             for t, im in tiles]
    cols = 2
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
