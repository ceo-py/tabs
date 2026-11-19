"""b20a_grab.py - private helper (batch b20a): pull frames out of a video.

Usage:
  py -3.14 b20a_grab.py <id> <t1> [t2 ...]                    # full frames
  py -3.14 b20a_grab.py <id> --crop <t> x y w h [name]         # one crop
"""
import os
import subprocess
import sys


def main():
    vid = sys.argv[1]
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b20a_%s' % vid
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
