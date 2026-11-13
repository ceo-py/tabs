"""Rebuild stack.png for a prepared video.

Groups the sections by the title text inside the red header bar (so a section
that repeats keeps only one or two representatives) and scales the panels so
the section titles and chord names stay readable.

Usage: py -3.14 b16_stack.py <frames_dir> [max_width] [per_title]
"""
import hashlib, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def title_sig(im):
    """Hash of the white glyphs inside the red header bar of a panel crop."""
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    redrow = ((r > 125) & (g < 80) & (b < 80)).sum(axis=1)
    w = a.shape[1]
    rows = np.flatnonzero(redrow > 0.5 * w)
    if not len(rows):
        return 'none'
    y0, y1 = rows[0], rows[-1]
    sub = a[y0:y1 + 1]
    m = (sub[:, :, 0] > 195) & (sub[:, :, 1] > 195) & (sub[:, :, 2] > 195)
    return hashlib.md5(m.tobytes()).hexdigest()[:8]


def main():
    d = sys.argv[1]
    mw = int(sys.argv[2]) if len(sys.argv) > 2 else 1100
    per_title = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    scan = json.load(open(os.path.join(d, 'scan.json'), encoding='utf-8'))

    groups = []
    gmap = {}
    for s in scan['sections']:
        if not os.path.exists(s['png']):
            continue
        im = Image.open(s['png']).convert('RGB')
        sg = title_sig(im)
        key = sg
        if key not in gmap:
            gmap[key] = len(groups)
            groups.append([])
        g = groups[gmap[key]]
        if len(g) < per_title:
            g.append(('SEC %d  t=%d-%ds' % (s['i'], s['t0'], s['t1']), s['png'], im))
        else:
            g.append(None)
    # extras (top-right chord boxes) always shown once per title group
    extra = []
    egmap = {}
    for s in scan['sections']:
        for e in s.get('extra', []):
            if not os.path.exists(e['png']):
                continue
            im = Image.open(e['png']).convert('RGB')
            sg = 'x' + title_sig(im)
            if sg not in egmap:
                egmap[sg] = len(extra)
                extra.append(('EXTRA SEC %d (t=%ds)' % (s['i'], s['t0']), e['png'], im))
            elif len(extra) > 0:
                pass

    items = [x for g in groups for x in g if x] + extra
    lab = 30
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 22)
    ims = []
    for name, p, im in items:
        if im.size[0] > mw:
            im = im.resize((mw, int(im.size[1] * mw / im.size[0])), Image.LANCZOS)
        ims.append((name, im))
    if not ims:
        print('NO IMAGES')
        return
    W = max(im.size[0] for _, im in ims)
    H = sum(im.size[1] + lab for _, im in ims)
    while H > 5200 and W > 640:
        sc = 640.0 / W
        ims = [(n, i.resize((int(i.size[0] * sc), int(i.size[1] * sc)), Image.LANCZOS))
               for n, i in ims]
        W = max(i.size[0] for _, i in ims)
        H = sum(i.size[1] + lab for _, i in ims)
    canvas = Image.new('RGB', (W, H), (18, 18, 30))
    dr = ImageDraw.Draw(canvas)
    y = 0
    for name, im in ims:
        dr.rectangle([0, y, W, y + lab], fill=(0, 0, 0))
        dr.text((6, y + 3), name, font=fnt, fill=(255, 210, 0))
        y += lab
        canvas.paste(im, (0, y))
        y += im.size[1]
    canvas.save(os.path.join(d, 'stack.png'))
    print('saved', d, canvas.size, len(ims), 'groups', len(groups))


if __name__ == '__main__':
    main()
