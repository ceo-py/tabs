import json, sys

rows = json.load(open('classified.json', encoding='utf-8'))
g = [r for r in rows if r['inst'] == 'guitar']
mode = sys.argv[1] if len(sys.argv) > 1 else 'rock'

if mode == 'rock':
    sel = [r for r in g if r['rock']]
    print('=== GUITAR + ROCK (%d) ===' % len(sel))
elif mode == 'nonrock':
    sel = [r for r in g if not r['rock']]
    print('=== GUITAR (non-rock) (%d) ===' % len(sel))
else:
    sel = g
    print('=== ALL GUITAR (%d) ===' % len(sel))

for r in sorted(sel, key=lambda x: (x['tab'], x['date'] or '')):
    print('%s %s %s | %s' % (r['tab'][:4], r['date'] or '?', r['id'], r['title'][:95]))
