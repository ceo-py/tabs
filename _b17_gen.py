# -*- coding: utf-8 -*-
"""
Build gz_batches/batch17.json — the three rock bands the user picked:
Red Hot Chili Peppers (8), Nirvana (7), Linkin Park (6).

Only lessons that are NOT in the published catalog are taken.

    py -3.14 _b17_gen.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTISTS = ['Red Hot Chili Peppers', 'Nirvana', 'Linkin Park']


def slug(text):
    """Artist-Song with dashes, like every other card in out_gz/"""
    text = re.sub(r"['’]", '', text)
    text = re.sub(r'[^A-Za-z0-9]+', '-', text)
    return text.strip('-')


def main():
    master = json.load(open(os.path.join(ROOT, 'gz_tabs_all.json'), encoding='utf-8'))
    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    done = set(e['id'] for e in catalog if e.get('channel') == 'GuitarZero2HeroExpress')

    # a song that already has a batch file keeps it there (batch16 already
    # owns the Linkin Park songs - they must not be listed twice)
    taken = set()
    for fn in sorted(os.listdir(os.path.join(ROOT, 'gz_batches'))):
        if not fn.startswith('batch') or not fn.endswith('.json') or fn == 'batch17.json':
            continue
        try:
            rows = json.load(open(os.path.join(ROOT, 'gz_batches', fn), encoding='utf-8-sig'))
        except Exception:
            continue
        for r in rows:
            taken.add(r['id'])

    rows = []
    skipped = []
    for r in master:
        if r['artist'] not in ARTISTS:
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

    path = os.path.join(ROOT, 'gz_batches', 'batch17.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    with open(os.path.join(ROOT, 'gz_batches', 'batch17_ids.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(r['id'] for r in rows) + '\n')

    print('batch17: %d songs' % len(rows))
    for r in rows:
        print('  %-22s %-46s %s' % (r['artist'], r['song'], r['id']))
    for r in skipped:
        print('  (kept in the batch that owns it) %-22s %-46s %s' % (r['artist'], r['song'], r['id']))


if __name__ == '__main__':
    main()
