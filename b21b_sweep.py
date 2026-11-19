"""b21b_sweep.py - private helper (namespace b21b): fast 1 fps sweep of a video
looking for any on-screen notation panel (white/light rectangle) or a flat
dark text-card region.

Usage:
  py -3.14 b21b_sweep.py <id> [fps]
"""
import os
import subprocess
import sys

import numpy as np

W, H = 320, 180


def main():
    vid = sys.argv[1]
    fps = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    cmd = ['ffmpeg', '-v', 'error', '-i', 'dl/w4_%s.mp4' % vid,
           '-vf', 'fps=%g,scale=%d:%d' % (fps, W, H),
           '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
    p = subprocess.run(cmd, capture_output=True)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = len(buf) // (W * H)
    buf = buf[:n * W * H].reshape(n, H, W)
    print('frames', n, 'fps', fps)
    hits = 0
    for i in range(n):
        f = buf[i].astype(np.float32)
        white = (f > 235).mean(axis=1)
        rows = np.where(white > 0.5)[0]
        if len(rows) >= 8:
            hits += 1
            print('t=%7.2f  whiteband rows %d..%d' % (i / fps, rows[0], rows[-1]))
        # flat dark card: large area of very dark pixels
        dark = (f < 25)
        if dark.mean() > 0.55:
            hits += 1
            print('t=%7.2f  DARKCARD %.2f' % (i / fps, dark.mean()))
    print('total flagged frames:', hits)


if __name__ == '__main__':
    main()
