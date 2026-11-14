"""b14b_zoom.py - private helper: zoom into a region of a video frame.

Crops a region of a frame and scales it UP so small lettering (chord names,
strumming letters) stays legible when the sheet is read.

Usage:
    py -3.14 b14b_zoom.py <video> <out.png> --box x,y,w,h --t 84 [--scale 2]
"""
import os
import subprocess
import sys

from PIL import Image


def main():
    video = sys.argv[1]
    out = sys.argv[2]
    t = float(sys.argv[3])
    box = [int(v) for v in sys.argv[4].split(',')]
    scale = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
    x, y, w, h = box
    tmp = out + '.raw.png'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(tmp).convert('RGB')
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    im.save(out)
    os.remove(tmp)
    print('wrote', out, im.size)


if __name__ == '__main__':
    main()
