# -*- coding: utf-8 -*-
"""
Build gz_batches/batch19.json — the fourteen acts the user picked for the
next wave:

Lady Gaga & Bradley Cooper, Lady Gaga, Phil Collins, Pink Floyd, R.E.M.,
REM, Rage Against The Machine, Santana, Shania Twain, Slipknot,
The Cranberries, The Offspring, The Verve, Tracy Chapman, Wheatus

Three of these songs (the two Lady Gaga ones and Shallow) already sat in
batch15 / batch16. They are MOVED here so no song is listed in two batch
files and no card path is ever produced twice.

    py -3.14 _b19_gen.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTISTS = [
    'Lady Gaga & Bradley Cooper', 'Lady Gaga', 'Phil Collins', 'Pink Floyd',
    'R.E.M.', 'REM', 'Rage Against The Machine', 'Santana', 'Shania Twain',
    'Slipknot', 'The Cranberries', 'The Offspring', 'The Verve',
    'Tracy Chapman', 'Wheatus',
]
# songs that are moved out of their old batch file
MOVE = {
    'YGGjna1GkK0',   # Lady Gaga - Always Remember Us This Way  (batch15)
    'gz0mC6yiMFQ',   # Lady Gaga - I'll Never Love Again       (batch15)
    '11plqWEM8cc',   # Lady Gaga & Bradley Cooper - Shallow    (batch16)
}


def slug(text):
    """Artist-Song with dashes, like every other card in out_gz/"""
    text = re.sub(r"['’]", '', text)
    text = re.sub(r'[^A-Za-z0-9]+', '-', text)
    return text.strip('-')


def load_batch(n):
    p = os.path.join(ROOT, 'gz_batches', 'batch%d.json' % n)
    return p, json.load(open(p, encoding='utf-8-sig'))


def save_batch(p, rows):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    name = os.path.basename(p)[5:-5]          # 'batch15.json' -> '15'
    ids = os.path.join(os.path.dirname(p), 'batch%s_ids.txt' % name)
    with open(ids, 'w', encoding='utf-8') as f:
        f.write('\n'.join(r['id'] for r in rows) + '\n')


def main():
    master = json.load(open(os.path.join(ROOT, 'gz_tabs_all.json'), encoding='utf-8'))
    catalog = json.load(open(os.path.join(ROOT, 'songs.json'), encoding='utf-8'))
    done = set(e['id'] for e in catalog if e.get('channel') == 'GuitarZero2HeroExpress')

    # 1. take the moved songs out of their old batch files
    for n in (15, 16):
        p, rows = load_batch(n)
        kept = [r for r in rows if r['id'] not in MOVE]
        if len(kept) != len(rows):
            save_batch(p, kept)
            print('batch%d: %d -> %d songs' % (n, len(rows), len(kept)))

    # 2. every id that another batch file already owns
    taken = set()
    for fn in sorted(os.listdir(os.path.join(ROOT, 'gz_batches'))):
        if not fn.startswith('batch') or not fn.endswith('.json') or fn == 'batch19.json':
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

    path = os.path.join(ROOT, 'gz_batches', 'batch19.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'gz_batches', 'batch19_ids.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(r['id'] for r in rows) + '\n')

    print('\nbatch19: %d songs' % len(rows))
    for r in rows:
        print('  %-28s %-40s %s' % (r['artist'], r['song'], r['id']))
    for r in skipped:
        print('  (kept in the batch that owns it) %-22s %-40s %s' % (r['artist'], r['song'], r['id']))
    for r in published:
        print('  (already published) %-22s %-40s %s' % (r['artist'], r['song'], r['id']))


if __name__ == '__main__':
    main()
