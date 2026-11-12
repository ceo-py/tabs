"""Scan a video for frames containing a bright (white) rectangular panel in a
given region, to locate TAB / graphic overlays.

Usage: py -3.14 b6_scan.py <video_id> <x> <y> <w> <h> <step> <t0> <t1>
"""
import os
import subprocess
import sys

from PIL import Image, ImageStat

vid = sys.argv[1]
x, y, w, h = (int(v) for v in sys.argv[2:6])
step = float(sys.argv[6])
t0 = float(sys.argv[7])
t1 = float(sys.argv[8])
src = 'dl/v_%s.mp4' % vid
outdir = 'frames/scan_%s' % vid
os.makedirs(outdir, exist_ok=True)
t = t0
while t <= t1:
    p = '%s/s_%06.1f.png' % (outdir, t)
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.1f' % t, '-i', src,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), p],
                       check=False)
    if os.path.exists(p):
        im = Image.open(p).convert('L')
        st = ImageStat.Stat(im)
        print('%7.1f  mean=%.1f  bright=%d' % (t, st.mean[0], sum(1 for v in im.getdata() if v > 200)))
    t += step
