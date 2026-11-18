"""b19b_titles.py - private helper: a readable sheet of every on-screen section
title of a video, with its timestamp.

For every sample time it cuts the red section-title bar out of the video,
trims it down to the lettering and pastes it into a grid next to the time.
Reading that one image tells me which sections the video has and when.

Usage: py -3.14 b19b_titles.py <id> [step] [cols]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


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


def main():
    vid = sys.argv[1]
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    video = video_path(vid)
    base = 'frames/b19b_%s' % vid
    os.makedirs(base, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    tmp = os.path.join(base, '_t.png')
    items = []
    t = 2.0
    while t < dur:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', tmp]
        if subprocess.run(cmd, capture_output=True).returncode != 0 or not os.path.exists(tmp):
            t += step
            continue
        im = Image.open(tmp).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        red = (r > 120) & (g < 95) & (b < 95)
        bars = red_bars(red, im.size[0], im.size[1])
        if bars:
            bars.sort(key=lambda bb: -(bb[2] * bb[3]))
            x0, y0, w, h = bars[0]
            lbl = im.crop((x0, y0, x0 + w, y0 + h))
            m = bar_text_mask(lbl)
            cols_ = bands(m.sum(axis=0) > 0, 1)
            rows_ = bands(m.sum(axis=1) > 0, 1)
            if cols_ and rows_:
                lbl = lbl.crop((cols_[0][0], rows_[0][0], cols_[-1][1] + 1, rows_[-1][1] + 1))
                items.append((round(t, 1), lbl, [x0, y0, w, h]))
        t += step

    if not items:
        print('NO TITLES', vid)
        return
    cw = max(460, max(i[1].size[0] for i in items) + 20)
    ch = max(40, max(i[1].size[1] for i in items)) + 26
    rows_n = (len(items) + cols - 1) // cols
    canvas = Image.new('RGB', (cw * cols, ch * rows_n), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 20)
    for k, (t, lbl, bar) in enumerate(items):
        cx = (k % cols) * cw
        cy = (k // cols) * ch
        d.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline=(90, 90, 90))
        d.text((cx + 6, cy + 3), 't=%gs  bar=%s' % (t, bar), font=fnt, fill=(255, 210, 0))
        canvas.paste(lbl, (cx + 6, cy + 24))
    canvas.save(os.path.join(base, 'titles.png'))
    print('%s titles=%d -> frames/b19b_%s/titles.png' % (vid, len(items), vid))


if __name__ == '__main__':
    main()
