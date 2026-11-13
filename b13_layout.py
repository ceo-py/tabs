"""b13_layout.py - fingerprint the on-screen layout of a video.

Extracts a few frames spread over the duration and reports the big white
panel and the big red label bar of each, in SOURCE pixel coordinates.  This
tells which layout family the video uses (bottom tab panel, upper tab sheet,
chord/strumming overlay) and gives the crop box to use.

Usage: py -3.14 b13_layout.py <video> <id> [video2 id2 ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

FRACS = [0.12, 0.28, 0.45, 0.62, 0.80, 0.92]


def duration(video):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())


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


def big_regions(mask, min_fill=0.55, min_area_frac=0.02):
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
            out.append((x0, x1, y0, y1, area, fill))
    out.sort(key=lambda t: -t[4])
    return out


def main():
    args = sys.argv[1:]
    for i in range(0, len(args), 2):
        video, vid = args[i], args[i + 1]
        if not os.path.exists(video):
            print('%s MISSING %s' % (vid, video))
            continue
        dur = duration(video)
        SW, SH = size(video)
        d = 'frames/b13_%s' % vid
        os.makedirs(d, exist_ok=True)
        print('== %s  dur=%.0fs  %dx%d' % (vid, dur, SW, SH))
        for f in FRACS:
            t = round(dur * f, 1)
            png = '%s/L%02d.png' % (d, int(f * 100))
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
                            '-frames:v', '1', png], capture_output=True)
            if not os.path.exists(png):
                continue
            a = np.asarray(Image.open(png).convert('RGB')).astype(np.int16)
            r, g, b = a[..., 0], a[..., 1], a[..., 2]
            white = (r > 205) & (g > 205) & (b > 205)
            red = (r > 120) & (g < 95) & (b < 95)
            ws = big_regions(white)
            rs = big_regions(red, min_fill=0.55, min_area_frac=0.004)
            wtxt = ' '.join('W[%d-%d,%d-%d]%.2f' % (x0, x1, y0, y1, f) for x0, x1, y0, y1, _, f in ws[:2])
            rtxt = ' '.join('R[%d-%d,%d-%d]%.2f' % (x0, x1, y0, y1, f) for x0, x1, y0, y1, _, f in rs[:2])
            print('  f=%.2f t=%-6s %s %s' % (f, t, wtxt, rtxt))


if __name__ == '__main__':
    main()
