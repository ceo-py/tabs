"""b13_survey.py - private survey helper for the GuitarZero2HeroExpress batches.

For every video it finds the on-screen graphic overlay (white tab sheet /
chord table plus the red section label bar), groups the frames into sections
and renders one montage:

    caption : "#n  t=<a>-<b>s  crop=[x,y,w,h]"
    label   : the section title cropped out of the red bar (rotated upright
              when the bar is vertical)
    panel   : the overlay crop, scaled to the montage width

Reading that single image reveals every section of the video, its time range
and the crop box to use for the card.

Usage: py -3.14 b13_survey.py <video> <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
TILE_W = 900
GAP = 130


def size(video):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                         capture_output=True, text=True).stdout.strip().split(',')
    return int(out[0]), int(out[1])


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


def regions(mask, min_fill, min_area_frac):
    im = Image.fromarray((mask * 255).astype(np.uint8), 'L').filter(ImageFilter.MinFilter(5))
    e = np.asarray(im) > 0
    h, w = e.shape
    out = []
    for y0, y1 in bands(e.sum(axis=1) > 0, 2):
        sub = e[y0:y1 + 1]
        for x0, x1 in bands(sub.sum(axis=0) > 0, 2):
            area = (y1 - y0 + 1) * (x1 - x0 + 1)
            if area < min_area_frac * w * h:
                continue
            fill = mask[y0:y1 + 1, x0:x1 + 1].mean()
            if fill < min_fill:
                continue
            out.append([x0, x1, y0, y1, area, fill])
    out.sort(key=lambda b: -b[4])
    return out


def cluster(regs):
    """Group boxes that are within GAP px of each other."""
    groups = []
    for r in regs:
        hit = None
        for g in groups:
            for q in g:
                gap_x = max(0, max(q[0] - r[1], r[0] - q[1]))
                gap_y = max(0, max(q[2] - r[3], r[2] - q[3]))
                if gap_x < GAP or gap_y < GAP:
                    hit = g
                    break
            if hit:
                break
        if hit is None:
            groups.append([r])
        else:
            hit.append(r)
    # merge groups that became connected
    changed = True
    while changed:
        changed = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if any(near(q, r) for q in groups[i] for r in groups[j]):
                    groups[i] += groups[j]
                    del groups[j]
                    changed = True
                    break
            if changed:
                break
    return groups


def near(q, r):
    gap_x = max(0, max(q[0] - r[1], r[0] - q[1]))
    gap_y = max(0, max(q[2] - r[3], r[2] - q[3]))
    return gap_x < GAP or gap_y < GAP


def bbox(group):
    x0 = min(g[0] for g in group)
    x1 = max(g[1] for g in group)
    y0 = min(g[2] for g in group)
    y1 = max(g[3] for g in group)
    return [x0, y0, x1 - x0, y1 - y0]


def label_region(group, is_red):
    """Biggest red box of the cluster = the section title bar."""
    reds = [g for g in group if g[5] >= 0 and g in group]
    return None


def red_bars(mask, W, H):
    """Wide horizontal bars and tall vertical bars of saturated red.

    Returned as source-independent boxes [x0, y0, w, h].
    """
    out = []
    xoff = 200
    rows = mask[:, xoff:].sum(axis=1)
    for y0, y1 in bands(rows > 0.5 * (W - xoff), 3):
        sub = mask[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 3)
        if cols:
            x0 = cols[0][0]
            x1 = cols[-1][1]
            if x1 - x0 > 0.4 * W:
                out.append([x0, y0, x1 - x0 + 1, y1 - y0 + 1])
    cols = mask.sum(axis=0)
    for x0, x1 in bands(cols > 0.22 * H, 3):
        sub = mask[:, x0:x1 + 1]
        rows2 = bands(sub.sum(axis=1) > 0, 3)
        if rows2:
            y0 = rows2[0][0]
            y1 = rows2[-1][1]
            if y1 - y0 > 0.4 * H:
                # widen to the full bar: every column that carries red in the
                # bar's row range
                sub2 = mask[y0:y1 + 1]
                cc = bands(sub2.sum(axis=0) > 0.2 * (y1 - y0 + 1), 2)
                if cc:
                    x0 = cc[0][0]
                    x1 = cc[-1][1]
                out.append([x0, y0, x1 - x0 + 1, y1 - y0 + 1])
    return out


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    base = 'frames/b13_%s' % vid
    tmpd = base + '/p'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=480:-1' % interval, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))
    SW, SH = size(video)

    frames = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        white = (r > 205) & (g > 205) & (b > 205)
        red = (r > 120) & (g < 95) & (b < 95)
        ws = regions(white, 0.55, 0.004)
        rs = regions(red, 0.55, 0.002)
        for b_ in ws:
            b_.append('w')
        for b_ in rs:
            b_.append('r')
        regs = ws + rs
        if not regs:
            continue
        px = SW / im.size[0]
        py = SH / im.size[1]
        regs = [[int(g[0] * px), int(g[1] * py), int(g[2] * px), int(g[3] * py),
                 g[4], g[5], g[6]] for g in regs]
        groups = cluster(regs)
        groups.sort(key=lambda g: -sum(x[4] for x in g))
        best = groups[0]
        main = max(best, key=lambda g: g[4])
        # keep the solid graphic parts of the cluster (the panel, the label
        # bar, the chord table); drop the soft-edged leftovers (the guitarist)
        keep = [g for g in best
                if g[5] >= 0.78 or (g[2] >= main[2] and g[3] <= main[3])]
        # the section title bar: a wide / tall saturated red bar next to the panel
        bars = red_bars(red, im.size[0], im.size[1])
        bars = [[int(b_[0] * px), int(b_[1] * py), int(b_[2] * px), int(b_[3] * py)]
                for b_ in bars]
        bar = None
        if bars:
            cand = []
            for b_ in bars:
                bx0, by0, bw, bh = b_
                gap_x = max(0, max(main[0] - (bx0 + bw), bx0 - main[1]))
                gap_y = max(0, max(main[2] - (by0 + bh), by0 - main[3]))
                cand.append((gap_x + gap_y, -bw * bh, b_))
            cand.sort(key=lambda c: (c[0], c[1]))
            bar = cand[0][2]
        box = bbox(keep)
        if bar:
            bx0, by0, bw, bh = bar
            vertical = bh > bw
            members = keep
            if not vertical:
                # horizontal header bar -> the crop is exactly bar + panel
                members = [main]
            x0 = min([members[0][0]] + [bx0])
            y0 = min([members[0][2]] + [by0])
            x1 = max([members[0][1]] + [bx0 + bw])
            y1 = max([members[0][3]] + [by0 + bh])
            for m in members[1:] if vertical else []:
                x0 = min(x0, m[0]); y0 = min(y0, m[2])
                x1 = max(x1, m[1]); y1 = max(y1, m[3])
            box = [x0, y0, x1 - x0, y1 - y0]
        rb = bar
        if (main[1] - main[0]) * (main[3] - main[2]) < 0.015 * SW * SH:
            continue
        if rb and rb[3] > 0.75 * SH:
            continue
        frames.append({'t': round(i * interval, 2), 'box': box, 'rb': rb,
                       'sig': _sig(f, rb, im.size, px, py)})

    # group frames by the section title glyphs (all occurrences of the same
    # title anywhere in the video belong to one group)
    groups = []

    def diff(a, b):
        return sum(1 for x, y in zip(a, b) if x != y)

    def same(a, b):
        if len(a) != len(b):
            return False
        n = max(1, sum(a))
        return diff(a, b) <= 0.12 * n

    for fr in frames:
        if fr['sig'] is None:
            continue
        hit = None
        for g in groups:
            if same(fr['sig'], g['sig']):
                hit = g
                break
        if hit is None:
            groups.append({'sig': fr['sig'], 'ranges': [[fr['t'], fr['t']]],
                           'box': fr['box'], 'rb': fr['rb'], 'rep': fr['t'],
                           'area': fr['box'][2] * fr['box'][3]})
        else:
            if fr['t'] - hit['ranges'][-1][1] > interval * 1.6:
                hit['ranges'].append([fr['t'], fr['t']])
            else:
                hit['ranges'][-1][1] = fr['t']
            if fr['box'][2] * fr['box'][3] > hit['area']:
                hit['area'] = fr['box'][2] * fr['box'][3]
                hit['box'] = fr['box']
                hit['rb'] = fr['rb']
                hit['rep'] = fr['t']
    secs = []
    for g in groups:
        secs.append({'t0': g['ranges'][0][0], 't1': g['ranges'][-1][1],
                     'ranges': g['ranges'], 'box': g['box'], 'rb': g['rb'],
                     'rep': g['rep']})
    json.dump({'sw': SW, 'sh': SH, 'sections': secs,
               'frames': [{'t': f['t'], 'box': f['box'], 'rb': f['rb'],
                           'sig': None if f['sig'] is None else len(f['sig'])}
                          for f in frames]},
              open(base + '/sections.json', 'w'), indent=1)

    tiles = []
    for idx, s in enumerate(secs):
        crop = crop_at(video, s['rep'], s['box'], base)
        if crop is None:
            continue
        lbl = label_strip(video, s['rep'], s['rb'], base) if s['rb'] else None
        tiles.append((idx, s, crop, lbl))
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
            d.text((5, y + 4), '#%d t=%s  crop=%s' % (idx, rng, s['box']),
                   font=fnt, fill=(255, 210, 0))
            if lbl is not None:
                canvas.paste(lbl, (min(t.size[0] - lbl.size[0], 560), y + 3))
            canvas.paste(t, (8, y + 30))
            y += t.size[1] + 30
        canvas.save(base + '/survey.png')
    print('%s sections=%d tiles=%d' % (vid, len(secs), len(tiles)))
    for idx, s in enumerate(secs):
        rng = ','.join('%g-%g' % (a, b) for a, b in s['ranges'][:6])
        print('   #%d t=%s box=%s rb=%s' % (idx, rng, s['box'], s['rb']))


def bar_text_mask(lbl):
    """White lettering inside the red bar (white sheet next to the bar is
    ignored).  Returns the boolean mask of the glyphs."""
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


def _sig(path, rb, imsize, px, py):
    if not rb:
        return None
    im = Image.open(path).convert('RGB')
    w, h = im.size
    x0 = int(rb[0] / px)
    x1 = int((rb[0] + rb[2]) / px)
    y0 = int(rb[1] / py)
    y1 = int((rb[1] + rb[3]) / py)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, max(x0 + 1, x1)), min(h, max(y0 + 1, y1))
    lbl = im.crop((x0, y0, x1, y1))
    m = bar_text_mask(lbl)
    if m.sum() < 10:
        return None
    # drop the columns that are white over the whole height - those are the
    # edge of the tab sheet showing next to the label bar, not the lettering
    tall = m.sum(axis=0) > 0.8 * m.shape[0]
    m[:, tall] = False
    if m.sum() < 10:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    m = m[rows[0][0]:rows[-1][1] + 1, cols[0][0]:cols[-1][1] + 1]
    return m.tobytes()


def crop_at(video, t, box, base):
    tmp = base + '/_crop.png'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1',
           '-vf', 'crop=%d:%d:%d:%d' % (box[2], box[3], box[0], box[1]), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    im = Image.open(tmp).convert('RGB')
    if im.size[0] > TILE_W:
        im = im.resize((TILE_W, max(1, int(im.size[1] * TILE_W / im.size[0]))))
    return im


def label_strip(video, t, rb, base):
    tmp = base + '/_lbl.png'
    x0, y0, w, h = rb
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1',
           '-vf', 'crop=%d:%d:%d:%d' % (w, h, x0, y0), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
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
    h = 30
    if im.size[1] != h:
        im = im.resize((max(1, int(im.size[0] * h / max(1, im.size[1]))), h))
    return im


if __name__ == '__main__':
    main()
