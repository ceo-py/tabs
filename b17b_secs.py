"""b17b_secs.py - private helper for the Nirvana (b17b) batch.

Re-detects the section-title bar of a video, hashes the lettering of every
sampled title and groups equal titles into runs, so the section list of a video
is exact (no eyeballing of a montage).

    py -3.14 b17b_secs.py <video> <id> [step]

Prints the runs and writes frames/b17b_<id>/secs.png with one row per DISTINCT
title (so the wording can be read once) and frames/b17b_<id>/secs.json
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def bands(flags, min_run=2):
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


def main():
    video, vid = sys.argv[1], sys.argv[2]
    step = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    base = 'frames/b17b_%s' % vid
    tmpd = base + '/psec'
    os.makedirs(tmpd, exist_ok=True)
    for f in os.listdir(tmpd):
        os.remove(os.path.join(tmpd, f))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf',
                    'fps=1/%.4f,scale=640:-1' % step, os.path.join(tmpd, 'p_%04d.png')],
                   check=True, capture_output=True)
    files = sorted(os.path.join(tmpd, f) for f in os.listdir(tmpd) if f.endswith('.png'))

    runs = []
    for i, f in enumerate(files):
        t = round(i * step, 2)
        im = Image.open(f).convert('RGB')
        W, H = im.size
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 110) & (g < 95) & (b < 95)
        xoff = int(W * 0.13)
        cnt = red[:, xoff:].sum(axis=1)
        cands = [(y0, y1) for y0, y1 in bands(cnt > 0.5 * (W - xoff), 2)]
        if not cands:
            continue
        y0, y1 = max(cands, key=lambda c: cnt[c[0]:c[1] + 1].max())
        sub = red[y0:y1 + 1]
        cols = bands(sub.sum(axis=0) > 0, 2)
        if not cols:
            continue
        bx0, bx1 = cols[0][0], cols[-1][1]
        if (bx1 - bx0) < W * 0.25:
            continue
        st = strip_at(video, t, [int(bx0 / W * 1920), int(y0 / H * 1080),
                                 int((bx1 - bx0) / W * 1920), int((y1 - y0 + 1) / H * 1080)],
                      base)
        if st is None:
            continue
        key = hash(st.tobytes())
        if runs and runs[-1]['key'] == key:
            runs[-1]['t1'] = t
            runs[-1]['n'] += 1
            runs[-1]['strip'] = st
        else:
            runs.append({'key': key, 't0': t, 't1': t, 'n': 1, 'strip': st,
                         'box': [int(bx0 / W * 1920), int(y0 / H * 1080),
                                 int((bx1 - bx0) / W * 1920), int((y1 - y0 + 1) / H * 1080)]})

    # merge runs whose strip differs only slightly (anti-aliasing)
    merged = []
    for r_ in runs:
        if merged:
            a = np.asarray(merged[-1]['strip']).astype(np.int16).mean(axis=2)
            b = np.asarray(r_['strip']).astype(np.int16).mean(axis=2)
            if a.shape == b.shape and np.mean(np.abs(a.astype(int) - b.astype(int))) < 6:
                merged[-1]['t1'] = r_['t1']
                merged[-1]['n'] += r_['n']
                continue
        merged.append(r_)

    for r_ in merged:
        r_.pop('strip', None)
    json.dump(merged, open(base + '/secs.json', 'w'), indent=1)

    tiles = []
    seen = []
    for r_ in merged:
        st = strip_at(video, r_['t0'], r_['box'], base)
        if st is not None:
            tiles.append((r_['t0'], st))
    if tiles:
        Wt = max(s.size[0] for _, s in tiles) + 16
        Ht = sum(s.size[1] + 24 for _, s in tiles)
        canvas = Image.new('RGB', (Wt, Ht), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 17)
        y = 0
        for t, s in tiles:
            d.rectangle([0, y, Wt, y + 23], fill=(0, 0, 0))
            d.text((5, y + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
            canvas.paste(s, (8, y + 24))
            y += s.size[1] + 24
        canvas.save(base + '/secs.png')
    print('%s runs=%d' % (vid, len(merged)))
    for r_ in merged:
        print('   t=%g-%g  box=%s' % (r_['t0'], r_['t1'], r_['box']))


def strip_at(video, t, box, base):
    tmp = base + '/_sec.png'
    x0, y0, w, h = box
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1',
           '-vf', 'crop=%d:%d:%d:%d' % (w, h, x0, y0), tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    im = Image.open(tmp).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    r_, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r_ > 195) & (g > 195) & (b > 195)
    cols = bands(white.sum(axis=0) > 0, 1)
    rows_ = bands(white.sum(axis=1) > 0, 1)
    if not cols or not rows_:
        return None
    im = im.crop((cols[0][0], rows_[0][0], cols[-1][1] + 1, rows_[-1][1] + 1))
    if im.size[1] > im.size[0]:
        im = im.rotate(-90, expand=True)
    h = 34
    if im.size[1] != h:
        im = im.resize((max(1, int(im.size[0] * h / max(1, im.size[1]))), h))
    return im


if __name__ == '__main__':
    main()
