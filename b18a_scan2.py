"""b18a_scan2.py - private scanner for the b18a videos that use the
"right overlay on black" layout (Queen Bohemian Rhapsody / Crazy Little Thing
Called Love).

On screen there is no red bar and no white sheet: the chord chart and the
section title are drawn in the upper right corner on a black background, and
the strumming pattern sits below the chart.

The section title is the only red text in the upper right band, so its glyph
mask is a reliable signature.  Frames are clustered by that signature.

Writes, per video:
    frames/b18a_<id>/sections.json   sections, time ranges, panel crops
    frames/b18a_<id>/labels.png      every distinct section title, upright
    frames/b18a_<id>/panels.png      the two panel crops of every section

Usage: py -3.14 b18a_scan2.py <video> <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
SIG_H = 20
SIG_W = 340

# title band (x, y, w, h), chart crop (x, y, w, h), strum crop (x, y, w, h)
LAYOUTS = {
    'VHZXP8MCrQg': {
        'title': (1150, 100, 770, 75),
        'chart': (1130, 100, 790, 295),
        'strum': (940, 383, 970, 128),
    },
    '9gGc45WjnpY': {
        'title': (1150, 100, 770, 75),
        'chart': (1120, 105, 800, 165),
        'strum': (1225, 385, 525, 160),
    },
}


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


def crop(video, t, box, out):
    x, y, w, h = box
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out],
                   capture_output=True)
    if not os.path.exists(out):
        return None
    return Image.open(out).convert('RGB')


def title_sig(im, box):
    x, y, w, h = box
    a = np.asarray(im.crop((x, y, x + w, y + h))).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    if red.sum() < 40:
        return None, None
    cols = bands(red.sum(axis=0) >= 3, 1)
    rows = bands(red.sum(axis=1) >= 2, 1)
    if not cols or not rows:
        return None, None
    t2 = im.crop((x + cols[0][0], y + rows[0][0],
                  x + cols[-1][1] + 1, y + rows[-1][1] + 1))
    # the title is RED on black - the signature has to use the red mask, the
    # brightness of red text is far below any grey threshold
    a2 = np.asarray(t2.convert('RGB')).astype(np.int16)
    r2, g2, b2 = a2[..., 0], a2[..., 1], a2[..., 2]
    m = ((r2 > 110) & (g2 < 100) & (b2 < 100)).astype(np.float32)
    if m.sum() < 20:
        return None, None
    h = SIG_H
    w = max(1, int(round(t2.size[0] * h / max(1, t2.size[1]))))
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
        (min(w, SIG_W), h))).astype(np.float32) / 255.0
    sig = np.zeros((h, SIG_W), dtype=np.float32)
    sig[:, :m.shape[1]] = m
    return sig, t2


def main():
    video, vid = sys.argv[1], sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    cfg = LAYOUTS[vid]
    base = 'frames/b18a_%s' % vid
    tmpd = base + '/s2'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=960:-1' % interval,
                    os.path.join(tmpd, 'p_%04d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))

    groups = []
    for i, f in enumerate(files):
        t = i * interval
        im = Image.open(f).convert('RGB')
        sx = im.size[0] / 1920.0
        box = tuple(int(v * sx) if i % 2 == 0 else int(v * sx)
                    for i, v in enumerate(cfg['title']))
        sig, lbl = title_sig(im, box)
        if sig is None:
            continue
        hit = None
        for g in groups:
            if np.abs(g['sig'] - sig).mean() < 0.012:
                hit = g
                break
        if hit is None:
            groups.append({'sig': sig, 'lbl': lbl, 'times': [t]})
        else:
            hit['times'].append(t)

    merged = []
    for g in groups:
        if merged and np.abs(merged[-1]['sig'] - g['sig']).mean() < 0.012:
            merged[-1]['times'].extend(g['times'])
            continue
        merged.append(g)

    secs = []
    for idx, g in enumerate(merged):
        secs.append({'idx': idx, 't0': g['times'][0], 't1': g['times'][-1],
                     'rep': g['times'][-1], 'times': g['times'],
                     'chart': list(cfg['chart']), 'strum': list(cfg['strum'])})
    json.dump({'sw': 1920, 'sh': 1080, 'sections': secs},
              open(base + '/sections.json', 'w'), indent=1)

    # labels sheet
    lbls = []
    for idx, g in enumerate(merged):
        l = g['lbl']
        if l is None:
            continue
        h = 44
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
            d.text((6, y), '#%d  t=%g-%g' % (idx, times[0], times[-1]),
                   font=fnt, fill=(255, 210, 0))
            canvas.paste(l, (6, y + 26))
            y += l.size[1] + 34
        canvas.save(base + '/labels.png')

    # panels sheet: chart + strum crop of every section
    tiles = []
    for idx, s in enumerate(secs):
        c = crop(video, s['rep'], tuple(s['chart']), base + '/_c.png')
        if c is None:
            continue
        st = crop(video, s['rep'], tuple(s['strum']), base + '/_s.png')
        tiles.append((idx, s, c, st))
    if tiles:
        TW = 1400
        H = sum((t[2].size[1] + (t[3].size[1] if t[3] else 0) + 46)
                for t in tiles) + 10
        canvas = Image.new('RGB', (TW, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 5
        for idx, s, c, st in tiles:
            d.rectangle([0, y, TW, y + 30], fill=(0, 0, 0))
            d.text((6, y + 4), '#%d  t=%g-%g  rep=%g' % (idx, s['t0'], s['t1'], s['rep']),
                   font=fnt, fill=(255, 210, 0))
            c2 = c.resize((TW - 16, max(1, int(c.size[1] * (TW - 16) / c.size[0]))))
            canvas.paste(c2, (8, y + 32))
            y += c2.size[1] + 14
            if st is not None:
                st2 = st.resize((TW - 16, max(1, int(st.size[1] * (TW - 16) / st.size[0]))))
                canvas.paste(st2, (8, y))
                y += st2.size[1]
            y += 16
        canvas.save(base + '/panels.png')

    print('%s sections=%d' % (vid, len(secs)))
    for s in secs:
        print('   #%d t=%g-%g rep=%g' % (s['idx'], s['t0'], s['t1'], s['rep']))


if __name__ == '__main__':
    main()
