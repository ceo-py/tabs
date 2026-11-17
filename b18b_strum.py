"""b18b_strum.py - stack the strumming rows of several panels for reading."""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

# video, timestamp, caption, crop x, crop y, crop w, crop h
JOBS = [
    ('dl/w4_7oqpJKjW7nE.mp4', 52, 'angie chorus', 800, 880, 760, 130),
    ('dl/w4_7oqpJKjW7nE.mp4', 230, 'angie bridge', 800, 880, 760, 130),
    ('dl/w4_UjScq2EYzbI.mp4', 8, 'disarm intro', 800, 880, 760, 130),
    ('dl/w4_UjScq2EYzbI.mp4', 24, 'disarm verse', 800, 880, 760, 130),
    ('dl/w4_UjScq2EYzbI.mp4', 70, 'disarm chorus', 800, 880, 760, 130),
    ('dl/w4_UjScq2EYzbI.mp4', 180, 'disarm outro', 800, 880, 760, 130),
]

ims = []
tmp = 'frames/b18b_3-7BlYrqLoA/_s.png'
for v, t, name, x, y, w, h in JOBS:
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', v, '-frames:v', '1',
                    '-vf', 'crop=%d:%d:%d:%d,scale=iw*2:ih*2:flags=lanczos' % (w, h, x, y),
                    tmp], check=True, capture_output=True)
    ims.append((name, Image.open(tmp).convert('RGB')))

W = max(i.size[0] for _, i in ims)
H = sum(i.size[1] + 18 for _, i in ims)
c = Image.new('RGB', (W, H), (20, 20, 20))
d = ImageDraw.Draw(c)
f = ImageFont.truetype(F_BOLD, 14)
y = 0
for name, i in ims:
    d.text((4, y + 2), name, font=f, fill=(255, 210, 0))
    c.paste(i, (0, y + 18))
    y += i.size[1] + 18
c.save('frames/b18b_3-7BlYrqLoA/str_disarm.png')
print(c.size)
