"""b18a_scan.py - private scanner for the b18a batch (Metallica / Queen).

Layout "A" ("bottom sheet"): a wide horizontal red section-title bar, with the
white TAB sheet underneath it.  The title bar's geometry wobbles by a few
pixels between frames, so the lettering is extracted at FULL resolution and
normalised to a fixed size before the frames are clustered - that keeps the
signature stable and separates the real section titles from each other.

Writes, per video:
    frames/b18a_<id>/sections.json   sections, time ranges, crop boxes
    frames/b18a_<id>/labels.png      every distinct section title, upright
    frames/b18a_<id>/panels.png      one full-res panel crop per section

Usage: py -3.14 b18a_scan.py <video> <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
SW_SAMPLE = 480
SIG_H = 20
SIG_W = 340


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


def bar_of(im):
    """Locate the wide red title bar of the bottom-sheet layout.

    Returns (bx0, bx1, by0, by1) in sample pixels or None.
    """
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    H, W = red.shape
    xoff = int(0.20 * W)
    rows = red[:, xoff:].sum(axis=1)
    cands = []
    for y0, y1 in bands(rows > 0.50 * (W - xoff), 3):
        if y0 < 0.40 * H:
            continue
        sub = red[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 3)
        if not cols:
            continue
        cands.append((cols[-1][1] - cols[0][0], y0, y1, cols[0][0], cols[-1][1]))
    if not cands:
        return None
    cands.sort(reverse=True)
    _, y0, y1, bx0, bx1 = cands[0]
    if bx1 - bx0 < 0.35 * W:
        return None
    return bx0, bx1, y0, y1


def title_sig(video, t, bar, base, SW, SH):
    """Full-resolution crop of the bar lettering -> (signature, label image)."""
    x0, x1, y0, y1 = bar
    px, py = SW / 480.0, SH / 270.0
    bx = int(x0 * px)
    by = int(y0 * py)
    bw = int((x1 - x0 + 1) * px)
    bh = max(8, int((y1 - y0 + 1) * py))
    bx = max(0, bx)
    by = max(0, by)
    bw = max(8, min(bw, SW - bx))
    bh = max(8, min(bh, SH - by))
    tmp = base + '/_bar.png'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (bw, bh, bx, by),
                    tmp], capture_output=True)
    if not os.path.exists(tmp):
        return None, None
    im = Image.open(tmp).convert('RGB')
    # the bar graphic carries a thin bright edge line; drop a couple of rows
    # at the top and bottom so that line cannot become the "lettering"
    if im.size[1] > 8:
        im = im.crop((0, 3, im.size[0], im.size[1] - 3))
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 150) & (g > 150) & (b > 150)
    if white.sum() < 12:
        return None, None
    cols = bands(white.sum(axis=0) >= 8, 1)
    rows = bands(white.sum(axis=1) >= 3, 1)
    if not cols or not rows:
        return None, None
    t2 = im.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
    if t2.size[1] > t2.size[0]:
        t2 = t2.rotate(-90, expand=True)
    m = (np.asarray(t2.convert('L')) > 150).astype(np.float32)
    h = SIG_H
    w = max(1, int(round(t2.size[0] * h / max(1, t2.size[1]))))
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
        (min(w, SIG_W), h))).astype(np.float32) / 255.0
    sig = np.zeros((h, SIG_W), dtype=np.float32)
    sig[:, :m.shape[1]] = m
    return sig, t2


def main():
    video, vid = sys.argv[1], sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    base = 'frames/b18a_%s' % vid
    tmpd = base + '/s'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=%d:-1' % (interval, SW_SAMPLE),
                    os.path.join(tmpd, 'p_%04d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                          video], capture_output=True, text=True).stdout.strip().split(',')
    SW, SH = int(out[0]), int(out[1])

    groups = []
    for i, f in enumerate(files):
        t = i * interval
        im = Image.open(f).convert('RGB')
        bar = bar_of(im)
        if not bar:
            continue
        sig, lbl = title_sig(video, t, bar, base, SW, SH)
        if sig is None:
            continue
        hit = None
        for g in groups:
            if np.abs(g['sig'] - sig).mean() < 0.010:
                hit = g
                break
        if hit is None:
            groups.append({'sig': sig, 'lbl': lbl, 'times': [t], 'bar': bar})
        else:
            hit['times'].append(t)
            if t - hit['times'][-2] > interval * 2.5:
                hit['times'].append(t)

    # merge neighbouring groups that ended up with the same title
    merged = []
    for g in groups:
        if merged and np.abs(merged[-1]['sig'] - g['sig']).mean() < 0.010:
            merged[-1]['times'].extend(g['times'])
            continue
        merged.append(g)

    secs = []
    for idx, g in enumerate(merged):
        t0, t1 = g['times'][0], g['times'][-1]
        # the panel box: the title bar plus the white sheet below it
        px, py = SW / 480.0, SH / 270.0
        bx0 = int(g['bar'][0] * px)
        by0 = int(g['bar'][2] * py)
        box = [bx0, by0, SW - bx0, SH - by0]
        secs.append({'idx': idx, 't0': t0, 't1': t1, 'rep': t1, 'box': box,
                     'times': g['times']})
    json.dump({'sw': SW, 'sh': SH, 'sections': secs},
              open(base + '/sections.json', 'w'), indent=1)

    # labels sheet --------------------------------------------------------
    lbls = []
    for idx, g in enumerate(merged):
        l = g['lbl']
        if l is None:
            continue
        h = 40
        if l.size[1] != h:
            l = l.resize((max(1, int(l.size[0] * h / max(1, l.size[1]))), h))
        lbls.append((idx, g['times'], l))
    if lbls:
        Wl = max(s.size[0] for _, _, s in lbls) + 20
        Hl = sum(s.size[1] + 34 for _, _, s in lbls) + 10
        canvas = Image.new('RGB', (Wl, Hl), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 5
        for idx, times, l in lbls:
            txt = '#%d  t=%g-%g' % (idx, times[0], times[-1])
            d.text((6, y), txt, font=fnt, fill=(255, 210, 0))
            canvas.paste(l, (6, y + 26))
            y += l.size[1] + 34
        canvas.save(base + '/labels.png')

    # panels sheet --------------------------------------------------------
    tiles = []
    for idx, s in enumerate(secs):
        tmp = base + '/_c.png'
        r = s['box']
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % s['rep'],
                        '-i', video, '-frames:v', '1', '-vf',
                        'crop=%d:%d:%d:%d' % (r[2], r[3], r[0], r[1]), tmp],
                       capture_output=True)
        if not os.path.exists(tmp):
            continue
        tiles.append((idx, s, Image.open(tmp).convert('RGB')))
    if tiles:
        TW = 1500
        H = sum(t.size[1] + 34 for _, _, t in tiles) + 10
        canvas = Image.new('RGB', (TW, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 5
        for idx, s, im in tiles:
            im = im.resize((TW - 16, max(1, int(im.size[1] * (TW - 16) / im.size[0]))))
            d.rectangle([0, y, TW, y + 30], fill=(0, 0, 0))
            d.text((6, y + 4), '#%d  t=%g-%g  rep=%g  crop=%s' % (
                idx, s['t0'], s['t1'], s['rep'], s['box']), font=fnt, fill=(255, 210, 0))
            canvas.paste(im, (8, y + 32))
            y += im.size[1] + 34
        canvas.save(base + '/panels.png')

    print('%s sections=%d' % (vid, len(secs)))
    for s in secs:
        print('   #%d t=%g-%g rep=%g box=%s' % (s['idx'], s['t0'], s['t1'], s['rep'], s['box']))


if __name__ == '__main__':
    main()
