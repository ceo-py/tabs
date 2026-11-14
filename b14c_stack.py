"""b14c_stack.py - stack crops of several timestamps into one image for reading.

Usage: py -3.14 b14c_stack.py <video_id> <out.png> <t1> <t2> ...  [bbox x y w h]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
W = 1700


def pick(vid):
    for c in ('dl/w4_%s.mp4' % vid, 'dl/gz_%s.mp4' % vid, 'dl/v_%s.mp4' % vid):
        if os.path.exists(c) and os.path.getsize(c) > 1000000:
            return c
    return None


def main():
    vid, out = sys.argv[1], sys.argv[2]
    ts = [float(a) for a in sys.argv[3:]]
    bbox = [244, 560, 1676, 516]
    if len(ts) > 3 and all(a.lstrip('-').isdigit() for a in sys.argv[-4:]) and len(sys.argv) > 7:
        bbox = [int(a) for a in sys.argv[-4:]]
        ts = [float(a) for a in sys.argv[3:-4]]
    v = pick(vid)
    tmpd = 'frames/_b14c_tmp'
    os.makedirs(tmpd, exist_ok=True)
    tiles = []
    for t in ts:
        p = os.path.join(tmpd, 'c_%.0f.png' % t)
        x, y, w, h = bbox
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', v,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), p],
                       check=True, capture_output=True)
        im = Image.open(p).convert('RGB')
        if im.size[0] > W:
            im = im.resize((W, int(im.size[1] * W / im.size[0])))
        tiles.append((t, im))
    H = sum(t_.size[1] + 26 for _, t_ in tiles)
    canvas = Image.new('RGB', (W + 16, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(F_BOLD, 18)
    y = 0
    for t, im in tiles:
        d.rectangle([0, y, W + 16, y + 25], fill=(0, 0, 0))
        d.text((5, y + 3), 't=%gs' % t, font=f, fill=(255, 210, 0))
        canvas.paste(im, (8, y + 26))
        y += im.size[1] + 26
    canvas.save(out)
    print(out, canvas.size)


if __name__ == '__main__':
    main()
