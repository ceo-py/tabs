"""b13_probe.py - private helper for the GuitarZero2HeroExpress card batches.

Generic on-screen panel prober.  For every sampled frame it finds the large
white regions (the tab sheet / chord boxes) and the large saturated-red
regions (the section label bar) in SOURCE pixel coordinates.  Frames that share
the same panel geometry are merged into "states" (one per on-screen section).

For every state a tile is rendered:
    caption  : "t=<a>-<b>s"  +  the section title bar cropped out of the frame
               (rotated upright when the bar is vertical)
    below    : the panel region itself (white sheet + red bar, padded)

so a single image read reveals every on-screen layout of the video, its
section title and its time range.

Usage:
  py -3.14 b13_probe.py <video> <id> [interval]
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SW_TARGET = 480
F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def probe_size(video):
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


def regions(mask, SW, SH, min_frac, max_out=4):
    im = Image.fromarray((mask * 255).astype(np.uint8), 'L')
    im = im.filter(ImageFilter.MinFilter(5))
    a = np.asarray(im) > 0
    h, w = a.shape
    fx, fy = SW / w, SH / h
    res = []
    for y0, y1 in bands(a.sum(axis=1) > 0, 2):
        sub = a[y0:y1 + 1]
        for x0, x1 in bands(sub.sum(axis=0) > 0, 2):
            area = (y1 - y0 + 1) * (x1 - x0 + 1)
            if area < min_frac * w * h:
                continue
            res.append([int(x0 * fx), int(y0 * fy), int((x1 - x0 + 1) * fx), int((y1 - y0 + 1) * fy)])
    res.sort(key=lambda b: -(b[2] * b[3]))
    return res[:max_out]


def frame_at(video, t, box=None):
    tmp = 'frames/_b13_tmp.png'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video, '-frames:v', '1']
    if box:
        cmd += ['-vf', 'crop=%d:%d:%d:%d' % (box[2], box[3], box[0], box[1])]
    cmd += [tmp]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    return Image.open(tmp).convert('RGB')


def merge(a, b):
    """Union of two boxes."""
    x0 = min(a[0], b[0])
    y0 = min(a[1], b[1])
    x1 = max(a[0] + a[2], b[0] + b[2])
    y1 = max(a[1] + a[3], b[1] + b[3])
    return [x0, y0, x1 - x0, y1 - y0]


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
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

    frames = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        white = (r > 205) & (g > 205) & (b > 205)
        red = (r > 130) & (g < 90) & (b < 90)
        frames.append({'t': round(i * interval, 2),
                       'white': regions(white, SW, SH, 0.010),
                       'red': regions(red, SW, SH, 0.004)})

    # ---- merge frames into states by panel geometry (x extent + red bar)
    states = []
    for fr in frames:
        if not fr['white']:
            continue
        wx0 = min(w[0] for w in fr['white'])
        wx1 = max(w[0] + w[2] for w in fr['white'])
        rx0 = min((r[0] for r in fr['red']), default=None)
        rx1 = max((r[0] + r[2] for r in fr['red']), default=None)
        key = (wx0 // 25, wx1 // 25, (rx0 // 25) if rx0 is not None else -1,
               (rx1 // 25) if rx1 is not None else -1)
        hit = None
        for st in states:
            if st['key'] == key:
                hit = st
                break
        if hit is None:
            states.append({'key': key, 't0': fr['t'], 't1': fr['t'], 'best': fr,
                           'white': fr['white'], 'red': fr['red']})
        else:
            hit['t1'] = fr['t']
            if fr['white'][0][3] > hit['white'][0][3]:
                hit['white'] = fr['white']
                hit['red'] = fr['red']
                hit['best'] = fr

    # the frame used for the crop is the one with the tallest panel
    out_states = []
    for st in states:
        ws = st['white']
        reds = st['red']
        box = [min(w[0] for w in ws), min(w[1] for w in ws),
               max(w[0] + w[2] for w in ws) - min(w[0] for w in ws),
               max(w[1] + w[3] for w in ws) - min(w[1] for w in ws)]
        for r in reds:
            if r[0] < box[0] + box[2] + 80 and r[0] + r[2] > box[0] - 80 \
               and r[1] < box[1] + box[3] + 80 and r[1] + r[3] > box[1] - 80:
                box = merge(box, r)
        out_states.append({'t0': st['t0'], 't1': st['t1'], 'rep': st['best']['t'],
                           'box': box, 'white': st['white'], 'red': st['red']})

    json.dump({'sw': SW, 'sh': SH, 'interval': interval, 'states': out_states},
              open(base + '/panels.json', 'w'), indent=1)

    tiles = []
    for idx, st in enumerate(out_states):
        panel = frame_at(video, st['rep'], st['box'])
        if panel is None:
            continue
        lbl = None
        if st['red']:
            lbl = label_strip(video, st['rep'], st['red'][0])
        tiles.append((idx, st, panel, lbl))
    if tiles:
        W = max(t.size[0] for _, _, t, _ in tiles) + 16
        H = sum(t.size[1] + 30 for _, _, t, _ in tiles)
        canvas = Image.new('RGB', (W, H), (18, 18, 18))
        d = ImageDraw.Draw(canvas)
        fnt = ImageFont.truetype(F_BOLD, 18)
        y = 0
        for idx, st, t, lbl in tiles:
            d.rectangle([0, y, W, y + 29], fill=(0, 0, 0))
            d.text((5, y + 4), '#%d t=%s-%ss box=%s' % (idx, st['t0'], st['t1'], st['box']),
                   font=fnt, fill=(255, 210, 0))
            if lbl is not None:
                canvas.paste(lbl, (min(t.size[0] - lbl.size[0], 430), y + 3))
            canvas.paste(t, (8, y + 30))
            y += t.size[1] + 30
        canvas.save(base + '/states.png')
    for idx, st in enumerate(out_states):
        print('#%d t=%s-%s rep=%s box=%s white=%s red=%s' % (idx, st['t0'], st['t1'], st['rep'],
                                                             st['box'], st['white'][:1], st['red'][:2]))


def label_strip(video, t, redbox):
    """Crop the white title glyphs out of the red bar, upright."""
    im = frame_at(video, t, redbox)
    if im is None:
        return None
    a = np.asarray(im).astype(np.int16)
    m = (a[..., 0] > 190) & (a[..., 1] > 190) & (a[..., 2] > 190)
    if m.sum() < 15:
        return None
    cols = bands(m.sum(axis=0) > 0, 1)
    rows = bands(m.sum(axis=1) > 0, 1)
    if not cols or not rows:
        return None
    im = im.crop((cols[0][0], rows[0][0], cols[-1][1] + 1, rows[-1][1] + 1))
    if im.size[1] > im.size[0]:          # vertical bar -> rotate upright
        im = im.rotate(-90, expand=True)
    h = 34
    if im.size[1] > h:
        im = im.resize((max(1, int(im.size[0] * h / im.size[1])), h))
    elif im.size[1] < h:
        im = im.resize((int(im.size[0] * h / max(1, im.size[1])), h))
    return im


if __name__ == '__main__':
    main()
