# -*- coding: utf-8 -*-
"""
Build gz_batches/batch18.json — ten classic rock acts the user picked:
Metallica, Queen, The Rolling Stones, The Smashing Pumpkins, U2,
Oasis, Pearl Jam, Stone Sour, The Police, Radiohead.

Only lessons that are NOT in the published catalog are taken, and a song that
already belongs to another batch file keeps it there (no double booking).

    py -3.14 _b18_gen.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTISTS = [
    'Metallica', 'Queen', 'The Rolling Stones', 'The Smashing Pumpkins', 'U2',
    'Oasis', 'Pearl Jam', 'Stone Sour', 'The Police', 'Radiohead',
]


def slug(text):
    """Artist-Song with dashes, like every other card in out_gz/"""
    text = re.sub(r"['’]", '', text)
    text = re.sub(r'[^A-Za-z0-9]+', '-', text)
    return text.strip('-')


def main():
    master = json.load(open(os.path.join(ROOT, 'gz_tabs_all.json'), encoding='utf-8'))
    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    done = set(e['id'] for e in catalog if e.get('channel') == 'GuitarZero2HeroExpress')

    # a song that already has a batch file keeps it there (batch17 already
    # owns some of these songs - they must not be listed twice)
    taken = set()
    for fn in sorted(os.listdir(os.path.join(ROOT, 'gz_batches'))):
        if not fn.startswith('batch') or not fn.endswith('.json') or fn == 'batch18.json':
            continue
        try:
            rows = json.load(open(os.path.join(ROOT, 'gz_batches', fn), encoding='utf-8-sig'))
        except Exception:
            continue
        for r in rows:
            taken.add(r['id'])

    rows = []
    skipped = []
    published = []
    for r in master:
        if r['artist'] not in ARTISTS:
            continue
        if r['id'] in done:
            published.append(r)
            continue
        if r['id'] in taken:
            skipped.append(r)
            continue
        out = 'out_gz/%s.png' % slug('%s - %s' % (r['artist'], r['song']))
        rows.append({
            'id': r['id'],
            'artist': r['artist'],
            'song': r['song'],
            'tag': r.get('tag', ''),
            'rock': bool(r.get('rock')),
            'out': out,
            'url': r['url'],
        })

    path = os.path.join(ROOT, 'gz_batches', 'batch18.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    with open(os.path.join(ROOT, 'gz_batches', 'batch18_ids.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(r['id'] for r in rows) + '\n')

    print('batch18: %d songs' % len(rows))
    for r in rows:
        print('  %-22s %-46s %s' % (r['artist'], r['song'], r['id']))
    for r in skipped:
        print('  (kept in the batch that owns it) %-22s %-46s %s' % (r['artist'], r['song'], r['id']))
    for r in published:
        print('  (already published) %-22s %-46s %s' % (r['artist'], r['song'], r['id']))


if __name__ == '__main__':
    main()
