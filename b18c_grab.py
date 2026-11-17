"""b18c_grab.py - private helper: pull single frames / crops out of a video.

Usage:
  py -3.14 b18c_grab.py <id> <t1> [t2 ...]              # full 1920x1080 frames
  py -3.14 b18c_grab.py <id> --crop <t> x y w h [name]  # one crop
"""
import os
import subprocess
import sys

VIDS = {
    'MmmhEd7j8K8': 'dl/w4_MmmhEd7j8K8.mp4',
    'jmNmAnr_Vr4': 'dl/w4_jmNmAnr_Vr4.mp4',
    'YXHCL2Y-e0U': 'dl/w4_YXHCL2Y-e0U.mp4',
    'mbnmB_hTfiM': 'dl/w4_mbnmB_hTfiM.mp4',
    'LRXRm0eMZZY': 'dl/w4_LRXRm0eMZZY.mp4',
    'JvRLYuiyURk': 'dl/w4_JvRLYuiyURk.mp4',
    '_YrDIC5tZcA': 'dl/w4__YrDIC5tZcA.mp4',
}


def main():
    vid = sys.argv[1]
    video = VIDS[vid]
    base = 'frames/b18c_%s' % vid
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
