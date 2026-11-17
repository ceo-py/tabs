"""b18a_crop.py - cut one crop out of a video frame.

Usage: py -3.14 b18a_crop.py <video_id> <time> <x> <y> <w> <h> <out.png>
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    vid, t, x, y, w, h, out = sys.argv[1:8]
    video = 'dl/w4_%s.mp4' % vid
    if not os.path.exists(video):
        for c in ('dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
            if os.path.exists(c):
                video = c
                break
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%s:%s:%s:%s' % (w, h, x, y), out],
                   check=True, capture_output=True)
    print('ok', out)


if __name__ == '__main__':
    main()
