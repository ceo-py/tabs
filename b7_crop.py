"""Batch7 helper: extract a cropped frame from a video.

Usage:
  py -3.14 b7_crop.py <VIDEO_ID> <SEC> <NAME> <W:H:X:Y>
Writes frames/b7_<VIDEO_ID>/<NAME>.png
"""
import os
import subprocess
import sys

vid, sec, name, crop = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
outdir = os.path.join('frames', 'b7_' + vid)
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, name + '.png')
cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(sec), '-i', os.path.join('dl', 'v_%s.mp4' % vid),
       '-frames:v', '1', '-vf', 'crop=' + crop, out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print('ERR', r.stderr[-500:])
    sys.exit(1)
print('ok', out)
