"""b17c_scan.py - private scanner for the b17c (Red Hot Chili Peppers) videos.

Two on-screen layouts exist in this batch:

A) "bottom sheet": a wide horizontal red section-title bar with the TAB sheet
   underneath, from the right edge of the wooden fretboard down to the bottom
   of the frame.

B) "top-right panel": a white TAB sheet in the upper right with a narrow
   VERTICAL red title bar glued to its right edge.

For every sampled frame the scanner finds the red title bar, measures the
graphic region, extracts the white lettering at FULL resolution (stable
signatures) and groups the frames into sections.  It writes:

  frames/b17c_<id>/sections.json   - sections, time ranges, crop boxes
  frames/b17c_<id>/labels.png      - every distinct section title, upright
  frames/b17c_<id>/scan.png        - one full-res crop per section occurrence

Usage: py -3.14 b17c_scan.py <video> <id> [interval]
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
SW_SAMPLE = 480


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


def glyph_box(im):
    """Bounding box of the white lettering inside a red bar crop.

    The crop's last row is often the white top edge of the tab sheet, so a
    pixel-thin white line must not count as lettering -> require the column
    to carry at least 5 white pixels.
    """
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 170) & (g > 170) & (b > 170)
    if white.sum() < 12:
        return None
    cols = bands(white.sum(axis=0) >= 5, 1)
    rows = bands(white.sum(axis=1) >= 3, 1)
    if not cols or not rows:
        return None
    return (cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1)


def sheet_left(white, y0, y1, x_from):
    """Left edge of the white sheet that ends just left of column x_from."""
    rows = y1 - y0 + 1
    x = x_from
    gap = 0
    while x > 0 and gap <= 8:
        frac = white[y0:y1 + 1, x].mean()
        if frac > 0.12:
            x -= 1
            gap = 0
        else:
            gap += 1
            x -= 1
    return x + 1


def analyze(im, SW, SH):
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 110) & (g < 100) & (b < 100)
    white = (r > 200) & (g > 200) & (b > 200)
    H, W = red.shape
    px, py = SW / W, SH / H

    # ---- horizontal red bars (layout A) -------------------------------
    xoff = int(0.22 * W)
    rows = red[:, xoff:].sum(axis=1)
    hb = [bb for bb in bands(rows > 0.55 * (W - xoff), 3)
          if 0.35 * H < bb[0] < 0.80 * H and (bb[1] - bb[0]) < 0.16 * H]

    # ---- vertical red bars (layout B) --------------------------------
    cols = red.sum(axis=0)
    vb = [bb for bb in bands(cols > 0.15 * H, 3)
          if bb[0] > 0.70 * W and (bb[1] - bb[0]) < 0.14 * W]

    if hb:
        y0, y1 = max(hb, key=lambda bb: (bb[1] - bb[0]))
        sub = red[y0:y1 + 1]
        cc = bands(sub.sum(axis=0) > 0.4 * (y1 - y0 + 1), 2)
        if not cc:
            return None
        bx0, bx1 = cc[0][0], cc[-1][1]
        if bx0 < 0.08 * W:
            return None                      # full-width bar (outro / overlay)
        # the sheet under the bar must be mostly white
        sheet = white[y1 + 1:H, bx0:W]
        if sheet.size == 0 or sheet.mean() < 0.25:
            return None
        # the red bar ends where the white sheet starts - cut the bar there so
        # the sheet's white edge never enters the lettering crop
        sheet_top = H
        for yy in range(y0 + 4, H):
            if white[yy, bx0:W].mean() > 0.6:
                sheet_top = yy
                break
        bh = max(12, sheet_top - y0 - 2)
        region = [int(bx0 * px), int(y0 * py),
                  int((W - bx0) * px), int((H - y0) * py)]
        bar = [int(bx0 * px), int(y0 * py), int((bx1 - bx0 + 1) * px), int(bh * py)]
        return {'layout': 'A', 'region': region, 'bar': bar,
                'band_y0': int(y0 * py), 'sheet_top': int(sheet_top * py),
                'bx0': int(bx0 * px), 'bw': int((bx1 - bx0 + 1) * px)}

    if vb:
        bx0, bx1 = max(vb, key=lambda bb: (bb[1] - bb[0]))
        sub = red[:, bx0:bx1 + 1]
        rr = bands(sub.sum(axis=1) > 0.5 * (bx1 - bx0 + 1), 2)
        if not rr:
            return None
        by0, by1 = rr[0][0], rr[-1][1]
        px0 = sheet_left(white, by0, by1, bx0)
        region = [int(px0 * px), int(by0 * py),
                  int((W - px0) * px), int((by1 - by0 + 1) * py)]
        bar = [int(bx0 * px), int(by0 * py), int((bx1 - bx0 + 1) * px),
               int((by1 - by0 + 1) * py)]
        return {'layout': 'B', 'region': region, 'bar': bar,
                'bx0': int(bx0 * px), 'bw': int((bx1 - bx0 + 1) * px)}
    return None


def bar_crop(video, t, bar, out):
    x, y, w, h = bar
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), out],
                   capture_output=True)
    if not os.path.exists(out):
        return None
    return Image.open(out).convert('RGB')


def label_of(lbl):
    """(signature mask, upright label image) for a red bar crop.

    The signature keeps the aspect ratio of the lettering (height fixed at 20)
    and pads to a fixed width, so a short title and a long title can never be
    confused.
    """
    box = glyph_box(lbl)
    if box is None:
        return None, None
    t = lbl.crop(box)
    if t.size[1] > t.size[0]:
        t = t.rotate(-90, expand=True)
    a = np.asarray(t.convert('L'))
    m = (a > 150).astype(np.float32)
    h = 20
    w = max(1, int(round(t.size[0] * h / max(1, t.size[1]))))
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
        (min(w, 340), h))).astype(np.float32) / 255.0
    sig = np.zeros((h, 340), dtype=np.float32)
    sig[:, :m.shape[1]] = m
    return sig, t


def main():
    video, vid = sys.argv[1], sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    base = 'frames/b17c_%s' % vid
    tmpd = base + '/s'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=%d:-1' % (interval, SW_SAMPLE),
                    os.path.join(tmpd, 'p_%04d.png')], check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))

    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                         capture_output=True, text=True).stdout.strip().split(',')
    SW, SH = int(out[0]), int(out[1])

    groups = []
    frames = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        info = analyze(im, SW, SH)
        if not info:
            frames.append({'t': i * interval, 'info': None})
            continue
        frames.append({'t': i * interval, 'info': info})

    # ---- canonicalise the title-bar geometry ---------------------------
    # The detected bar edges wobble by a few pixels between frames; a fixed
    # box keeps the lettering crop (and therefore the signature) stable.
    def med(vals):
        return sorted(vals)[len(vals) // 2]

    infos = [f['info'] for f in frames if f.get('info')]
    for lay in ('A', 'B'):
        li = [i for i in infos if i['layout'] == lay]
        if not li:
            continue
        mx = med([i['bx0'] for i in li])
        mw = med([i['bw'] for i in li])
        if lay == 'A':
            mst = med([i['sheet_top'] for i in li])
            mh = med([i['sheet_top'] - i['band_y0'] for i in li])
            for i in li:
                i['bar'] = [mx, mst - mh, mw, max(12, mh - 2)]
                i['region'] = [mx, mst - mh, 1920 - mx, 1080 - (mst - mh)]
        else:
            for i in li:
                i['bar'][0] = mx
                i['bar'][2] = mw

    # ---- keep only frames whose title bar has the modal geometry ------
    for lay in ('A', 'B'):
        ws = [f['info']['bar'][2] for f in frames if f.get('info') and f['info']['layout'] == lay]
        hs = [f['info']['bar'][3] for f in frames if f.get('info') and f['info']['layout'] == lay]
        if not ws:
            continue
        mw, mh = sorted(ws)[len(ws) // 2], sorted(hs)[len(hs) // 2]
        for f in frames:
            if f.get('info') and f['info']['layout'] == lay:
                b = f['info']['bar']
                f['rel'] = abs(b[2] - mw) <= 8 and abs(b[3] - mh) <= 25

    # ---- crop the lettering out of every reliable frame -----------------
    for f in frames:
        if not f.get('rel'):
            continue
        bc = bar_crop(video, f['t'], f['info']['bar'], base + '/_bar.png')
        if bc is None:
            continue
        sig, lbl = label_of(bc)
        if sig is None:
            f['rel'] = False
            continue
        f['sig'] = sig
        f['lbl'] = lbl

    # ---- cluster the reliable frames by their lettering ----------------
    # Section titles are static on screen, so a change of the lettering
    # between two neighbouring samples marks a new section.
    clusters = []
    prev = None
    for f in frames:
        if not f.get('rel'):
            continue
        if prev is not None and np.abs(prev['sig'] - f['sig']).mean() < 0.012:
            prev['end'] = f['t']
            continue
        c = {'sig': f['sig'], 'lbl': f['lbl'], 'start': f['t'], 'end': f['t']}
        clusters.append(c)
        prev = c

    # ---- timeline: assign every frame to its section --------------------
    segs = []
    for c in clusters:
        segs.append({'t': (c['start'] + c['end']) / 2.0, 'start': c['start'],
                     'end': c['end'], 'lbl': c['lbl'], 'sig': c['sig']})

    # region / bar of every segment = the ones of its middle frame
    for s in segs:
        rep = None
        for f in frames:
            if f.get('rel') and abs(f['t'] - s['t']) < 1.6:
                rep = f
                break
        if rep is None:
            for f in frames:
                if f.get('rel') and abs(f['t'] - s['t']) < 4.0:
                    rep = f
                    break
        if rep is None:
            continue
        s['rep'] = rep['t']
        s['region'] = rep['info']['region']
        s['bar'] = rep['info']['bar']
        s['layout'] = rep['info']['layout']

    secs = [{'layout': s.get('layout', 'A'), 'ranges': [[s['start'], s['end']]],
             'rep': s.get('rep', s['t']), 'region': s.get('region', [0, 0, 1, 1]),
             'bar': s.get('bar', [0, 0, 1, 1])} for s in segs]
    json.dump({'sw': SW, 'sh': SH, 'sections': secs},
              open(base + '/sections.json', 'w'), indent=1)

    # ---- labels sheet ------------------------------------------------
    lbls = []
    for s in segs:
        l = s['lbl']
        if l is None:
            continue
        h = 44
        if l.size[1] != h:
            l = l.resize((max(1, int(l.size[0] * h / max(1, l.size[1]))), h))
        lbls.append(([[s['start'], s['end']]], l))
    if lbls:
        Wl = max(l.size[0] for _, l in lbls) + 20
        Hl = sum(l.size[1] + 34 for _, l in lbls) + 10
        canvas = Image.new('RGB', (Wl, Hl), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 5
        for rng, l in lbls:
            txt = '  '.join('t=%g-%g' % (a, b) for a, b in rng)
            d.text((6, y), txt, font=fnt, fill=(255, 210, 0))
            canvas.paste(l, (6, y + 26))
            y += l.size[1] + 34
        canvas.save(base + '/labels.png')

    # ---- scan sheet: full-res crop per section occurrence -------------
    tiles = []
    for idx, s in enumerate(secs):
        t = s['rep']
        tmp = base + '/_c.png'
        r = s['region']
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (r[2], r[3], r[0], r[1]),
                        tmp], capture_output=True)
        if not os.path.exists(tmp):
            continue
        tiles.append((idx, t, [[s['ranges'][0][0], s['ranges'][0][1]]], Image.open(tmp).convert('RGB')))
    if tiles:
        TW = 1500
        H = sum(t.size[1] + 34 for _, _, _, t in tiles) + 10
        canvas = Image.new('RGB', (TW, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 20)
        y = 5
        for idx, t, rng, im in tiles:
            im = im.resize((TW - 16, max(1, int(im.size[1] * (TW - 16) / im.size[0]))))
            d.rectangle([0, y, TW, y + 30], fill=(0, 0, 0))
            d.text((6, y + 4), '#%d  t=%g-%g  layout=%s  crop=%s' % (
                idx, rng[0][0], rng[0][1], secs[idx]['layout'], secs[idx]['region']),
                font=fnt, fill=(255, 210, 0))
            canvas.paste(im, (8, y + 32))
            y += im.size[1] + 34
        canvas.save(base + '/scan.png')

    print('%s sections=%d tiles=%d' % (vid, len(secs), len(tiles)))
    for idx, s in enumerate(secs):
        rng = ','.join('%g-%g' % (a, b) for a, b in s['ranges'][:5])
        print('   #%d %s t=%s region=%s bar=%s' % (idx, s['layout'], rng, s['region'], s['bar']))


if __name__ == '__main__':
    main()
