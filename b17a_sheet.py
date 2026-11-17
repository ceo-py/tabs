"""b17a_sheet.py - private helper for the Linkin Park (batch 17) cards.

Builds a contact sheet out of video frames so the section titles, chord rows
and strumming patterns can be read straight from one image.

Usage:
  py -3.14 b17a_sheet.py <video> <id> [interval] [cols] [crop x,y,w,h]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 620


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    crop = None
    if len(sys.argv) > 5 and sys.argv[5].strip():
        crop = [int(v) for v in sys.argv[5].split(',')]
    suffix = sys.argv[6] if len(sys.argv) > 6 else ''
    tile_w = int(sys.argv[7]) if len(sys.argv) > 7 else TILE_W
    base = 'frames/b17a_%s' % vid
    tmpd = base + '/sh'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f' % interval, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    tiles = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        if crop:
            x, y, w, h = crop
            sw, sh = im.size
            im = im.crop((int(x * sw / 1920), int(y * sh / 1080),
                          int((x + w) * sw / 1920), int((y + h) * sh / 1080)))
        if im.size[0] > tile_w:
            im = im.resize((tile_w, max(1, int(im.size[1] * tile_w / im.size[0]))))
        tiles.append((i * interval, im))
    if not tiles:
        print('NO FRAMES', vid)
        return
    rows = (len(tiles) + cols - 1) // cols
    cw = max(t.size[0] for _, t in tiles) + 12
    ch = max(t.size[1] for _, t in tiles) + 26
    canvas = Image.new('RGB', (cols * cw + 8, rows * ch + 8), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 16)
    for k, (t, im) in enumerate(tiles):
        r, c = divmod(k, cols)
        x = 8 + c * cw
        y = 8 + r * ch
        d.text((x, y), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (x, y + 22))
    out = base + '/sheet%s.png' % suffix
    canvas.save(out)
    print('%s frames=%d -> %s %s' % (vid, len(tiles), out, canvas.size))


if __name__ == '__main__':
    main()
