import json, re, glob, csv

rows = json.load(open('gz_all_rows.json', encoding='utf-8'))

# The channel's grammar is: "<song> Guitar Cover <artist> 🎸|TAG|"
# but a handful omit the artist, or put it before "Guitar Cover".
cov = re.compile(r'^(?P<song>.+?)\s*Guitar Cover\s*(?P<artist>.*?)\s*[🎸|]*$', re.I)
plain = re.compile(r'^(?P<song>.+?)\s+(?P<artist>Radiohead|[A-Z][\w&.\'\- ]{2,30})\s*[🎸|]*$')

for r in rows:
    if r['artist'] and r['song']:
        continue
    t = re.sub(r'\s*[🎸🎄|]+\s*', ' ', r['title'])
    t = re.sub(r'\s+', ' ', t).strip()
    tag = r['tag']
    t = re.sub(r'\s*(Tabs?\s*\+\s*Chords?|Chords?|Fingerpicking\s*\+\s*Chords?|'
               r'Riffs?\s*\+\s*Chords?|Tabs?\s*\+\s*Solo|Solo\s*\+\s*Tabs?)\s*$', '', t,
               flags=re.I).strip()
    m = cov.match(t)
    if m:
        r['song'] = m.group('song').strip()
        r['artist'] = m.group('artist').strip() or '—'
        continue
    m = plain.match(t)
    if m:
        r['song'] = m.group('song').strip()
        r['artist'] = m.group('artist').strip()
        continue
    # last resort: song only, no artist in title
    r['song'] = t
    r['artist'] = '—'

json.dump(rows, open('gz_all_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

tabs = [r for r in rows if r['tabs']]
tabs.sort(key=lambda r: (r['artist'].lower(), r['song'].lower()))
json.dump(tabs, open('gz_tabs_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('tab songs:', len(tabs))
print('still missing artist:', sum(1 for r in tabs if r['artist'] in ('', '—')))
print()
for i, r in enumerate(tabs[:12], 1):
    print('%2d | %-26s | %-34s | %s' % (i, r['artist'][:26], r['song'][:34], r['tag']))
