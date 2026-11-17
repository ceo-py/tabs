"""b18d_titles.py - private helper for the b18d batch.

Reads frames/b18d_<id>/sections.json (produced by b18d_survey.py) and renders
every distinct section title at FULL resolution, upright, one row per section.
Also renders the full panel crop of every section into frames/b18d_<id>/.

Usage: py -3.14 b18d_titles.py <video> <id>
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13_survey import bar_text_mask, bands  # noqa: E402

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def grab(video, t, box, out):
    x, y, w, h = box
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out]
    r = subprocess.run(cmd, capture_output=True)
    return out if r.returncode == 0 and os.path.exists(out) else None


def strip(video, t, rb, base):
    tmp = base + '/_strip.png'
    if not grab(video, t, rb, tmp):
        return None
    im = Image.open(tmp).convert('RGB')
    m = bar_text_mask(im)
    if m.sum() < 12:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    im = im.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
    if im.size[1] > im.size[0]:
        im = im.rotate(-90, expand=True)
    h = 34
    if im.size[1] != h:
        im = im.resize((max(1, int(im.size[0] * h / max(1, im.size[1]))), h))
    return im


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    base = 'frames/b18d_%s' % vid
    data = json.load(open(base + '/sections.json', encoding='utf-8'))
    secs = data['sections']
    tiles = []
    for i, s in enumerate(secs):
        full = '%s/full_%02d.png' % (base, i)
        grab(video, s['rep'], s['box'], full)
        lbl = strip(video, s['rep'], s['rb'], base) if s.get('rb') else None
        tiles.append((i, s, lbl))
    W = 900
    rows = []
    for i, s, lbl in tiles:
        rows.append((i, s, lbl))
    H = len(rows) * 26 + sum(((lbl.size[1] + 8) if lbl is not None else 6)
                              for _, _, lbl in rows)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for i, s, lbl in rows:
        d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
        rng = ','.join('%g-%g' % (a, b) for a, b in s['ranges'][:5])
        d.text((5, y + 3), '#%d t=%s  box=%s' % (i, rng, s['box']), font=fnt,
               fill=(255, 210, 0))
        y += 26
        if lbl is not None:
            canvas.paste(lbl, (8, y))
            y += lbl.size[1] + 8
        else:
            y += 6
    canvas.save(base + '/titles.png')
    print('%s sections=%d -> titles.png' % (vid, len(secs)))


if __name__ == '__main__':
    main()
