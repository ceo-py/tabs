import json, re, glob, csv
from collections import Counter

# ---- technique tag from the channel's title grammar
tag_re = re.compile(r'[|]\s*([^|]{2,60}?)\s*[|]\s*$')
tag_re2 = re.compile(r'[\[\(]\s*([^)\]]{2,60}?)\s*[\]\)]\s*$')

def tag_of(title):
    m = tag_re.search(title) or tag_re2.search(title)
    return m.group(1).strip() if m else ''

def has_tabs(tag, title):
    t = tag.lower()
    return 'tab' in t or 'tabs' in t or 'tab' in title.lower().split('|')[-2:][0:1]

# ---- metadata from the agent's jsonl parts
meta = {}
for f in sorted(glob.glob('gz_meta_part_*.jsonl')):
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        meta[o['id']] = o

parsed = json.load(open('gz_parsed.json', encoding='utf-8'))

# ---- rock flag from the agent's CSV
rock = {}
with open('GuitarZero2HeroExpress-rock.csv', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        rock[row['id']] = row['rock'].strip().lower() in ('true', '1', 'yes')

rows = []
for p in parsed:
    vid = p['id']
    title = p.get('title', '')
    tag = tag_of(title)
    m = meta.get(vid, {})
    rows.append({
        'id': vid,
        'artist': p.get('artist') or '',
        'song': p.get('song') or '',
        'title': title,
        'tag': tag,
        'tabs': 'tab' in tag.lower(),
        'rock': rock.get(vid, False),
        'dur': m.get('duration') or '',
        'date': m.get('upload_date') or '',
        'views': m.get('view_count') or '',
        'url': 'https://www.youtube.com/watch?v=' + vid,
    })

tabs = [r for r in rows if r['tabs']]
notabs = [r for r in rows if not r['tabs']]

def dur_s(d):
    try:
        return int(d)
    except Exception:
        return 0

# canonical order: artist, then song
tabs.sort(key=lambda r: (r['artist'].lower(), r['song'].lower(), -dur_s(r['dur'])))

json.dump(rows, open('gz_all_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(tabs, open('gz_tabs_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('total videos      :', len(rows))
print('with TABS         :', len(tabs))
print('  of which rock   :', sum(1 for r in tabs if r['rock']))
print('  non-rock        :', sum(1 for r in tabs if not r['rock']))
print('without tabs      :', len(notabs))
print('  tags seen       :', Counter(r['tag'] for r in notabs).most_common(8))
print()
print('--- FIRST 50 TAB SONGS ---')
for i, r in enumerate(tabs[:50], 1):
    print('%2d | %-28s | %-32s | %-24s | %s' % (
        i, r['artist'][:28], r['song'][:32], r['tag'][:24], 'ROCK' if r['rock'] else ''))
