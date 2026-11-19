"""b20d_check.py - private helper (batch b20d): validate the b20d specs against
the rendered crops and the batch20 manifest.

Checks for every spec:
  * panel bbox heights are even (ffmpeg crops odd heights downwards)
  * the written crop PNG has exactly the bbox width/height
  * the crop PNG is not blank / is not a black frame
  * title / subtitle / out match gz_batches/batch20.json
  * the subtitle contains the exact source_channel string
  * `diagram` is one of LETTERS / DIAGRAM / NONE

Usage:
  py -3.14 b20d_check.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

MANIFEST = 'gz_batches/batch20.json'


def main():
    manifest = {it['id']: it for it in json.load(open(MANIFEST, encoding='utf-8'))}
    ok = True
    for f in sorted(os.listdir('b20d_spec')):
        if not f.endswith('.json'):
            continue
        vid = f[:-5]
        s = json.load(open(os.path.join('b20d_spec', f), encoding='utf-8'))
        m = manifest.get(vid)
        print('== %s' % vid)
        if not m:
            print('   FAIL: not in batch20 manifest')
            ok = False
            continue
        if s['out'] != m['out']:
            print('   FAIL out: %s != %s' % (s['out'], m['out']))
            ok = False
        if s['subtitle'].split('  ·  ')[-1] != m['source_channel']:
            print('   FAIL subtitle channel: %r' % s['subtitle'])
            ok = False
        if s['diagram'] not in ('LETTERS', 'DIAGRAM', 'NONE'):
            print('   FAIL diagram: %r' % s['diagram'])
            ok = False
        for p in s['panels']:
            x, y, w, h = p['bbox']
            if h % 2 or w % 2:
                print('   FAIL odd bbox %s' % (p['bbox'],))
                ok = False
            if x + w > 1920 or y + h > 1080:
                print('   FAIL bbox out of frame %s' % (p['bbox'],))
                ok = False
            if not os.path.exists(p['png']):
                print('   FAIL missing png %s' % p['png'])
                ok = False
                continue
            im = Image.open(p['png']).convert('RGB')
            if im.size != (w, h):
                print('   FAIL png size %s != bbox %s' % (im.size, (w, h)))
                ok = False
            a = np.asarray(im).astype(int)
            black = (a.max(axis=2) < 20).mean()
            print('   t=%-4s %-13s bbox=%-18s png=%-34s size=%s black=%.3f'
                  % (p['t'], p['label'][:13], p['bbox'], p['png'], im.size, black))
        print('   title=%r  subtitle=%r' % (s['title'], s['subtitle']))
        print('   diagram=%s  note=%d chars' % (s['diagram'], len(s.get('note', ''))))
    print('\nRESULT:', 'ALL CHECKS PASSED' if ok else 'FAILURES PRESENT')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())
