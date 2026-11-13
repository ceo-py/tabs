"""b13_panels.py - private helper: montages of the on-screen overlay PANELS.

b13_survey.py pastes the detected section-label strip on top of the panel, which
hides the real section title printed in the red header bar of the panel itself.
This helper renders the panel crop alone (plus a caption with the timestamp), so
the section title, the chord names and the strumming pattern are readable.

Usage:
    py -3.14 b13_panels.py <video> <id> [t1 t2 ...]
    py -3.14 b13_panels.py <video> <id> --box x,y,w,h --times 10,40,80
    py -3.14 b13_panels.py <video> <id> --full --times 10,40,80   (whole frame)

Without timestamps the representative times of frames/b13_<id>/sections.json are
used and the crop box is the most common box of that file.  Output is written as
frames/b13_<id>/pm<k>.png, at most 4 panels per image so that everything stays
legible when the image is downscaled for reading.
"""
import json
import os
import subprocess
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 960
PER_IMG = 4


def frame_at(video, t):
    tmp = 'frames/_b13_panel.png'
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    return Image.open(tmp).convert('RGB')


def common_box(base):
    p = os.path.join(base, 'sections.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    boxes = [tuple(s['box']) for s in d['sections']
             if s['box'][2] > 400 and s['box'][3] > 100]
    if not boxes:
        return None
    return list(Counter(boxes).most_common(1)[0][0])


def save_chunk(tiles, base, idx, box):
    W = max(t.size[0] for _, t in tiles) + 16
    H = sum(t.size[1] + 28 for _, t in tiles)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, im in tiles:
        d.rectangle([0, y, W, y + 27], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%gs  box=%s' % (t, box), font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (8, y + 28))
        y += im.size[1] + 28
    out = os.path.join(base, 'pm%d.png' % idx)
    canvas.save(out)
    return out


def main():
    argv = sys.argv[1:]
    video, vid = argv[0], argv[1]
    rest = argv[2:]
    full = '--full' in rest
    rest = [a for a in rest if a != '--full']
    box = None
    times = []
    i = 0
    while i < len(rest):
        if rest[i] == '--box':
            box = [int(v) for v in rest[i + 1].split(',')]
            i += 2
        elif rest[i] == '--times':
            times = [float(v) for v in rest[i + 1].split(',')]
            i += 2
        else:
            times.append(float(rest[i]))
            i += 1
    base = 'frames/b13_%s' % vid
    os.makedirs(base, exist_ok=True)
    if box is None and not full:
        box = common_box(base)
        if box:
            x, y, w, h = box
            box = [x, y, min(w, 1920 - x), min(h, 1080 - y)]
    if not times:
        d = json.load(open(os.path.join(base, 'sections.json'), encoding='utf-8'))
        times = []
        for s in d['sections']:
            for rng in s['ranges']:
                times.append(round((rng[0] + rng[1]) / 2.0, 1))
        times = sorted(set(times))
    tiles = []
    for t in times:
        im = frame_at(video, t)
        if im is None:
            continue
        if box:
            x, y, w, h = box
            im = im.crop((x, y, x + w, y + h))
        if im.size[0] > TILE_W:
            im = im.resize((TILE_W, max(1, int(im.size[1] * TILE_W / im.size[0]))))
        tiles.append((t, im))
    if not tiles:
        print('NO PANELS', vid)
        return
    outs = []
    for k in range(0, len(tiles), PER_IMG):
        outs.append(save_chunk(tiles[k:k + PER_IMG], base, k // PER_IMG, box))
    print('%s panels=%d -> %s' % (vid, len(tiles), ' '.join(outs)))


if __name__ == '__main__':
    main()
