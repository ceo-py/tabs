"""b18c_block.py - private helper: sample a rectangular region of a video and
group consecutive identical-looking frames into sections.

Usage: py -3.14 b18c_block.py <id> <x> <y> <w> <h> [step]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def sig(im):
    a = np.asarray(im.convert('L').resize((160, 90))).astype(np.int16)
    return a


def same(a, b):
    if a is None or b is None:
        return False
    return float(np.abs(a - b).mean()) < 3.0


def main():
    vid = sys.argv[1]
    x, y, w, h = [int(v) for v in sys.argv[2:6]]
    step = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
    video = 'dl/w4_%s.mp4' % vid
    base = 'frames/b18c_%s' % vid
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, '_blk_tmp.png')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout.strip())
    groups = []
    for i in range(int(dur / step) + 1):
        t = i * step
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % t, '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        s = sig(Image.open(tmp))
        if groups and same(s, groups[-1]['s']):
            groups[-1]['t1'] = t
            continue
        groups.append({'t0': t, 't1': t, 's': s})
    merged = []
    for g in groups:
        if merged and g['t0'] - merged[-1]['t1'] <= step * 1.6 and same(g['s'], merged[-1]['s']):
            merged[-1]['t1'] = g['t1']
        else:
            merged.append(g)
    tiles = []
    for g in merged:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '%.3f' % g['t0'], '-i', video,
                        '-frames:v', '1', '-vf', 'crop=%d:%d:%d:%d' % (w, h, x, y), tmp],
                       check=True, capture_output=True)
        tiles.append((g, Image.open(tmp).convert('RGB')))
    if not tiles:
        print('NONE', vid)
        return
    tw = 1180
    tiles = [(g, im.resize((tw, max(1, int(im.size[1] * tw / im.size[0])))))
             for g, im in tiles]
    cols = 2
    rows = (len(tiles) + cols - 1) // cols
    th = max(im.size[1] for _, im in tiles)
    W = cols * tw + (cols + 1) * 12
    H = rows * (th + 28) + 12
    canvas = Image.new('RGB', (W, H), (18, 18, 18))
    d = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 20)
    for i, (g, im) in enumerate(tiles):
        cx = 12 + (i % cols) * (tw + 12)
        cy = 12 + (i // cols) * (th + 28)
        d.rectangle([cx, cy, cx + tw, cy + 26], fill=(0, 0, 0))
        d.text((cx + 4, cy + 3), 't=%gs-%gs' % (g['t0'], g['t1']), font=fnt, fill=(255, 210, 0))
        canvas.paste(im, (cx, cy + 27))
    out = os.path.join(base, 'block.png')
    canvas.save(out)
    print(out, canvas.size)
    for g in merged:
        print('  t=%g-%g' % (g['t0'], g['t1']))


if __name__ == '__main__':
    main()
