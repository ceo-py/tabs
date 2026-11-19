"""b20b_chord.py - private helper (batch b20b): crop the CHORD-NAME band of the
score sheet at many timestamps and stack the bands into one labelled sheet, so
the chord names of a whole video can be read in a couple of looks.

Usage:
  py -3.14 b20b_chord.py <id> <y> <h> <t1> [t2 ...] [--name NAME] [--width W]
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
    y, h = int(sys.argv[2]), int(sys.argv[3])
    args = sys.argv[4:]
    name, width = 'chordband.png', 1500
    times = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--name':
            name = args[i + 1]
            i += 2
            continue
        if a == '--width':
            width = int(args[i + 1])
            i += 2
            continue
        times.append(float(a))
        i += 1
    video = video_path(vid)
    base = BASE % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_chord_tmp.png')
    tiles = []
    for t in times:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=1920:%d:0:%d' % (h, y), tmp],
                       check=True, capture_output=True)
        tiles.append((t, Image.open(tmp).convert('RGB')))
    scale = float(width) / max(im.size[0] for _, im in tiles)
    tiles = [(t, im.resize((int(im.size[0] * scale), max(1, int(im.size[1] * scale)))))
             for t, im in tiles]
    tw = max(im.size[0] for _, im in tiles)
    th = max(im.size[1] for _, im in tiles)
    W = tw + 16
    H = len(tiles) * (th + 26) + 16
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (t, im) in enumerate(tiles):
        cy = 12 + i * (th + 26)
        d.rectangle([8, cy, 8 + tw, cy + 24], fill=(0, 0, 0))
        d.text((12, cy + 2), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (8, cy + 25))
    if not name.lower().endswith('.png'):
        name += '.png'
    out = os.path.join(base, name)
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
