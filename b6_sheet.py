"""Build a labeled contact sheet of cropped panels from a video.

Usage:
  py -3.14 b6_sheet.py <video_id> <crop W:H:X:Y> <out_dir> <t1,t2,t3,...>
Cropped PNGs are written to <out_dir>/c_<t>.png and a labeled sheet to
<out_dir>/sheet.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

vid = sys.argv[1]
crop = sys.argv[2]
outdir = sys.argv[3]
times = [t.strip() for t in sys.argv[4].split(',') if t.strip()]
os.makedirs(outdir, exist_ok=True)
src = 'dl/v_%s.mp4' % vid
imgs = []
if crop == '-':
    # assemble existing c_*.png in outdir, using `times` as filenames
    for t in times:
        p = '%s/%s.png' % (outdir, t)
        if os.path.exists(p):
            imgs.append((t, Image.open(p).convert('RGB')))
    times = [t for t in times]
else:
    for t in times:
        p = '%s/c_%s.png' % (outdir, t.replace('.', '_'))
        if not os.path.exists(p):
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i', src,
                            '-frames:v', '1', '-vf', 'crop=' + crop, p], check=False)
    imgs = []
    for t in times:
        p = '%s/c_%s.png' % (outdir, t.replace('.', '_'))
        if not os.path.exists(p):
            continue
        imgs.append((t, Image.open(p).convert('RGB')))
if not imgs:
    print('NO IMGS')
    sys.exit()
TW = int(sys.argv[5]) if len(sys.argv) > 5 else 900
LAB = 26
scaled = []
for t, im in imgs:
    h = int(im.size[1] * TW / im.size[0])
    scaled.append((t, im.resize((TW, h))))
cols = min(int(sys.argv[6]) if len(sys.argv) > 6 else 2, len(scaled))
rows = (len(scaled) + cols - 1) // cols
rh = max(im.size[1] for _, im in scaled) + LAB
canvas = Image.new('RGB', (cols * TW, rows * rh), (18, 18, 18))
d = ImageDraw.Draw(canvas)
fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
for i, (t, im) in enumerate(scaled):
    x = (i % cols) * TW
    y = (i // cols) * rh
    canvas.paste(im, (x, y))
    d.rectangle([x, y + im.size[1], x + TW, y + rh], fill=(0, 0, 0))
    d.text((x + 6, y + im.size[1] + 3), 't=%ss' % t, font=fnt, fill=(255, 210, 0))
canvas.save('%s/sheet.png' % outdir)
print('saved', '%s/sheet.png' % outdir, canvas.size, len(scaled))
