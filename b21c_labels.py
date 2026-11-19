"""b21c_labels.py - private: save one representative crop per distinct label
group (as found by b21c_hash.py) and montage them for reading.

Usage: py -3.14 b21c_labels.py <id> <x> <y> <w> <h> [step]
"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

vid = sys.argv[1]
x, y, w, h = [int(v) for v in sys.argv[2:6]]
step = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0

dur = float(subprocess.run(
    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
     'stream=duration', '-of', 'csv=p=0', 'dl/w4_%s.mp4' % vid],
    capture_output=True, text=True, check=True).stdout.strip())

tmp = 'frames/b21c_%s/_lbl.png' % vid
outdir = 'frames/b21c_%s/labels' % vid
groups = []
t = 0.0
while t < dur:
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1',
                    '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                   check=True, capture_output=True)
    im = Image.open(tmp).convert('L')
    mask = np.asarray(im).astype(float) < 128
    best = None
    for i, (t0, m0, times) in enumerate(groups):
        union = np.logical_or(mask, m0).sum()
        iou = np.logical_and(mask, m0).sum() / union if union else 0.0
        if iou > 0.85:
            best = i
            break
    if best is None:
        groups.append((t, mask, [t]))
    else:
        groups[best][2].append(t)
    t += step

import os
os.makedirs(outdir, exist_ok=True)
tiles = []
for i, (t0, m0, times) in enumerate(groups):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t0, '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1',
                    '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y),
                    '%s/g%02d.png' % (outdir, i)], check=True, capture_output=True)
    tiles.append((t0, Image.open('%s/g%02d.png' % (outdir, i)).convert('RGB')))

cols = 3
scale = 900.0 / max(t.size[0] for _, t in tiles)
tiles = [(t, im.resize((int(im.size[0] * scale), int(im.size[1] * scale))))
         for t, im in tiles]
rows = (len(tiles) + cols - 1) // cols
tw = max(t.size[0] for _, t in tiles)
th = max(t.size[1] for _, t in tiles)
W = cols * tw + (cols + 1) * 12
H = rows * (th + 28) + 12
canvas = Image.new('RGB', (W, H), (18, 18, 18))
d = ImageDraw.Draw(canvas)
fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
for i, (t, im) in enumerate(tiles):
    cx = 12 + (i % cols) * (tw + 12)
    cy = 12 + (i // cols) * (th + 28)
    d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
    d.text((cx + 4, cy + 3), 't=%gs' % t, font=fnt, fill=(255, 210, 0))
    canvas.paste(im, (cx, cy + 27))
out = 'frames/b21c_%s/labels.png' % vid
canvas.save(out)
print(out, canvas.size, 'groups:', len(groups))
