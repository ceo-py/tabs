import json, os, glob
from PIL import Image

rows = []
for bi in range(1, 5):
    for r in json.load(open('gz_batches/batch%d.json' % bi, encoding='utf-8')):
        rows.append(r)

# resolve output-name collisions (same song covered by two different videos)
_seen = {}
for r in rows:
    o = r['out']
    if o in _seen:
        stem, ext = os.path.splitext(o)
        newo = stem + '-Alt' + ext
        n = 2
        while newo in [x['out'] for x in rows]:
            newo = '%s-Alt%d%s' % (stem, n, ext)
            n += 1
        print('collision: %s (id %s) -> %s' % (o, r['id'], newo))
        r['out'] = newo
    _seen[r['out']] = True

def hhmmss(d):
    try:
        d = int(d)
    except Exception:
        return ''
    return '%d:%02d' % (d // 60, d % 60)

tabs = json.load(open('gz_tabs_all.json', encoding='utf-8'))
meta = {r['id']: r for r in tabs}

lines = ['# GuitarZero2HeroExpress — карти с табове, партида 1 (първите 50)\n',
         'Канал: https://www.youtube.com/@GuitarZero2HeroExpress  ',
         'Всяка карта съдържа извадени директно от видеото TAB нотни листи '
         '(VERSE / CHORUS / BRIDGE), chord pattern и strumming pattern, плюс линк към видеото.\n',
         '## Карти (%d)\n' % len(rows),
         '| # | Песен | Изпълнител | Техника | Рок | Карта | Видео |',
         '|---|---|---|---|---|---|---|']
ok = miss = 0
for i, r in enumerate(rows, 1):
    exists = os.path.exists(r['out'])
    ok += exists
    miss += (not exists)
    m = meta.get(r['id'], {})
    lines.append('| %d | %s | %s | %s | %s | `%s` %s | [▶](%s) |' % (
        i, r['song'], r['artist'], r['tag'], 'да' if r['rock'] else '',
        r['out'], 'OK' if exists else '**ЛИПСВА**', r['url']))

lines.append('\n**Готови: %d / %d**' % (ok, len(rows)))
lines.append('\n## Размери\n')
lines.append('| Карта | Размер |')
lines.append('|---|---|')
for r in rows:
    if os.path.exists(r['out']):
        im = Image.open(r['out'])
        lines.append('| `%s` | %dx%d |' % (r['out'], im.width, im.height))

open('GZ-CARDS-INDEX.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('written GZ-CARDS-INDEX.md  |  ok %d, missing %d' % (ok, miss))
for r in rows:
    if not os.path.exists(r['out']):
        print('  MISSING', r['out'])
