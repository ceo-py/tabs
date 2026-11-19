"""b20d_scan3.py - private helper (batch b20d): fast, broad layout probe.

Decodes the whole video once (fps=2) into a temporary frame folder and for
every frame reports the widest run of
  * "paper" rows  (bright, almost colourless) -> a printed TAB page
  * "red"   rows  (the Sparky Guitar red banner)
in the left and the right half of the frame separately, so that a vertical
TAB strip on the left is found as well as a horizontal one on the right.

Usage:
  py -3.14 b20d_scan3.py <id> [fps]
"""
import glob
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image


def longest_run(mask):
    best = cur = 0
    for v in mask:
        if v:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


def scan_window(a, x0, x1):
    win = a[:, x0:x1]
    mxp = win.max(axis=2)
    mnp = win.min(axis=2)
    pa = (mxp > 190) & ((mxp - mnp) <= 22)
    rd = ((win[..., 0] > 110) & (win[..., 0] - win[..., 1] > 55)
          & (win[..., 0] - win[..., 2] > 55))
    return (longest_run(pa.sum(axis=1) > 200), longest_run(rd.sum(axis=1) > 200))


def main():
    vid = sys.argv[1]
    fps = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    video = 'dl/w4_%s.mp4' % vid
    tmpdir = os.path.join('frames', 'b20d_%s' % vid, '_scan3')
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    os.makedirs(tmpdir, exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vf', 'fps=%g' % fps,
                    os.path.join(tmpdir, 'f_%05d.png')], check=True, capture_output=True)
    files = sorted(glob.glob(os.path.join(tmpdir, 'f_*.png')))
    print('== %s  frames=%d fps=%g' % (vid, len(files), fps))
    groups = []
    for i, f in enumerate(files):
        a = np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
        pl, rl = scan_window(a, 0, 960)
        pr, rr = scan_window(a, 960, 1920)
        key = (pl // 40, rl // 40, pr // 40, rr // 40)
        t = i / fps
        if groups and groups[-1][0] == key:
            groups[-1][2] = t
        else:
            groups.append([key, t, t])
        if pl >= 120 or rl >= 120 or pr >= 120 or rr >= 120:
            print('  t=%-7.1f  L paper=%3d red=%3d   R paper=%3d red=%3d' % (t, pl, rl, pr, rr))
    print('-- layout groups (t0..t1 key=(Lpaper,Lred,Rpaper,Rred)/40):')
    for key, t0, t1 in groups:
        print('  %7.1f..%7.1f  %s' % (t0, t1, key))
    shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    main()
