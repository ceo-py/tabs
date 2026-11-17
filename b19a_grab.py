"""b19a_grab.py - private helper (batch b19a): pull single frames / crops out of a video.

Usage:
  py -3.14 b19a_grab.py <id> <t1> [t2 ...]                 # full frames
  py -3.14 b19a_grab.py <id> --crop <t> x y w h [name]    # one crop
"""
import os
import subprocess
import sys


def video_for(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    raise SystemExit('no video for ' + vid)


def main():
    vid = sys.argv[1]
    video = video_for(vid)
    base = 'frames/b19a_%s' % vid
    os.makedirs(base, exist_ok=True)
    args = sys.argv[2:]
    if args and args[0] == '--crop':
        t = float(args[1])
        x, y, w, h = [int(v) for v in args[2:6]]
        name = args[6] if len(args) > 6 else 'crop_%s' % str(t).replace('.', '_')
        out = os.path.join(base, name + '.png')
        vf = 'crop=%d:%d:%d:%d' % (w, h, x, y)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', vf, out], check=True, capture_output=True)
        print(out)
        return
    for a in args:
        t = float(a)
        out = os.path.join(base, 'full_%s.png' % str(t).replace('.', '_'))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', out], check=True, capture_output=True)
        print(out)


if __name__ == '__main__':
    main()
