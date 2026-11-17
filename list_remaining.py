# -*- coding: utf-8 -*-
"""
List every lesson of the GuitarZero2HeroExpress channel that is not in the
catalog yet.

    py -3.14 list_remaining.py            # -> REMAINING-LESSONS.md + stdout summary

Sources
    gz_tabs_all.json     the master list of the channel (606 lessons)
    songs.json           what is published already (source of truth)
    gz_batches/*.json    which lessons are already planned in a batch

The output file lists the lessons grouped by artist, with the batch they
belong to (batch15 / batch16) or "-" for the ones that are not planned yet.
"""
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, 'gz_tabs_all.json')
CATALOG = os.path.join(ROOT, 'songs.json')
BATCHES = os.path.join(ROOT, 'gz_batches')
OUT_MD = os.path.join(ROOT, 'REMAINING-LESSONS.md')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def batch_map():
    """video id -> name of the batch file it is planned in"""
    out = {}
    for fn in sorted(os.listdir(BATCHES)):
        if not fn.startswith('batch') or not fn.endswith('.json'):
            continue
        name = os.path.splitext(fn)[0]
        for r in load(os.path.join(BATCHES, fn)):
            out[r['id']] = name
    return out


def main():
    master = load(MASTER)
    catalog = load(CATALOG)

    done = set()
    bern_done = 0
    for e in catalog:
        if e.get('channel') == 'GuitarZero2HeroExpress':
            done.add(e['id'])
        elif e.get('channel') == 'BernadetteTeachesMusic':
            bern_done += 1

    batches = batch_map()
    remaining = [r for r in master if r['id'] not in done]

    by_artist = defaultdict(list)
    for r in remaining:
        by_artist[r['artist']].append(r)

    planned = [r for r in remaining if r['id'] in batches]
    unplanned = [r for r in remaining if r['id'] not in batches]

    lines = []
    lines.append('# Останали уроци — %s' % 'GuitarZero2HeroExpress')
    lines.append('')
    lines.append('Генерирано с `py -3.14 list_remaining.py`.')
    lines.append('')
    lines.append('## Обзор')
    lines.append('')
    lines.append('| | |')
    lines.append('|---|---|')
    lines.append('| Уроци в канала (`gz_tabs_all.json`) | %d |' % len(master))
    lines.append('| Публикувани (GuitarZero2HeroExpress) | %d |' % len(done))
    lines.append('| **Остават** | **%d** |' % len(remaining))
    lines.append('| От тях в готов партиден файл | %d (batch15: %d, batch16: %d) |' % (
        len(planned),
        len([r for r in planned if batches[r['id']] == 'batch15']),
        len([r for r in planned if batches[r['id']] == 'batch16'])))
    lines.append('| От тях без партиден файл | %d |' % len(unplanned))
    lines.append('| BernadetteTeachesMusic | %d карти — всички публикувани |' % bern_done)
    lines.append('')
    lines.append('Следващите 25 за работа са готови като `gz_batches/batch15.json` '
                 '(още %d) и `gz_batches/batch16.json` (%d).' % (
                     len([r for r in planned if batches[r['id']] == 'batch15']),
                     len([r for r in planned if batches[r['id']] == 'batch16'])))
    lines.append('')
    lines.append('## Списък по изпълнител')
    lines.append('')
    lines.append('| # | Изпълнител | Песен | Формат | YouTube id | Партида |')
    lines.append('|---|---|---|---|---|---|')
    n = 0
    for artist in sorted(by_artist, key=lambda a: a.lower()):
        for r in sorted(by_artist[artist], key=lambda x: x['song'].lower()):
            n += 1
            b = batches.get(r['id'], '—')
            lines.append('| %d | %s | %s | %s | `%s` | %s |' % (
                n, artist, r['song'], r.get('tag', ''), r['id'], b))
    lines.append('')
    lines.append('## Само id-тата (за скриптове)')
    lines.append('')
    lines.append('```')
    for r in remaining:
        lines.append(r['id'])
    lines.append('```')
    lines.append('')

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print('remaining: %d of %d' % (len(remaining), len(master)))
    print('  planned   : %d' % len(planned))
    print('  unplanned : %d' % len(unplanned))
    print('  artists   : %d' % len(by_artist))
    print('-> %s' % os.path.relpath(OUT_MD, ROOT))


if __name__ == '__main__':
    main()
