"""b20d_tiles.py - private helper (batch b20d): dense small-thumbnail overview of
a whole video, to spot the frames where a TAB / chord panel appears.

Usage:
  py -3.14 b20d_tiles.py <id> <step> <cols> [start] [name]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    start = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    name = sys.argv[5] if len(sys.argv) > 5 else 'tiles.png'
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20d_%s' % vid
    os.makedirs(base, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    tmp = os.path.join(base, '_tile_tmp.png')
    tiles = []
    t = start
    while t < dur:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], capture_output=True)
        if os.path.exists(tmp):
            im = Image.open(tmp).convert('RGB')
            tw = 420
            tiles.append((t, im.resize((tw, int(im.size[1] * tw / im.size[0])))))
        t += step
    if not tiles:
        print('NO TILES')
        return
    th = tiles[0][1].size[1]
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (tiles[0][1].size[0] + 8) + 8
    H = rows * (th + 24) + 8
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 16)
    for i, (t, im) in enumerate(tiles):
        cx = 8 + (i % cols) * (im.size[0] + 8)
        cy = 8 + (i // cols) * (th + 24)
        d.text((cx + 3, cy + 2), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 20))
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size, len(tiles))


if __name__ == '__main__':
    main()
