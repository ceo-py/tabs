# -*- coding: utf-8 -*-
"""
Fourth wave: the rest of the paused batches + the next 100 catalogue songs.

  * batch6_rest2.json / batch11_rest.json / batch12_rest.json
        -> only the songs of those batches whose card is still missing
  * batch13.json .. batch16.json
        -> catalogue index 250..349 (the next 100 songs)

    py -3.14 gz_make_batches4.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(ROOT, 'gz_batches')
PER_BATCH = 25
WAVE3_START = 250      # catalogue index of the first song of this wave


def safe(s):
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s).strip()
    return '-'.join(s.split()) or 'Untitled'


def load(name):
    return json.load(open(os.path.join(BATCH_DIR, name + '.json'), encoding='utf-8'))


def write(name, items):
    p = os.path.join(BATCH_DIR, name + '.json')
    json.dump(items, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(BATCH_DIR, name + '_ids.txt'), 'w', encoding='ascii') as f:
        for it in items:
            f.write(it['id'] + '\n')
    print('  %-16s %2d songs' % (name, len(items)))
    return items


def done(r):
    return os.path.exists(os.path.join(ROOT, r['out'].replace('/', os.sep)))


def used_names():
    used = set()
    for bi in range(1, 13):
        for r in load('batch%d' % bi):
            used.add(os.path.splitext(os.path.basename(r['out']))[0])
    return used


def main():
    tabs = json.load(open(os.path.join(ROOT, 'gz_tabs_all.json'), encoding='utf-8'))
    print('catalogue: %d tab songs' % len(tabs))

    print('\nstill missing of the paused batches:')
    write('batch6_rest2', [r for r in load('batch6_rest') if not done(r)])
    write('batch11_rest', [r for r in load('batch11') if not done(r)])
    write('batch12_rest', [r for r in load('batch12') if not done(r)])

    print('\nnext 100 songs (catalogue %d..%d):' % (WAVE3_START, WAVE3_START + 99))
    window = tabs[WAVE3_START:WAVE3_START + 100]
    used = used_names()
    for bi in range(13, 17):
        chunk = window[(bi - 13) * PER_BATCH:(bi - 13 + 1) * PER_BATCH]
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
        write('batch%d' % bi, items)


if __name__ == '__main__':
    main()
