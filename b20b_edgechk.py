"""b20b_edgechk.py - private helper (batch b20b): for a video frame, report the
leftmost/rightmost ink column inside the chord-name band of the score sheet.
Ink touching the frame edge means a chord name is cut off by the crop.

Usage: py -3.14 b20b_edgechk.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

from PIL import Image

BASE = 'frames/b20b_%s'


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for ' + vid)


def sheet_top(px, W, H):
    for y in range(300, H):
        n = 0
        cnt = 0
        for x in range(0, W, 4):
            r, g, b = px[x, y]
            cnt += 1
            if r > 232 and g > 232 and b > 232:
                n += 1
        if n / float(cnt) > 0.92:
            return y
    return None


def main():
    vid = sys.argv[1]
    video = video_path(vid)
    base = BASE % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_edge_tmp.png')
    for a in sys.argv[2:]:
        t = float(a)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        W, H = im.size
        px = im.load()
        top = sheet_top(px, W, H)
        band_top = top if top is not None else 400
        lo, hi = None, None
        for y in range(band_top, band_top + 120):
            for x in range(W):
                if sum(px[x, y]) / 3.0 < 200:
                    if lo is None or x < lo:
                        lo = x
                    if hi is None or x > hi:
                        hi = x
        # also the whole sheet, to see the staff itself
        print('t=%-7s top=%s band_ink=[%s..%s]' % (t, top, lo, hi))


if __name__ == '__main__':
    main()
