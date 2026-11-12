# -*- coding: utf-8 -*-
"""
Add ONE song to the site catalog.

    py -3.14 add_song.py --png out_gz/Adele-Someone-Like-You.png \
        --artist "Adele" --title "Someone Like You" --url https://www.youtube.com/watch?v=XXX

Optional:  --channel GuitarZero2HeroExpress | BernadetteTeachesMusic
           --tag "Tabs + Chords"      --rock / --no-rock
           --id <youtube id>          (default: guessed from --url)

The PNG is copied into site/cards/, a webp preview is generated, and the entry
is appended to songs.json (the single source of truth).
"""
import argparse
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, 'songs.json')
SITE_CARDS = os.path.join(ROOT, 'site', 'cards')
SITE_THUMBS = os.path.join(ROOT, 'site', 'thumbs')

THUMB_W = 560
FULL_MAX_W = 1600


def slug(path):
    return os.path.splitext(os.path.basename(path))[0]


def build_assets(src, name):
    from PIL import Image
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
    crop.save(os.path.join(SITE_THUMBS, name + '.webp'), 'WEBP', quality=80, method=6)

    f = im
    if w > FULL_MAX_W:
        f = im.resize((FULL_MAX_W, max(1, int(h * FULL_MAX_W / w))), Image.LANCZOS)
    f.save(os.path.join(SITE_CARDS, name + '.webp'), 'WEBP', quality=88, method=6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', required=True, help='path to the lesson-card PNG')
    ap.add_argument('--artist', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--url', default='')
    ap.add_argument('--channel', default='GuitarZero2HeroExpress')
    ap.add_argument('--tag', default='Tabs + Chords')
    ap.add_argument('--id', default='')
    ap.add_argument('--rock', dest='rock', action='store_true', default=None)
    ap.add_argument('--no-rock', dest='rock', action='store_false')
    args = ap.parse_args()

    src = os.path.abspath(args.png)
    if not os.path.exists(src):
        raise SystemExit('PNG not found: %s' % src)

    vid = args.id
    if not vid and args.url:
        import re
        m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', args.url)
        vid = m.group(1) if m else slug(args.png)

    os.makedirs(SITE_CARDS, exist_ok=True)
    os.makedirs(SITE_THUMBS, exist_ok=True)
    name = slug(src)
    build_assets(src, name)

    rel = os.path.relpath(src, ROOT).replace('\\', '/')
    entry = {
        'id': vid,
        'title': args.title,
        'artist': args.artist,
        'tag': args.tag,
        'rock': bool(args.rock),
        'channel': args.channel,
        'url': args.url,
        'card': rel,
    }

    cat = json.load(open(CATALOG, encoding='utf-8')) if os.path.exists(CATALOG) else []
    cat = [e for e in cat if e.get('id') != vid]
    cat.append(entry)
    cat.sort(key=lambda s: (s.get('artist', '').lower(), s.get('title', '').lower(), s.get('channel', '')))
    with open(CATALOG, 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)

    print('added: %s - %s  (%s)' % (args.artist, args.title, vid))
    print('catalog now holds %d songs -> %s' % (len(cat), os.path.relpath(CATALOG, ROOT)))


if __name__ == '__main__':
    main()
