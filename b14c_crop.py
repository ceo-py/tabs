"""b14c_crop.py - extract one crop from a video frame for inspection.

Usage: py -3.14 b14c_crop.py <video_id> <t> <x> <y> <w> <h> <out.png>
"""
import os
import subprocess
import sys


def pick(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    return None


def main():
    vid, t, x, y, w, h, out = sys.argv[1:8]
    v = pick(vid)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % float(t), '-i', v,
           '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (int(w), int(h), int(x), int(y)), out]
    subprocess.run(cmd, check=True)
    print(out)


if __name__ == '__main__':
    main()
