"""Build a compact 'titles' image per prepared video: one red header strip
(centre part, where the section title is drawn) per section, labelled with its
time range.  Reading this single small image tells which sections the video
shows and when they start.

Usage: py -3.14 b16_titles.py <frames_dir>
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def main():
    d = sys.argv[1]
    scan = json.load(open(os.path.join(d, 'scan.json'), encoding='utf-8'))
    lab = 26
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    strips = []
    mode = scan.get('mode', 'A')
    for s in scan['sections']:
        p = s['png']
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        a = np.asarray(im).astype(np.int16)
        r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        redm = (r > 125) & (g < 80) & (b < 80)
        redrow = redm.sum(axis=1)
        redcol = redm.sum(axis=0)
        if mode == 'B':
            cols = np.flatnonzero(redcol > 0.12 * a.shape[0])
            if not len(cols):
                continue
            x0, x1 = int(cols.min()), int(cols.max())
            strip = im.crop((x0, 0, x1 + 1, im.size[1]))
            strip = strip.rotate(90, expand=True)
        else:
            rows = np.flatnonzero(redrow > 0.4 * a.shape[1])
            if not len(rows):
                continue
            y0, y1 = int(rows[0]), int(rows[-1]) + 1
            strip = im.crop((0, y0, im.size[0], y1))
            w = strip.size[0]
            half = w // 2
            strip = strip.crop((half // 2, 0, half // 2 + half, strip.size[1]))
        strips.append(('t=%d-%ds' % (s['t0'], s['t1']), strip))
    if not strips:
        print('NO STRIPS')
        return
    W = max(im.size[0] for _, im in strips)
    H = sum(im.size[1] + lab for _, im in strips)
    canvas = Image.new('RGB', (W, H), (18, 18, 30))
    dr = ImageDraw.Draw(canvas)
    y = 0
    for name, im in strips:
        dr.rectangle([0, y, W, y + lab], fill=(0, 0, 0))
        dr.text((6, y + 2), name, font=fnt, fill=(255, 210, 0))
        y += lab
        canvas.paste(im, (0, y))
        y += im.size[1]
    canvas.save(os.path.join(d, 'titles.png'))
    print('saved', d, canvas.size, len(strips))


if __name__ == '__main__':
    main()
