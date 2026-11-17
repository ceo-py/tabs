"""b18d_rows.py - private helper for the b18d batch.

Crops an arbitrary horizontal band out of the video at several timestamps and
stacks the crops into one image (with a caption per row) so the on-screen text
can be read in a single look.

Usage:
  py -3.14 b18d_rows.py <video> <id> <out.png> <x> <y> <w> <h> <t1,t2,...>
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    video = sys.argv[1]
    vid = sys.argv[2]
    outp = sys.argv[3]
    x, y, w, h = (int(v) for v in sys.argv[4:8])
    times = [float(t) for t in sys.argv[8].split(',')]
    base = 'frames/b18d_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = base + '/_row.png'
    rows = []
    for t in times:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            continue
        rows.append((t, Image.open(tmp).convert('RGB')))
    if not rows:
        print('NO ROWS')
        return
    W = max(im.size[0] for _, im in rows) + 20
    H = len(rows) * (26 + rows[0][1].size[1] + 4)
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(F_BOLD, 18)
    yy = 0
    for t, im in rows:
        d.rectangle([0, yy, W, yy + 25], fill=(0, 0, 0))
        d.text((5, yy + 3), 't=%g' % t, font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (10, yy + 26))
        yy += 26 + im.size[1] + 4
    canvas.crop((0, 0, W, yy)).save(outp)
    print('saved', outp, canvas.size)


if __name__ == '__main__':
    main()
