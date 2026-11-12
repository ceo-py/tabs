# -*- coding: utf-8 -*-
import io, json, re, sys, collections
sys.path.insert(0, r'D:\MiniMax Code Repos\Guitar Lessons')
sys.stdout.reconfigure(encoding='utf-8')
from gz_titleparse import parse_title
from gz_genres import normalise_artist, is_rock, ROCK_ARTISTS

recs = {}
for line in io.open('gz_meta.json', encoding='utf-8'):
    line = line.strip()
    if line:
        o = json.loads(line)
        recs[o['id']] = o

HASHTAG = re.compile(r'video by #([A-Za-z0-9_\'\-]+)', re.I)

# titles that need hand-set artist (grammar the parser can't handle)
MANUAL_ARTIST = {
    'Ryxmk_-XIJ0': 'Radiohead',            # "High And Dry Radiohead"
    'Y-pYj_1TQKY': 'Boyce Avenue',         # Game Of Thrones (Boyce Avenue version)
    'BuUx1e2SZdU': 'Ramin Djawadi',        # Game Of Thrones theme
    'vI1LIY4RmoU': 'John Williams',        # Harry Potter theme
    'TF001G6I_S4': 'Gustavo Santaolalla',  # The Last Of Us theme
    'zgPeDuZnTRo': 'Ramin Djawadi',        # Westworld theme
    'ILf-Pcd5rsY': 'Traditional',
    '8DUtH_RVFh4': 'Traditional',
    'CPdZrYRy4_U': 'Traditional',
    'B2T1EQ7ClBY': 'Traditional',
    'FZ5ATOu7sM0': 'Traditional',
    'pz-kI2iZNu8': 'Joey Batey',            # Toss A Coin To Your Witcher
    'YH_6caceDd0': 'Bob Dylan',            # Make You Feel My Love
    'ibGXTK2fT80': 'John Lennon',          # Happy Xmas (War Is Over)
    'WY_cxZGaSeA': 'John Mayer',           # Wild Blue - backing track
    'q63PX69vSTU': 'Major Lazer ft. Marcus Mumford',
    'AikrCVRguec': 'Post Malone & Swae Lee',
    'zmahoLrtne0': 'Yungblud & Marshmello',
    'WYtm_9xQB9k': 'Ed Sheeran, Bruno Mars & Chris Stapleton',
    '4_MLrGCrkx4': 'Dan + Shay & Justin Bieber',
    '8BZuUS4_5A0': 'Ed Sheeran & Taylor Swift',
    'Kr-hwv1dopY': 'Ed Sheeran & Justin Bieber',
    'M1tqgUK1ugw': 'Israel Kamakawiwo\u02bbole',
    'Hvf0sdfsHcs': 'Frank Valli',
}
MANUAL_SONG = {
    'YH_6caceDd0': "Make You Feel My Love",
    'ibGXTK2fT80': 'Happy Xmas (War Is Over)',
    'WY_cxZGaSeA': 'Wild Blue',
    'Ryxmk_-XIJ0': 'High And Dry',
    'a-QsXGhAFPE': 'Last Train Home',
    '_tTyvZRTJNs': 'Bohemian Rhapsody',
    'raLENTkO6M0': 'Crazy Little Thing Called Love',
    'CGKmmAPBwHw': 'The Man Who Sold The World',
}

# non-song videos / special types
def classify_type(vid, title, song, artist, desc):
    t = title.lower()
    if 'backing track' in t:
        return 'other', 'backing track (no lead performance)'
    if song and re.search(r'theme', song, re.I) and not artist:
        return 'song_tutorial', 'media soundtrack theme'
    return 'song_tutorial', ''

rows = []
for vid, rec in recs.items():
    title = rec.get('title') or ''
    song, artist_raw, notes = parse_title(title)
    desc = rec.get('description') or ''

    if vid in MANUAL_ARTIST:
        artist = MANUAL_ARTIST[vid]
    else:
        artist = normalise_artist(artist_raw)
    if vid in MANUAL_SONG:
        song = MANUAL_SONG[vid]

    # description hashtag cross-check
    m = HASHTAG.search(desc)
    desc_artist = normalise_artist(m.group(1)) if m else None
    agree = None
    if desc_artist and artist:
        a = artist.lower().replace(' the ', ' ').replace('&', 'and')
        d = desc_artist.lower().replace(' the ', ' ').replace('&', 'and')
        agree = (a == d) or (d in a) or (a in d)

    ttype, tnote = classify_type(vid, title, song, artist, desc)
    rock = is_rock(artist)
    if ttype == 'other':
        rock = False

    dur = rec.get('duration') or 0
    mmss = f"{dur//60}:{dur%60:02d}"
    ud = rec.get('upload_date') or ''
    ud_fmt = f"{ud[0:4]}-{ud[4:6]}-{ud[6:8]}" if len(ud) == 8 else ud

    rows.append({
        'id': vid, 'artist': artist, 'song': song, 'title': title,
        'genre': '', 'rock': rock, 'type': ttype, 'instrument': 'guitar',
        'duration_mm_ss': mmss, 'upload_date': ud_fmt,
        'views': rec.get('view_count'),
        'url': f"https://www.youtube.com/watch?v={vid}",
        'desc_artist': desc_artist, 'artist_agree': agree,
        'tnote': tnote, 'notes': notes,
    })

rows.sort(key=lambda r: (r['upload_date'], r['id']))
print('rows:', len(rows))
print('types:', collections.Counter(r['type'] for r in rows))
print('rock:', collections.Counter(r['rock'] for r in rows))
print('rock+song_tutorial:', sum(1 for r in rows if r['rock'] and r['type'] in ('song_tutorial', 'jam_along')))
print('artist cross-check agreement:',
      collections.Counter('agree' if r['artist_agree'] else ('no-desc-tag' if not r['desc_artist'] else 'DISAGREE')
                          for r in rows))
print()
print('--- DISAGREEMENTS (title artist vs description hashtag) ---')
for r in rows:
    if r['artist_agree'] is False:
        print(f"  {r['id']}  title='{r['artist']}'  desc='{r['desc_artist']}'  | {r['title'][:70]}")
print()
print('--- rows with artist None ---')
for r in rows:
    if r['artist'] is None:
        print(f"  {r['id']} | {r['title'][:75]}")
print()
print('--- rows with no description hashtag ---')
for r in rows:
    if not r['desc_artist']:
        print(f"  {r['id']} | {r['title'][:75]}")

json.dump(rows, io.open('gz_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nwrote gz_rows.json')
