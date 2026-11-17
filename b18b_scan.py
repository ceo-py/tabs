"""b18b_scan.py - private section scanner for the GuitarZero2HeroExpress batch 18b.

The shared b13_survey.py detector missed the overlay in some of the batch 18b
videos (the Smashing Pumpkins ones).  This scanner works purely off the
saturated-red section title bar, which every video in this channel uses:

  * find the horizontal red bar in the lower half of the frame
  * read the white lettering inside it (the section title)
  * group frames by the lettering -> one group per section
  * measure the white sheet under the bar -> the panel crop box

Output:
  frames/b18b_<id>/scan.png      montage (caption + title + panel crop)
  frames/b18b_<id>/scan.json     sections with time ranges and crop boxes

Usage: py -3.14 b18b_scan.py <video> <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 900


def size(video):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                          video], capture_output=True, text=True).stdout.strip().split(',')
    return int(out[0]), int(out[1])


def bands(flags, min_run=1):
    out, start = [], None
    for i, v in enumerate(list(flags) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_run:
                out.append((start, i - 1))
            start = None
    return out


def find_bar(im):
    """Locate the wide red title bar. Returns (x0, y0, w, h) in image pixels."""
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    H, W = red.shape
    xoff = int(0.13 * W)
    best = None
    for y0, y1 in bands(red[:, xoff:].sum(axis=1) > 0.55 * (W - xoff), 3):
        if y0 < 0.35 * H:
            continue
        sub = red[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0.6 * (y1 - y0 + 1), 3)
        if not cols:
            continue
        x0, x1 = cols[0][0], cols[-1][1]
        if x1 - x0 < 0.35 * W:
            continue
        if best is None or (y1 - y0) > (best[3]):
            best = (x0, y0, x1 - x0 + 1, y1 - y0 + 1)
    return best


def sheet_bottom(im, bar):
    """Bottom edge of the white sheet below the title bar."""
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 205) & (g > 205) & (b > 205)
    H, W = white.shape
    y0 = bar[1] + bar[3]
    rows = white[y0:].sum(axis=1) > 0.3 * W
    band = bands(rows, 5)
    if not band:
        return H
    return y0 + band[-1][1] + 1


def glyph_mask(lbl):
    """White lettering inside the red bar. Returns (mask, (x0,y0,x1,y1)) or None."""
    a = np.asarray(lbl).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 175) & (g > 175) & (b > 175)
    nrows = max(1, int(red.sum() / max(1, lbl.size[0])))
    colfrac = red.sum(axis=0) / max(1, nrows)
    keep = colfrac > 0.5
    if keep.sum() < 2:
        keep = colfrac > 0.25
    m = white.copy()
    if keep.sum() >= 2:
        m[:, ~keep] = False
    tall = m.sum(axis=0) > 0.85 * m.shape[0]
    m[:, tall] = False
    if m.sum() < 10:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    box = (cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1)
    m = m[box[1]:box[3], box[0]:box[2]]
    # normalise the glyph mask so that a jittering bar crop still groups
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((64, 16)))
    return m, box


def crop_at(video, t, box, path):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (box[2], box[3], box[0], box[1]),
           path]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and os.path.exists(path)


def main():
    video, vid = sys.argv[1], sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    base = 'frames/b18b_%s' % vid
    tmpd = base + '/s'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=960:-1' % interval,
                    os.path.join(tmpd, 'f_%05d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    SW, SH = size(video)

    groups = []

    def same(a, b):
        if a is None or b is None or len(a) != len(b):
            return False
        n = max(1, sum(1 for x in a if x))
        return sum(1 for x, y in zip(a, b) if x != y) <= 0.15 * n

    for i, f in enumerate(files):
        t = round(i * interval, 2)
        im = Image.open(f)
        bar = find_bar(im)
        if not bar:
            continue
        lbl = im.crop((bar[0], bar[1], bar[0] + bar[2], bar[1] + bar[3]))
        gm = glyph_mask(lbl)
        if gm is None:
            continue
        m = gm[0]
        sx = SW / im.size[0]
        sy = SH / im.size[1]
        obar = [int(bar[0] * sx), int(bar[1] * sy), int(bar[2] * sx), int(bar[3] * sy)]
        obot = int(sheet_bottom(im, bar) * sy)
        sig = m.tobytes()
        hit = None
        for g in groups:
            if same(sig, g['sig']):
                hit = g
                break
        if hit is None:
            groups.append({'sig': sig, 'ranges': [[t, t]], 'bar': obar,
                           'bot': obot, 'rep': t, 'img': f, 'lbl': lbl.copy()})
        else:
            if t - hit['ranges'][-1][1] > interval * 1.6:
                hit['ranges'].append([t, t])
            else:
                hit['ranges'][-1][1] = t
            if obot > hit['bot']:
                hit['bot'] = obot
                hit['rep'] = t
                hit['bar'] = obar
                hit['img'] = f

    secs = []
    for g in groups:
        secs.append({'t0': g['ranges'][0][0], 't1': g['ranges'][-1][1],
                     'ranges': g['ranges'], 'bar': g['bar'], 'bot': g['bot'],
                     'rep': g['rep']})
        g['sec'] = len(secs) - 1
    secs.sort(key=lambda s: s['t0'])
    for g in groups:
        g['sec'] = next(i for i, s in enumerate(secs) if s['rep'] == g['rep']
                        and s['bar'] == g['bar'])
    json.dump({'sw': SW, 'sh': SH, 'sections': secs},
              open(base + '/scan.json', 'w'), indent=1)

    tiles = []
    for idx, s in enumerate(secs):
        x, y, w, h = s['bar']
        box = [x, y, w, max(120, s['bot'] - y)]
        p = base + '/_s.png'
        if not crop_at(video, s['rep'], box, p):
            continue
        im = Image.open(p).convert('RGB')
        g = next(g for g in groups if g['rep'] == s['rep'] and g['bar'] == s['bar'])
        lbl = g['lbl'].copy()
        gm = glyph_mask(lbl)
        if gm is not None:
            box = gm[1]
            lbl = lbl.crop(box)
        if lbl.size[1] > lbl.size[0]:
            lbl = lbl.rotate(-90, expand=True)
        if lbl.size[1] != 30:
            lbl = lbl.resize((max(1, int(lbl.size[0] * 30 / max(1, lbl.size[1]))), 30))
        tiles.append((idx, s, im, lbl))

    if tiles:
        W = TILE_W + 16
        H = sum(t.size[1] + 30 for _, _, t, _ in tiles)
        canvas = Image.new('RGB', (W, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 18)
        y = 0
        for idx, s, t, lbl in tiles:
            d.rectangle([0, y, W, y + 29], fill=(0, 0, 0))
            rng = ','.join('%g-%g' % (a, b) for a, b in s['ranges'][:4])
            d.text((5, y + 4), '#%d t=%s  crop=[%d,%d,%d,%d]' % (
                idx, rng, s['bar'][0], s['bar'][1], s['bar'][2],
                max(120, s['bot'] - s['bar'][1])), font=fnt, fill=(255, 210, 0))
            canvas.paste(lbl, (min(max(0, t.size[0] - lbl.size[0]), 600), y + 3))
            canvas.paste(t, (8, y + 30))
            y += t.size[1] + 30
        canvas.save(base + '/scan.png')
    print('%s sections=%d tiles=%d' % (vid, len(secs), len(tiles)))
    for idx, s in enumerate(secs):
        rng = ','.join('%g-%g' % (a, b) for a, b in s['ranges'][:6])
        print('   #%d t=%s bar=%s bot=%d rep=%g' % (idx, rng, s['bar'], s['bot'], s['rep']))


if __name__ == '__main__':
    main()
