# -*- coding: utf-8 -*-
"""
Site asset builder — turns the catalog (songs.json) into the static site.

    py -3.14 site_build.py

Reads : songs.json              (single source of truth)
Writes: site/data/songs.json    (served manifest)
        site/cards/<slug>.webp  (full card, max width 1600)
        site/thumbs/<slug>.webp (preview, 4:5 portrait crop)

Adding songs:
  new card from a batch  -> py -3.14 import_cards.py  && py -3.14 site_build.py
  one-off song          -> py -3.14 add_song.py --png ... --artist ... --title ...
"""
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, 'songs.json')
SITE = os.path.join(ROOT, 'site')
CARDS = os.path.join(SITE, 'cards')
THUMBS = os.path.join(SITE, 'thumbs')
DATA = os.path.join(SITE, 'data')

THUMB_W = 560
FULL_MAX_W = 1600


def slug(path):
    return os.path.splitext(os.path.basename(path))[0]


def build_assets(src, name):
    """preview = top of the card, always exactly 4:5 portrait, never distorted"""
    im = Image.open(src).convert('RGB')
    w, h = im.size

    tw = min(THUMB_W, w)
    target_h = int(round(tw * 5 / 4))
    if h >= int(w * 1.25):
        crop = im.crop((0, 0, w, int(w * 1.25)))
    else:
        cw = max(1, min(w, int(h / 1.25)))
        left = (w - cw) // 2
        crop = im.crop((left, 0, left + cw, h))
    crop = crop.resize((tw, target_h), Image.LANCZOS)
    crop.save(os.path.join(THUMBS, name + '.webp'), 'WEBP', quality=80, method=6)

    f = im
    if w > FULL_MAX_W:
        f = im.resize((FULL_MAX_W, max(1, int(h * FULL_MAX_W / w))), Image.LANCZOS)
    f.save(os.path.join(CARDS, name + '.webp'), 'WEBP', quality=88, method=6)
    return (tw, target_h), f.size


def main():
    for d in (SITE, CARDS, THUMBS, DATA):
        os.makedirs(d, exist_ok=True)

    cat = json.load(open(CATALOG, encoding='utf-8')) if os.path.exists(CATALOG) else []

    songs, used = [], set()
    missing = 0
    for e in cat:
        src = os.path.join(ROOT, e['card'])
        if not os.path.exists(src):
            print('  MISSING card file:', e['card'])
            missing += 1
            continue
        name = slug(e['card'])
        used.add(name)
        tsz, fsz = build_assets(src, name)
        songs.append({
            'id': e.get('id', name),
            'title': e.get('title', ''),
            'artist': e.get('artist', ''),
            'tag': e.get('tag', ''),
            'rock': bool(e.get('rock')),
            'channel': e.get('channel', ''),
            'url': e.get('url', ''),
            'card': 'cards/%s.webp' % name,
            'thumb': 'thumbs/%s.webp' % name,
            'thumbW': tsz[0], 'thumbH': tsz[1],
            'w': fsz[0], 'h': fsz[1],
        })

    # drop assets that no longer belong to any song
    for d, ext in ((CARDS, '.webp'), (THUMBS, '.webp')):
        for f in os.listdir(d):
            if f.endswith(ext) and os.path.splitext(f)[0] not in used:
                os.remove(os.path.join(d, f))
                print('  removed stale asset:', f)

    payload = {
        'channels': [
            {'id': 'GuitarZero2HeroExpress', 'name': 'GuitarZero2HeroExpress',
             'url': 'https://www.youtube.com/@GuitarZero2HeroExpress'},
            {'id': 'BernadetteTeachesMusic', 'name': 'BernadetteTeachesMusic',
             'url': 'https://www.youtube.com/@BernadetteTeachesMusic'},
        ],
        'songs': songs,
    }
    with open(os.path.join(DATA, 'songs.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    rocks = sum(1 for s in songs if s['rock'])
    tot = sum(os.path.getsize(os.path.join(CARDS, f)) for f in os.listdir(CARDS))
    print('\n%d songs (%d rock)  |  site/cards = %.1f MB%s'
          % (len(songs), rocks, tot / 1048576, '  |  %d missing' % missing if missing else ''))


if __name__ == '__main__':
    main()
