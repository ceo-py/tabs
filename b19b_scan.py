"""b19b_scan.py - private timeline scanner for batch 19b.

Reuses the frames the interrupted survey already extracted
(frames/b19b_<id>/p/p_*.png, 480px wide, one per `interval` seconds) and
produces, for every video:

  * frames/b19b_<id>/timeline.json  - the runs (section title + time range)
  * frames/b19b_<id>/timeline.png   - one row per run: the time range, the
    section-title strip cut out of the red bar at full resolution and the
    matching panel crop (red bar + white sheet).

Usage: py -3.14 b19b_scan.py <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 900
GAP = 130


def size(video):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                         capture_output=True, text=True).stdout.strip().split(',')
    return int(out[0]), int(out[1])


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for %s' % vid)


def bands(flags, min_run=1):
    out, start = [], None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_run:
                out.append((start, i - 1))
            start = None
    if start is not None and len(flags) - start >= min_run:
        out.append((start, len(flags) - 1))
    return out


def red_bars(mask, W, H):
    """Wide horizontal bars of saturated red (the section-title bar)."""
    out = []
    xoff = 150
    rows = mask[:, xoff:].sum(axis=1)
    for y0, y1 in bands(rows > 0.5 * (W - xoff), 3):
        sub = mask[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 3)
        if cols:
            x0 = cols[0][0]
            x1 = cols[-1][1]
            if x1 - x0 > 0.4 * W:
                out.append([x0, y0, x1 - x0 + 1, y1 - y0 + 1])
    return out


def bar_text_mask(lbl):
    """White lettering inside the red bar."""
    a = np.asarray(lbl).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 190) & (g > 190) & (b > 190)
    rows_red = red.sum(axis=1) > 0
    nrows = max(1, int(rows_red.sum()))
    colfrac = red.sum(axis=0) / nrows
    keep = colfrac > 0.5
    if keep.sum() < 2:
        keep = colfrac > 0.25
    if keep.sum() < 2:
        return white
    m = white.copy()
    m[:, ~keep] = False
    return m


def glyph_sig(im, rb, px, py):
    """Binary glyph mask of the section title, cropped to the lettering."""
    w, h = im.size
    x0 = max(0, int(rb[0] / px))
    y0 = max(0, int(rb[1] / py))
    x1 = min(w, max(x0 + 1, int((rb[0] + rb[2]) / px)))
    y1 = min(h, max(y0 + 1, int((rb[1] + rb[3]) / py)))
    lbl = im.crop((x0, y0, x1, y1))
    m = bar_text_mask(lbl)
    if m.sum() < 10:
        return None
    tall = m.sum(axis=0) > 0.8 * m.shape[0]
    m[:, tall] = False
    if m.sum() < 10:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    m = m[rows[0][0]:rows[-1][1] + 1, cols[0][0]:cols[-1][1] + 1]
    return m


def same(a, b):
    if a is None or b is None or a.shape != b.shape:
        return False
    diff = int((a != b).sum())
    return diff <= 0.14 * max(1, a.size)


def crop_at(video, t, box, out):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (box[2], box[3], box[0], box[1]), out]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and os.path.exists(out)


def main():
    vid = sys.argv[1]
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    base = 'frames/b19b_%s' % vid
    video = video_path(vid)
    SW, SH = size(video)
    pdir = os.path.join(base, 'p')
    files = sorted(f for f in os.listdir(pdir) if f.endswith('.png'))

    runs = []
    for i, f in enumerate(files):
        t = round(i * interval, 2)
        im = Image.open(os.path.join(pdir, f)).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 120) & (g < 95) & (b < 95)
        bars = red_bars(red, im.size[0], im.size[1])
        if not bars:
            if runs and runs[-1]['t1'] == t - interval:
                runs[-1]['t1'] = t - interval
            continue
        bars.sort(key=lambda bb: -(bb[2] * bb[3]))
        bb = bars[0]
        px = SW / im.size[0]
        py = SH / im.size[1]
        rb = [int(bb[0] * px), int(bb[1] * py), int(bb[2] * px), int(bb[3] * py)]
        sig = glyph_sig(im, rb, px, py)
        if runs and same(sig, runs[-1]['sig']):
            runs[-1]['t1'] = t
            runs[-1]['rb'] = rb
            continue
        runs.append({'t0': t, 't1': t, 'rb': rb, 'sig': sig})

    # the panel crop: the red bar plus the white sheet below it
    out = []
    for rn in runs:
        rb = rn['rb']
        h = SH - rb[1]
        if h % 2:
            h -= 1
        out.append({'t0': rn['t0'], 't1': rn['t1'], 'rb': rb,
                    'panel': [rb[0], rb[1], SW - rb[0], h],
                    'rep': rn['t0'] + (rn['t1'] - rn['t0']) / 2.0})

    json.dump({'sw': SW, 'sh': SH, 'runs': out},
              open(os.path.join(base, 'timeline.json'), 'w'), indent=1)

    tiles = []
    for idx, rn in enumerate(out):
        tmp = os.path.join(base, '_sc.png')
        if not crop_at(video, rn['rep'], rn['panel'], tmp):
            continue
        panel = Image.open(tmp).convert('RGB')
        if panel.size[0] > TILE_W:
            panel = panel.resize((TILE_W, max(1, int(panel.size[1] * TILE_W / panel.size[0]))))
        tmp2 = os.path.join(base, '_sl.png')
        if not crop_at(video, rn['rep'], rn['rb'], tmp2):
            continue
        strip = Image.open(tmp2).convert('RGB')
        m = bar_text_mask(strip)
        cols = bands(m.sum(axis=0) > 0, 1)
        rows = bands(m.sum(axis=1) > 0, 1)
        if cols and rows:
            strip = strip.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
            if strip.size[0] > 700:
                strip = strip.resize((700, max(1, int(strip.size[1] * 700 / strip.size[0]))))
        tiles.append((idx, rn, panel, strip))

    if tiles:
        W = TILE_W + 16
        H = sum(t[2].size[1] + 30 for t in tiles)
        canvas = Image.new('RGB', (W, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 17)
        y = 0
        for idx, rn, panel, strip in tiles:
            d.rectangle([0, y, W, y + 29], fill=(0, 0, 0))
            d.text((5, y + 5), '#%d t=%g-%g  rep=%g  bar=%s  panel=%s'
                   % (idx, rn['t0'], rn['t1'], rn['rep'], rn['rb'], rn['panel']),
                   font=fnt, fill=(255, 210, 0))
            canvas.paste(strip, (10, y + 4))
            canvas.paste(panel, (8, y + 30))
            y += panel.size[1] + 30
        canvas.save(os.path.join(base, 'timeline.png'))
    print('%s runs=%d' % (vid, len(out)))
    for idx, rn in enumerate(out):
        print('   #%d t=%g-%g rep=%g bar=%s panel=%s'
              % (idx, rn['t0'], rn['t1'], rn['rep'], rn['rb'], rn['panel']))


if __name__ == '__main__':
    main()
