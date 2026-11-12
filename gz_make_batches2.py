# -*- coding: utf-8 -*-
"""
Second wave of GuitarZero2HeroExpress card batches.

Batches 1-4 covered the first 50 songs of `gz_tabs_all.json`. This script
takes the NEXT 100 (indices 50..149) and splits them into four batches of 25
so that four agents can work in parallel.

    py -3.14 gz_make_batches2.py

Writes: gz_batches/batch5.json .. batch8.json  (+ _ids.txt for yt-dlp)
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(ROOT, 'gz_batches')
PER_BATCH = 25
START = 50          # the first 50 are already done (batches 1-4)
COUNT = 100


def safe(s):
    """same naming rule as gz_make_batches.py"""
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s).strip()
    return '-'.join(s.split()) or 'Untitled'


def main():
    tabs = json.load(open(os.path.join(ROOT, 'gz_tabs_all.json'), encoding='utf-8'))
    print('catalogue: %d tab songs' % len(tabs))

    # sanity: the batches 1-4 must be the first 50 of the catalogue
    done_ids = set()
    for i in (1, 2, 3, 4):
        p = os.path.join(BATCH_DIR, 'batch%d.json' % i)
        if os.path.exists(p):
            done_ids |= {e['id'] for e in json.load(open(p, encoding='utf-8'))}
    first50 = {e['id'] for e in tabs[:50]}
    if done_ids and not done_ids <= first50:
        print('  ! batches 1-4 do not match the first 50 of the catalogue')
    print('  already done: %d' % len(done_ids))

    window = tabs[START:START + COUNT]
    print('  next %d songs: %s .. %s' % (len(window), window[0]['song'], window[-1]['song']))

    os.makedirs(BATCH_DIR, exist_ok=True)
    used = set()
    for bi in range(5, 9):
        chunk = window[(bi - 5) * PER_BATCH:(bi - 5 + 1) * PER_BATCH]
        items = []
        for r in chunk:
            name = '%s-%s' % (safe(r['artist']), safe(r['song']))
            if name in used:
                name += '-Alt'
            used.add(name)
            items.append({
                'id': r['id'],
                'artist': r['artist'],
                'song': r['song'],
                'tag': r['tag'],
                'rock': r['rock'],
                'out': 'out_gz/%s.png' % name,
                'url': r['url'],
            })
        p = os.path.join(BATCH_DIR, 'batch%d.json' % bi)
        json.dump(items, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        with open(os.path.join(BATCH_DIR, 'batch%d_ids.txt' % bi), 'w', encoding='ascii') as f:
            for it in items:
                f.write(it['id'] + '\n')
        print('  batch%d: %2d songs -> %s' % (bi, len(items), os.path.basename(p)))

    # a combined list of all 100
    allitems = []
    for bi in range(5, 9):
        allitems += json.load(open(os.path.join(BATCH_DIR, 'batch%d.json' % bi), encoding='utf-8'))
    p = os.path.join(BATCH_DIR, 'batch5-8.json')
    json.dump(allitems, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  combined: %d songs -> %s' % (len(allitems), os.path.basename(p)))


if __name__ == '__main__':
    main()
