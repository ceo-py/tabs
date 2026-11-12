import json, re, csv

rows = json.load(open('classified.json', encoding='utf-8'))
flags = {r['id']: r for r in json.load(open('guitar_only.json', encoding='utf-8'))}
for r in rows:
    r.update({k: v for k, v in flags.get(r['id'], {}).items() if k in ('song_lesson', 'clean')})
guitar = [r for r in rows if r['inst'] == 'guitar']

def fmt(d):
    return '%s-%s-%s' % (d[:4], d[4:6], d[6:8]) if d and len(d) == 8 else '?'

def hhmmss(s):
    try:
        s = int(s)
    except Exception:
        return ''
    return '%d:%02d' % (s // 60, s % 60)

rock = [r for r in guitar if r['rock'] and r.get('song_lesson')]
nonrock = [r for r in guitar if not r['rock'] and r.get('song_lesson')]
other = [r for r in guitar if not r.get('song_lesson')]

def line(r):
    return '| %s | %s | %s | %s | %s |' % (
        r['tab'][:4], fmt(r['date']), hhmmss(r['dur']), r['id'], r['title'])

def table(title, items):
    print('\n### %s (%d)\n' % (title, len(items)))
    print('| тип | дата | дължина | ID | заглавие |')
    print('|---|---|---|---|---|')
    for r in sorted(items, key=lambda x: (x['tab'], x['date'] or '')):
        print(line(r))

print('# BernadetteTeachesMusic — китарни уроци\n')
print('Канал: https://www.youtube.com/@BernadetteTeachesMusic')
print('Проучени видеа: %d (960 дълги + 317 Shorts)' % (len(rows) + 878))
print('Китарни видеа: %d | Уроци за песни: %d | Рок: %d' % (
    len(guitar), len(rock) + len(nonrock), len(rock)))

table('РОК — приоритет за извличане', rock)
table('Останали уроци за песни (не-рок)', nonrock)
table('Технически/общи китарни видеа', other)

with open('guitar_lessons.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['tip', 'data', 'dylzhina_s', 'id', 'zaglavie', 'rok', 'url'])
    for r in sorted(guitar, key=lambda x: (x['tab'], x['date'] or '')):
        w.writerow([r['tab'], fmt(r['date']), hhmmss(r['dur']), r['id'], r['title'],
                    'да' if r['rock'] else 'не', r['url']])

print('\nЗаписано: guitar_lessons.csv')
