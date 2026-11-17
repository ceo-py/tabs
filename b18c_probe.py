"""b18c_probe.py - private helper: pixel profile of a region (white/red coverage
per row and per column) so crop boxes can be trimmed exactly.

Usage: py -3.14 b18c_probe.py <id> <x> <y> <w> <h> [t]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

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
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    t = float(sys.argv[6]) if len(sys.argv) > 6 else 10.0
    video = VIDS[vid]
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_probe_tmp.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                    '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                   check=True, capture_output=True)
    a = np.asarray(Image.open(tmp).convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (r > 150) & (g > 150) & (b > 150)
    red = (r > 110) & (g < 90) & (b < 90)
    bright = (r > 90) | (g > 90) | (b > 90)
    print('region x=%d y=%d w=%d h=%d  t=%.1f' % (x, y, w, h, t))
    print('--- rows (abs y : white%% red%% bright%%)')
    for i in range(a.shape[0]):
        print('%4d : %5.1f %5.1f %5.1f' % (y + i, 100 * white[i].mean(),
                                            100 * red[i].mean(), 100 * bright[i].mean()))
    print('--- cols (abs x : white%% red%% bright%%)')
    for j in range(a.shape[1]):
        print('%4d : %5.1f %5.1f %5.1f' % (x + j, 100 * white[:, j].mean(),
                                            100 * red[:, j].mean(), 100 * bright[:, j].mean()))


if __name__ == '__main__':
    main()
