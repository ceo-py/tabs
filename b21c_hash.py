"""b21c_hash.py - private: enumerate distinct labels in a small region of a
video by binarising the text and grouping visually identical masks (IoU).

Usage: py -3.14 b21c_hash.py <id> <x> <y> <w> <h> [step]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

vid = sys.argv[1]
x, y, w, h = [int(v) for v in sys.argv[2:6]]
step = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0

dur = float(subprocess.run(
    ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
     'stream=duration', '-of', 'csv=p=0', 'dl/w4_%s.mp4' % vid],
    capture_output=True, text=True, check=True).stdout.strip())

tmp = 'frames/b21c_%s/_hash.png' % vid
groups = []          # list of (t0, mask, [times])
t = 0.0
while t < dur:
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i',
                    'dl/w4_%s.mp4' % vid, '-frames:v', '1',
                    '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                   check=True, capture_output=True)
    g = np.asarray(Image.open(tmp).convert('L')).astype(float)
    mask = (g < 128)
    best = None
    for i, (t0, m0, times) in enumerate(groups):
        inter = np.logical_and(mask, m0).sum()
        union = np.logical_or(mask, m0).sum()
        iou = inter / union if union else 0.0
        if iou > 0.85:
            best = i
            break
    if best is None:
        groups.append((t, mask, [t]))
    else:
        groups[best][2].append(t)
    t += step

print('distinct label groups:', len(groups))
for t0, m0, times in groups:
    print('t0=%6.1f  count=%4d  span %6.1f..%6.1f' %
          (t0, len(times), times[0], times[-1]))
