import json, csv, os, re

tabs = json.load(open('gz_tabs_all.json', encoding='utf-8'))

# ---------- full list: CSV + MD ----------
with open('GuitarZero-TABS-list.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['#', 'artist', 'song', 'technique_tag', 'rock', 'duration', 'upload_date',
                'views', 'id', 'url'])
    for i, r in enumerate(tabs, 1):
        w.writerow([i, r['artist'], r['song'], r['tag'], 'да' if r['rock'] else 'не',
                    r['dur'], r['date'], r['views'], r['id'], r['url']])

def hhmmss(d):
    try:
        d = int(d)
    except Exception:
        return ''
    return '%d:%02d' % (d // 60, d % 60)

lines = ['# GuitarZero2HeroExpress — песни с ТАБОВЕ\n',
         'Канал: https://www.youtube.com/@GuitarZero2HeroExpress  ',
         'От 657 видеа в канала, **606 съдържат табове** (техника-еткет в заглавието: '
         '`Tabs + Chords`, `Tabs`, `Tabs + Solo`, `Riffs + Tabs` и т.н.).  ',
         'Останалите 51 са само акорди (`Chords`, `Riffs + Chords`, `Fingerpicking + Chords`) '
         'и не влизат тук.\n',
         'Сортирано по изпълнител, после по песен.\n',
         '## Списък (%d)\n' % len(tabs),
         '| # | Изпълнител | Песен | Техника | Рок | Дължина | Дата | Видео |',
         '|---|---|---|---|---|---|---|---|']
for i, r in enumerate(tabs, 1):
    lines.append('| %d | %s | %s | %s | %s | %s | %s | [▶](%s) |' % (
        i, r['artist'], r['song'], r['tag'], 'да' if r['rock'] else '',
        hhmmss(r['dur']), r['date'], r['url']))

open('GuitarZero-TABS-list.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('written GuitarZero-TABS-list.csv / .md with', len(tabs), 'rows')

# ---------- batches of the first 50 ----------
first50 = tabs[:50]
BATCHES = [first50[0:13], first50[13:25], first50[25:38], first50[38:50]]
os.makedirs('gz_batches', exist_ok=True)

def safe(s):
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s).strip()
    return '-'.join(s.split()) or 'Untitled'

manifests = []
for bi, batch in enumerate(BATCHES, 1):
    items = []
    for r in batch:
        name = '%s-%s' % (safe(r['artist']), safe(r['song']))
        items.append({
            'id': r['id'],
            'artist': r['artist'],
            'song': r['song'],
            'tag': r['tag'],
            'rock': r['rock'],
            'out': 'out_gz/%s.png' % name,
            'url': r['url'],
        })
    p = 'gz_batches/batch%d.json' % bi
    json.dump(items, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    manifests.append(p)
    print('batch%d: %d songs -> %s' % (bi, len(items), p))

# also a plain id list per batch for yt-dlp --batch-file
for bi, batch in enumerate(BATCHES, 1):
    with open('gz_batches/batch%d_ids.txt' % bi, 'w', encoding='ascii') as f:
        for r in batch:
            f.write(r['id'] + '\n')
print('done')
