"""b14b_shot.py - private helper: full-resolution panel crops for reading.

Renders the given crop boxes at FULL source resolution (no downscaling) so the
chord names and the strumming letters stay legible, and can additionally zoom
into a sub-rectangle of the panel.

Usage:
    py -3.14 b14b_shot.py <video> <outdir> --box x,y,w,h --times 10,40,80
    py -3.14 b14b_shot.py <video> <outdir> --box x,y,w,h --times 10,40 \
        --zoom x,y,w,h          (sub-rect of the panel, zoomed)
"""
import os
import subprocess
import sys


def main():
    argv = sys.argv[1:]
    video, outdir = argv[0], argv[1]
    rest = argv[2:]
    box = None
    zoom = None
    times = []
    i = 0
    while i < len(rest):
        if rest[i] == '--box':
            box = [int(v) for v in rest[i + 1].split(',')]
            i += 2
        elif rest[i] == '--zoom':
            zoom = [int(v) for v in rest[i + 1].split(',')]
            i += 2
        elif rest[i] == '--times':
            times = [float(v) for v in rest[i + 1].split(',')]
            i += 2
        else:
            times.append(float(rest[i]))
            i += 1
    os.makedirs(outdir, exist_ok=True)
    for t in times:
        x, y, w, h = box
        zx, zy, zw, zh = zoom if zoom else (0, 0, w, h)
        ax = x + zx
        ay = y + zy
        # keep the zoom inside the panel
        ax = max(x, min(ax, x + w - 1))
        ay = max(y, min(ay, y + h - 1))
        zw = min(zw, x + w - ax)
        zh = min(zh, y + h - ay)
        out = os.path.join(outdir, 's_%s_%d_%d_%d_%d.png' % (
            str(t).replace('.', '_'), ax, ay, zw, zh))
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', '-vf',
               'crop=%d:%d:%d:%d' % (zw, zh, ax, ay), out]
        r = subprocess.run(cmd, capture_output=True)
        print('t=%s -> %s  rc=%d  %s' % (t, out, r.returncode,
                                        r.stderr.decode('utf-8', 'replace')[-200:]))


if __name__ == '__main__':
    main()
