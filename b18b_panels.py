"""b18b_panels.py - montage the on-screen panel content of a video for reading.

For every given timestamp it crops the white sheet that carries the TAB /
chord names / strumming pattern (the red title bar is cropped off) and stacks
the crops so the content can be read at full resolution.

Usage: py -3.14 b18b_panels.py <video> <id> <t1> <t2> ... [--bar]
        --bar  also keeps the red title bar in the crop
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
OUT_W = 1500


def main():
    args = sys.argv[3:]
    with_bar = '--bar' in args
    args = [a for a in args if a != '--bar']
    video, vid = sys.argv[1], sys.argv[2]
    ts = [float(a) for a in args]
    base = 'frames/b18b_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = base + '/_p.png'
    Y0, Y1 = (552, 1080) if with_bar else (620, 1080)

    crops = []
    for t in ts:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
               '-frames:v', '1', '-vf', 'crop=1672:%d:248:%d' % (Y1 - Y0, Y0), tmp]
        subprocess.run(cmd, check=True, capture_output=True)
        im = Image.open(tmp).convert('RGB')
        crops.append((t, im))

    CH = 4
    for c0 in range(0, len(crops), CH):
        chunk = crops[c0:c0 + CH]
        h = sum(im.size[1] + 26 for _, im in chunk)
        canvas = Image.new('RGB', (OUT_W, h), (20, 20, 20))
        d = ImageDraw.Draw(canvas)
        f = ImageFont.truetype(F_BOLD, 16)
        y = 0
        for t, im in chunk:
            d.text((4, y + 4), 't=%g' % t, font=f, fill=(255, 210, 0))
            im2 = im.resize((OUT_W - 16, int(im.size[1] * (OUT_W - 16) / im.size[0])))
            canvas.paste(im2, (8, y + 26))
            y += im2.size[1] + 26
        out = '%s/panels_%d.png' % (base, c0)
        canvas.save(out)
        print(out, canvas.size)


if __name__ == '__main__':
    main()
