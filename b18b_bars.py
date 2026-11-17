"""b18b_bars.py - stack the red section-title bars of a video into one image.

Usage: py -3.14 b18b_bars.py <video> <id> <t1> <t2> ...
Writes frames/b18b_<id>/bars.png
"""
import os
import subprocess
import sys

from PIL import Image

video, vid = sys.argv[1], sys.argv[2]
ts = [float(t) for t in sys.argv[3:]]
base = 'frames/b18b_%s' % vid
os.makedirs(base, exist_ok=True)
tmp = base + '/_bar.png'

strips = []
for t in ts:
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=1920:70:0:552', tmp]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(tmp).convert('RGB')
    strips.append((t, im))

W = 1920
H = sum(s.size[1] for _, s in strips)
canvas = Image.new('RGB', (W, H), (0, 0, 0))
y = 0
for t, s in strips:
    canvas.paste(s, (0, y))
    y += s.size[1]
canvas = canvas.resize((1280, int(H * 1280 / W)))
canvas.save(base + '/bars.png')
print('bars.png', canvas.size, len(ts), 'strips')
