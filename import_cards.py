# -*- coding: utf-8 -*-
"""
Catalog importer — merges every lesson card found in the repo into the single
source of truth `songs.json` (repo root).

    py -3.14 import_cards.py            # merge new cards, keep manual edits
    py -3.14 import_cards.py --force    # overwrite metadata of existing entries

Sources:
  out_gz/*.png   + gz_batches/batch*.json   -> GuitarZero2HeroExpress
  out/*.png      + ROCK-CARDS-INDEX.md      -> BernadetteTeachesMusic

`add_song.py` adds one entry by hand; both write into the same songs.json.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, 'songs.json')


# --- BernadetteTeachesMusic: file, title, artist, format ---------------------
BERN = [
    ('Eagles-Hotel-California-Short.png', 'Hotel California', 'The Eagles', 'Short'),
    ('Hotel-California.png', 'Hotel California', 'The Eagles', 'Long'),
    ('Sweet-Child-O-Mine.png', "Sweet Child O' Mine", "Guns N' Roses", 'Long'),
    ('Queen-Crazy-Little-Thing-Called-Love.png', 'Crazy Little Thing Called Love', 'Queen', 'Short'),
    ('CCR-Bad-Moon-Rising-Jam-Along.png', 'Bad Moon Rising (Jam-Along)', 'Creedence Clearwater Revival', 'Short'),
    ('CCR-Bad-Moon-Rising-Easy-Chords.png', 'Bad Moon Rising (Easy Chords)', 'Creedence Clearwater Revival', 'Long'),
    ('CCR-Bad-Moon-Rising-Challenge.png', 'Bad Moon Rising (CCR Challenge)', 'Creedence Clearwater Revival', 'Long'),
    ('CCR-Have-You-Ever-Seen-The-Rain.png', 'Have You Ever Seen the Rain', 'Creedence Clearwater Revival', 'Long'),
    ('CCR-Have-You-Ever-Seen-The-Rain-Short.png', 'Have You Ever Seen the Rain', 'Creedence Clearwater Revival', 'Short'),
    ('CCR-Down-on-the-Corner.png', 'Down on the Corner', 'Creedence Clearwater Revival', 'Long'),
    ('CCR-Proud-Mary.png', 'Proud Mary', 'Creedence Clearwater Revival', 'Long'),
    ('White-Stripes-Were-Going-To-Be-Friends.png', "We're Going To Be Friends", 'The White Stripes', 'Long'),
    ('Coldplay-Yellow.png', 'Yellow', 'Coldplay', 'Long'),
    ('Coldplay-Yellow-Short-2023.png', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Yellow-Short-2023b.png', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Yellow-Short-2024.png', 'Yellow', 'Coldplay', 'Short'),
    ('Coldplay-Viva-La-Vida.png', 'Viva La Vida', 'Coldplay', 'Short'),
    ('Pearl-Jam-Last-Kiss.png', 'Last Kiss', 'Pearl Jam', 'Short'),
    ('REM-Losing-My-Religion.png', 'Losing My Religion', 'R.E.M.', 'Short'),
    ('Elvis-Love-Me-Tender.png', 'Love Me Tender', 'Elvis Presley', 'Short'),
    ('Johnny-Cash-I-Walk-The-Line.png', 'I Walk the Line', 'Johnny Cash', 'Short'),
    ('John-Denver-Take-Me-Home-Country-Roads.png', 'Take Me Home, Country Roads', 'John Denver', 'Short'),
]


def bern_urls():
    """video url per Bernadette card, taken from ROCK-CARDS-INDEX.md"""
    idx = os.path.join(ROOT, 'ROCK-CARDS-INDEX.md')
    urls = {}
    if os.path.exists(idx):
        for line in open(idx, encoding='utf-8'):
            m = re.match(r'^\|\s*\d+\s*\|(.*)$', line.strip())
            if not m:
                continue
            cells = [c.strip() for c in m.group(1).split('|')]
            if len(cells) < 6:
                continue
            card = cells[3].replace('`', '')
            lm = re.search(r'\[link\]\((https?://[^)]+)\)', cells[5])
            if lm and card:
                urls[os.path.basename(card)] = lm.group(1)
    return urls


def discover():
    """-> list of catalog entries found on disk"""
    found = {}

    # --- GuitarZero2HeroExpress ---
    rows = []
    for bi in range(1, 17):
        p = os.path.join(ROOT, 'gz_batches', 'batch%d.json' % bi)
        if not os.path.exists(p):
            continue
        rows += json.load(open(p, encoding='utf-8'))

    seen = set()
    for r in rows:
        out = r['out'].replace('\\', '/')
        if out in seen:                       # two videos, same song -> unique file name
            stem, ext = os.path.splitext(out)
            new = stem + '-Alt' + ext
            n = 2
            allouts = {x['out'].replace('\\', '/') for x in rows}
            while new in allouts:
                new = '%s-Alt%d%s' % (stem, n, ext)
                n += 1
            print('  name collision: %s -> %s' % (out, new))
            out = new
        seen.add(out)

        src = os.path.join(ROOT, out)
        if not os.path.exists(src):
            continue
        found[r['id']] = {
            'id': r['id'],
            'title': r['song'],
            'artist': r['artist'],
            'tag': r.get('tag', ''),
            'rock': bool(r.get('rock')),
            'channel': 'GuitarZero2HeroExpress',
            'url': r['url'],
            'card': out,
        }

    # --- BernadetteTeachesMusic ---
    urls = bern_urls()
    for fname, song, artist, fmt in BERN:
        src = os.path.join(ROOT, 'out', fname)
        if not os.path.exists(src):
            continue
        url = urls.get(fname, '')
        if not url:
            m = re.search(r'([A-Za-z0-9_-]{11})', fname)
            url = 'https://www.youtube.com/watch?v=' + m.group(1) if m else ''
        found[fname] = {
            'id': fname,
            'title': song,
            'artist': artist,
            'tag': fmt,
            'rock': True,
            'channel': 'BernadetteTeachesMusic',
            'url': url,
            'card': 'out/' + fname,
        }
    return found


def load_catalog():
    if os.path.exists(CATALOG):
        return json.load(open(CATALOG, encoding='utf-8'))
    return []


def save_catalog(entries):
    entries.sort(key=lambda s: (s.get('artist', '').lower(), s.get('title', '').lower(), s.get('channel', '')))
    with open(CATALOG, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)


def main():
    force = '--force' in sys.argv
    cat = load_catalog()
    by_id = {e['id']: e for e in cat}
    found = discover()

    added = updated = 0
    for vid, entry in found.items():
        if vid in by_id:
            if force:
                by_id[vid].update(entry)
                updated += 1
        else:
            cat.append(entry)
            added += 1

    # drop entries whose card file no longer exists (unless it was added by hand)
    keep, dropped = [], 0
    for e in cat:
        if e.get('card') and not os.path.exists(os.path.join(ROOT, e['card'])):
            dropped += 1
            continue
        keep.append(e)
    cat = keep

    save_catalog(cat)
    print('catalog: %d songs  (+%d new, %d refreshed, %d removed)' % (len(cat), added, updated, dropped))
    print('-> %s' % os.path.relpath(CATALOG, ROOT))


if __name__ == '__main__':
    main()
