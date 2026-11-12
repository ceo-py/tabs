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
import hashlib
import json
import os
import re
from PIL import Image

import strip_link

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


def stamp(path):
    """short content hash — used to bust browser/CDN caches"""
    with open(path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def version_html(manifest_v):
    """Add ?v=<hash> to the css/js links in index.html and record the
    manifest version in a meta tag.

    Cloudflare and browsers cache by URL, so without this a rebuild would
    keep serving the previous app.js / style.css / songs.json. The hashes
    change only when the file itself changes, so there is no needless
    cache churn.
    """
    html_path = os.path.join(SITE, 'index.html')
    if not os.path.exists(html_path):
        return
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    new = html
    for rel, attr in (('style.css', 'href'), ('app.js', 'src'), ('chords.js', 'src')):
        p = os.path.join(SITE, rel)
        if not os.path.exists(p):
            continue
        new = re.sub(r'%s="%s(?:\?v=[0-9a-f]+)?"' % (attr, re.escape(rel)),
                     '%s="%s?v=%s"' % (attr, rel, stamp(p)), new)
    meta = '<meta name="site-build" content="%s">' % manifest_v
    if 'name="site-build"' in new:
        new = re.sub(r'<meta name="site-build" content="[0-9a-f]*">', meta, new)
    else:
        new = new.replace('</head>', '  ' + meta + '\n</head>')
    if new != html:
        with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new)
        print('  index.html: asset versions refreshed')


def build_assets(src, name):
    """preview = top of the card, always exactly 4:5 portrait, never distorted"""
    im = Image.open(src).convert('RGB')
    # the "▶ youtube.com/watch?v=..." line is dropped from the site copy
    # (the archived PNGs in out/ and out_gz/ stay untouched)
    strip_link.strip_link(im)
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
    thumb_path = os.path.join(THUMBS, name + '.webp')
    crop.save(thumb_path, 'WEBP', quality=80, method=6)

    f = im
    if w > FULL_MAX_W:
        f = im.resize((FULL_MAX_W, max(1, int(h * FULL_MAX_W / w))), Image.LANCZOS)
    card_path = os.path.join(CARDS, name + '.webp')
    f.save(card_path, 'WEBP', quality=88, method=6)
    return (tw, target_h), f.size, stamp(card_path), stamp(thumb_path)


def main():
    for d in (SITE, CARDS, THUMBS, DATA):
        os.makedirs(d, exist_ok=True)

    cat = json.load(open(CATALOG, encoding='utf-8')) if os.path.exists(CATALOG) else []

    # chord shapes + the chord list of every song (for the chord legend)
    shapes_path = os.path.join(ROOT, 'chord_shapes.json')
    shapes = json.load(open(shapes_path, encoding='utf-8')) if os.path.exists(shapes_path) else {}
    chords_path = os.path.join(ROOT, 'chords.json')
    song_chords = json.load(open(chords_path, encoding='utf-8')) if os.path.exists(chords_path) else {}
    # cards that already show a fretboard diagram in the video need no legend
    diag_path = os.path.join(ROOT, 'chords_has_diagram.json')
    has_diagram = json.load(open(diag_path, encoding='utf-8')) if os.path.exists(diag_path) else {}

    def chords_for(card_path):
        """the chords of a card, in lesson order, without repeats.

        A card that already shows a fretboard diagram gets an empty list —
        the legend would only duplicate what is on the picture."""
        if has_diagram.get(card_path, 'NONE') == 'DIAGRAM':
            return []
        out = []
        for c in song_chords.get(card_path, []):
            if c not in out:
                out.append(c)
        return out

    if shapes:
        with open(os.path.join(DATA, 'chord_shapes.json'), 'w', encoding='utf-8') as f:
            json.dump(shapes, f, ensure_ascii=False, separators=(',', ':'))

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
        tsz, fsz, card_v, thumb_v = build_assets(src, name)
        songs.append({
            'id': e.get('id', name),
            'title': e.get('title', ''),
            'artist': e.get('artist', ''),
            'tag': e.get('tag', ''),
            'rock': bool(e.get('rock')),
            'channel': e.get('channel', ''),
            'url': e.get('url', ''),
            # ?v=<content hash> so a rebuilt card is never served from an old cache
            'card': 'cards/%s.webp?v=%s' % (name, card_v),
            'thumb': 'thumbs/%s.webp?v=%s' % (name, thumb_v),
            'thumbW': tsz[0], 'thumbH': tsz[1],
            'w': fsz[0], 'h': fsz[1],
            # chords of the lesson -> the fretboard legend under the card
            'chords': chords_for(e['card']),
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

    version_html(stamp(os.path.join(DATA, 'songs.json')))

    rocks = sum(1 for s in songs if s['rock'])
    tot = sum(os.path.getsize(os.path.join(CARDS, f)) for f in os.listdir(CARDS))
    print('\n%d songs (%d rock)  |  site/cards = %.1f MB%s'
          % (len(songs), rocks, tot / 1048576, '  |  %d missing' % missing if missing else ''))


if __name__ == '__main__':
    main()
