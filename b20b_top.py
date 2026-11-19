"""b20b_top.py - private helper (batch b20b): detect the y where the white
score sheet starts in a given frame of a batch-20 video (the sheet is the
lower panel; above it is the guitarist video).

Usage: py -3.14 b20b_top.py <id> <t1> [t2 ...]
"""
import os
import subprocess
import sys

from PIL import Image


def video_path(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c):
            return c
    raise SystemExit('no video for ' + vid)


def white_frac(px, y, W):
    n = 0
    step = 4
    cnt = 0
    for x in range(0, W, step):
        r, g, b = px[x, y]
        cnt += 1
        if r > 232 and g > 232 and b > 232:
            n += 1
    return n / float(cnt)


def main():
    vid = sys.argv[1]
    video = video_path(vid)
    base = 'frames/b20b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_top_tmp.png')
    for a in sys.argv[2:]:
        t = float(a)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', tmp], check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        W, H = im.size
        px = im.load()
        top = None
        for y in range(300, H):
            if white_frac(px, y, W) > 0.92:
                top = y
                break
        # bottom: last row that is still mostly white
        bot = None
        for y in range(H - 1, 300, -1):
            if white_frac(px, y, W) > 0.92:
                bot = y
                break
        print('t=%-7s sheet_top=%s sheet_bottom=%s' % (t, top, bot))


if __name__ == '__main__':
    main()
