"""b20b_grab.py - private helper (batch b20b): pull full frames / crops from a
batch-20 video.  Videos live at dl/w4_<id>.mp4.

Usage:
  py -3.14 b20b_grab.py <id> <t1> [t2 ...]                # full 1920x1080 frames
  py -3.14 b20b_grab.py <id> --crop <t> x y w h [name]    # one crop
"""
import os
import subprocess
import sys

BASE = 'frames/b20b_%s'


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for ' + vid)


def main():
    vid = sys.argv[1]
    video = video_path(vid)
    base = BASE % vid
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
