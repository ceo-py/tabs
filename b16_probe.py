"""Stack crops of one screen region at several timestamps into one image.

Usage:
  py -3.14 b16_probe.py <video.mp4> <out.png> <x,y,w,h> <t1,t2,...>
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

video, out = sys.argv[1], sys.argv[2]
x, y, w, h = [int(v) for v in sys.argv[3].split(',')]
times = [float(v) for v in sys.argv[4].split(',')]

tmp = os.path.splitext(out)[0] + '_parts'
os.makedirs(tmp, exist_ok=True)
paths = []
for i, t in enumerate(times):
    p = os.path.join(tmp, 'p_%03d.png' % i)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), p],
                   check=True, capture_output=True)
    paths.append((t, p))

lab = 26
fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
ims = [(t, Image.open(p).convert('RGB')) for t, p in paths]
W = max(im.size[0] for _, im in ims)
H = sum(im.size[1] + lab for _, im in ims)
canvas = Image.new('RGB', (W, H), (18, 18, 30))
d = ImageDraw.Draw(canvas)
y0 = 0
for t, im in ims:
    d.rectangle([0, y0, W, y0 + lab], fill=(0, 0, 0))
    d.text((6, y0 + 2), 't=%.1fs' % t, font=fnt, fill=(255, 210, 0))
    y0 += lab
    canvas.paste(im, (0, y0))
    y0 += im.size[1]
canvas.save(out)
print('saved', out, canvas.size)
