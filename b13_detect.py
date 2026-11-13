"""b13_detect.py - private helper for the GuitarZero2HeroExpress card batches.

Locates the on-screen TAB / chord panel of a video and the list of on-screen
sections (the dark-red header bar) that appear in it.

Output (per video):
  frames/b13_<id>/panels.json  - geometry + section time ranges
  frames/b13_<id>/sections.png - one legible title strip per section, labelled
                                 with its time range
  frames/b13_<id>/s_<t>.png    - the full source-res frame used for each section

Usage:
  py -3.14 b13_detect.py <video> <id> [interval]
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SW_TARGET = 640
F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def probe_size(video):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                         capture_output=True, text=True).stdout.strip().split(',')
    return int(out[0]), int(out[1])


def duration(video):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())


def bands(flags, min_run=2):
    """Contiguous True runs of a 1-D boolean array -> list of (start, end) inclusive."""
    out = []
    start = None
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


def analyze(path, SW, SH):
    """Returns (sheet_box, bar_box, glyph_box) in SOURCE pixels."""
    im = Image.open(path).convert('RGB')
    w, h = im.size
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 205) & (g > 205) & (b > 205)
    red = (r > 130) & (g < 90) & (b < 90)
    fx, fy = SW / w, SH / h

    def box_from(mask, frac, min_w_frac=0.25):
        rows = mask.mean(axis=1) > frac
        rb = bands(rows, 2)
        if not rb:
            return None
        # widest band by height*coverage
        rb = sorted(rb, key=lambda s: -(s[1] - s[0]))
        y0, y1 = rb[0]
        sub = mask[y0:y1 + 1]
        cols = sub.mean(axis=0) > (frac * 0.6)
        cb = bands(cols, 2)
        if not cb:
            return None
        # merge column bands that are close together, keep the widest span
        merged = [list(cb[0])]
        for c0, c1 in cb[1:]:
            if c0 - merged[-1][1] <= 6:
                merged[-1][1] = c1
            else:
                merged.append([c0, c1])
        merged.sort(key=lambda m: -(m[1] - m[0]))
        x0, x1 = merged[0]
        if (x1 - x0) < min_w_frac * w:
            return None
        return [int(x0 * fx), int(y0 * fy), int((x1 - x0 + 1) * fx), int((y1 - y0 + 1) * fy)]

    sheet = box_from(white, 0.45)
    bar = box_from(red, 0.30)

    glyph = None
    if bar:
        bx, by, bw, bh = bar
        sx, sy = w / SW, h / SH
        sub = Image.open(path).convert('RGB').crop(
            (int(bx * sx), int(by * sy), int((bx + bw) * sx), int((by + bh) * sy)))
        sa = np.asarray(sub).astype(np.int16)
        gw = (sa[..., 0] > 195) & (sa[..., 1] > 195) & (sa[..., 2] > 195)
        gc = gw.sum(axis=0) > 0
        gb = bands(gc, 1)
        if gb:
            gx0 = gb[0][0]
            gx1 = gb[-1][1]
            gr = gw[:, gx0:gx1 + 1].sum(axis=1) > 0
            gb2 = bands(gr, 1)
            if gb2:
                glyph = [int((bx + gx0) * fx), int((by + gb2[0][0]) * fy),
                         int((gx1 - gx0 + 1) * fx), int((gb2[-1][1] - gb2[0][0] + 1) * fy)]
    return sheet, bar, glyph


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    base = 'frames/b13_%s' % vid
    small = base + '/p'
    os.makedirs(small, exist_ok=True)
    for f in glob.glob(small + '/*.png'):
        os.remove(f)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=%d:-1' % (interval, SW_TARGET),
                    os.path.join(small, 'p_%04d.png')], check=True, capture_output=True)
    files = sorted(glob.glob(small + '/*.png'))
    if not files:
        print('NO FRAMES')
        return
    SW, SH = probe_size(video)

    sheets, bars = {}, {}
    info = []
    for i, f in enumerate(files):
        sheet, bar, glyph = analyze(f, SW, SH)
        info.append({'i': i, 't': round(i * interval, 2), 'sheet': sheet, 'bar': bar})
        if sheet:
            k = (sheet[0], sheet[2])
            sheets[k] = sheets.get(k, 0) + 1
        if bar:
            k = (bar[0], bar[2])
            bars[k] = bars.get(k, 0) + 1
    if not sheets:
        print('NO SHEET DETECTED')
        json.dump({'sw': SW, 'sh': SH, 'sheet': None, 'bar': None, 'sections': []},
                  open(base + '/panels.json', 'w'), indent=1)
        return
    sk = max(sheets.items(), key=lambda kv: kv[1])[0]
    bk = max(bars.items(), key=lambda kv: kv[1])[0] if bars else None
    # union of all sheet y-ranges that share the winning x-span
    ys = [d['sheet'] for d in info if d['sheet'] and (d['sheet'][0], d['sheet'][2]) == sk]
    sy0 = min(y[1] for y in ys)
    sy1 = max(y[1] + y[3] for y in ys)
    sheet = [sk[0], sy0, sk[1], sy1 - sy0]
    bar = None
    if bk:
        bys = [d['bar'] for d in info if d['bar'] and (d['bar'][0], d['bar'][2]) == bk]
        by0 = min(y[1] for y in bys)
        by1 = max(y[1] + y[3] for y in bys)
        bar = [bk[0], by0, bk[1], by1 - by0]

    # ---- section grouping: signature of the white glyphs inside the red bar
    secs = []
    prev = None
    for d in info:
        if not d['bar']:
            sig = None
        else:
            sig = _glyph_sig(os.path.join(small, 'p_%04d.png' % d['i']), d['bar'], SW, SH)
        if sig is None:
            if prev is not None:
                prev = None
            continue
        if prev is None or sig != prev[1]:
            secs.append({'t0': d['t'], 't1': d['t'], 'sig': sig})
            prev = (d['t'], sig)
        else:
            secs[-1]['t1'] = d['t']
    for s in secs:
        s.pop('sig', None)

    json.dump({'sw': SW, 'sh': SH, 'sheet': sheet, 'bar': bar, 'sections': secs,
               'interval': interval}, open(base + '/panels.json', 'w'), indent=1)

    # ---- legible section-title strip image
    tiles = []
    for s in secs:
        t = s['t0']
        crop = _section_tile(video, base, t, bar, SW, SH)
        tiles.append((s, crop))
    if tiles:
        W = max(t.size[0] for _, t in tiles) + 16
        H = sum(t.size[1] + 26 for _, t in tiles)
        canvas = Image.new('RGB', (W, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 0
        for s, t in tiles:
            d.rectangle([0, y, W, y + 25], fill=(0, 0, 0))
            d.text((5, y + 3), 't=%s-%ss' % (s['t0'], s['t1']), font=fnt, fill=(255, 210, 0))
            canvas.paste(t, (8, y + 26))
            y += t.size[1] + 26
        canvas.save(base + '/sections.png')
    print('sheet', sheet, 'bar', bar, 'sections', len(secs))
    for s in secs:
        print('   t=%.1f-%.1f' % (s['t0'], s['t1']))


def _glyph_sig(path, bar, SW, SH):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    sx, sy = w / SW, h / SH
    bx, by, bw, bh = bar
    sub = im.crop((int(bx * sx), int(by * sy), int((bx + bw) * sx), int((by + bh) * sy)))
    a = np.asarray(sub).astype(np.int16)
    m = (a[..., 0] > 195) & (a[..., 1] > 195) & (a[..., 2] > 195)
    if m.sum() < 20:
        return None
    return m.tobytes()


def _section_tile(video, base, t, bar, SW, SH):
    """Full source-res frame at time t, cropped to the section title glyphs."""
    tmp = base + '/_tile.png'
    if bar:
        bx, by, bw, bh = bar
        x0 = max(0, bx - 20)
        y0 = max(0, by - 6)
        x1 = min(SW, bx + bw + 20)
        y1 = min(SH, by + bh + 6)
        vf = 'crop=%d:%d:%d:%d' % (x1 - x0, y1 - y0, x0, y0)
    else:
        vf = None
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1']
    if vf:
        cmd += ['-vf', vf]
    cmd += [tmp]
    subprocess.run(cmd, check=False, capture_output=True)
    im = Image.open(tmp).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    m = (a[..., 0] > 195) & (a[..., 1] > 195) & (a[..., 2] > 195)
    cols = m.sum(axis=0) > 0
    b = bands(cols, 1)
    if b:
        gx0, gx1 = b[0][0], b[-1][1]
        rows = m[:, gx0:gx1 + 1].sum(axis=1) > 0
        rb = bands(rows, 1)
        if rb:
            gy0, gy1 = rb[0][0], rb[-1][1]
            pad = 8
            im = im.crop((max(0, gx0 - pad), max(0, gy0 - pad),
                          min(im.size[0], gx1 + 1 + pad), min(im.size[1], gy1 + 1 + pad)))
    if im.size[0] > 640:
        im = im.resize((640, max(1, int(im.size[1] * 640 / im.size[0]))))
    return im


if __name__ == '__main__':
    main()
