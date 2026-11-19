"""b21c_scan.py - private scan: 1 frame/sec, report mean colour and how much
of the frame is near-white / near-black / dark-blue, to spot layout changes.

Usage: py -3.14 b21c_scan.py <id> [step]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid = sys.argv[1]
step = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

dur = float(subprocess.run(
    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
     'stream=duration', '-of', 'csv=p=0', 'dl/w4_%s.mp4' % vid],
    capture_output=True, text=True, check=True).stdout.strip())

tmp = 'frames/b21c_%s/_scan.png' % vid
t = 0.0
while t < dur:
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1', tmp],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(int)
    H, W, _ = a.shape
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    white = ((r > 225) & (g > 225) & (b > 225)).mean()
    black = ((r < 40) & (g < 40) & (b < 40)).mean()
    blue = ((b > 60) & (b < 200) & (r < 60) & (g < 60)).mean()
    print('%6.1f  white %.3f  black %.3f  blue %.3f  mean %s' %
          (t, white, black, blue, a.reshape(-1, 3).mean(axis=0).round(0)))
    t += step
