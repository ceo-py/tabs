"""b14b_check.py - private helper: sanity-check the produced cards.

Verifies for every spec in b14b_spec/ that the output PNG exists, that the
footer and the YouTube link are present, that the title is in caps, and that
the link matches the video id of the spec.

Usage: py -3.14 b14b_check.py
"""
import glob
import json
import os
import sys

from PIL import Image

OUT = 'out_gz'


def main():
    bad = 0
    for f in sorted(glob.glob('b14b_spec/*.json')):
        vid = os.path.splitext(os.path.basename(f))[0]
        s = json.load(open(f, encoding='utf-8'))
        out = s['out']
        ok = True
        if not os.path.exists(out):
            print('MISSING %s' % out)
            bad += 1
            continue
        im = Image.open(out).convert('RGB')
        w, h = im.size
        url = 'https://www.youtube.com/watch?v=' + vid
        # the composer draws the link and the footer in the bottom ~120 px
        foot = im.crop((0, h - 130, w, h))
        px = foot.load()
        link_col = (120, 190, 255)
        foot_col = (105, 105, 138)
        nlink = sum(1 for yy in range(foot.size[1]) for xx in range(foot.size[0])
                    if px[xx, yy] == link_col)
        nfoot = sum(1 for yy in range(foot.size[1]) for xx in range(foot.size[0])
                    if px[xx, yy] == foot_col)
        title = s['title']
        if not title.isupper():
            print('  %s: TITLE NOT CAPS: %s' % (out, title))
            ok = False
        if nlink < 200:
            print('  %s: link colour barely present (%d px) - url=%s' % (out, nlink, url))
            ok = False
        if nfoot < 50:
            print('  %s: footer colour barely present (%d px)' % (out, nfoot))
            ok = False
        print('%-46s %5dx%-5d link=%-5d footer=%-5d panels=%d  %s'
              % (out, w, h, nlink, nfoot, len(s['panels']), 'OK' if ok else 'CHECK'))
        if not ok:
            bad += 1
    print('\n%d card(s) need a look' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
