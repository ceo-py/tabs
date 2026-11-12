import json, glob, re

recs = {}

# 1) JSON chunks (full metadata incl. description)
for f in sorted(glob.glob('chunk_*.json')):
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        recs[o['id']] = {
            'id': o['id'],
            'dur': o.get('duration'),
            'date': o.get('upload_date'),
            'views': o.get('view_count'),
            'desc': (o.get('description') or '')[:1200],
            'json_title': o.get('title', ''),
        }

# 2) tsv batch (fills gaps, description may be truncated/continues on next line)
tsv_ids = {}
for line in open('cand_meta2.tsv', encoding='utf-8'):
    if line.startswith('ERROR'):
        continue
    p = line.rstrip('\n').split('\t')
    if len(p) >= 4 and len(p[0]) == 11:
        tsv_ids[p[0]] = {
            'dur': p[1],
            'date': p[2],
            'views': p[3],
            'desc': p[4] if len(p) > 4 else '',
        }

# titles + tab from the raw flat playlists
titles = {}
for fn in ['videos_raw.txt', 'shorts_raw.txt']:
    tab = 'shorts' if 'shorts' in fn else 'videos'
    for line in open(fn, encoding='utf-8'):
        if '\t' not in line:
            continue
        p = line.rstrip('\n').split('\t')
        if len(p) >= 2 and len(p[0]) == 11:
            titles[p[0]] = (p[1].strip().strip('"'), tab)

for i, v in tsv_ids.items():
    if i in recs:
        if not recs[i]['desc']:
            recs[i]['desc'] = v['desc']
        if not recs[i]['date']:
            recs[i]['date'] = v['date']
        if not recs[i]['dur']:
            recs[i]['dur'] = v['dur']
    else:
        recs[i] = {'id': i, 'dur': v['dur'], 'date': v['date'], 'views': v['views'],
                   'desc': v['desc'], 'json_title': ''}

rows = []
for i, o in recs.items():
    t, tab = titles.get(i, (o.get('json_title', ''), 'videos'))
    rows.append({
        'id': i,
        'title': t,
        'tab': tab,
        'dur': o.get('dur'),
        'date': o.get('date'),
        'views': o.get('views'),
        'desc': o.get('desc') or '',
        'url': 'https://www.youtube.com/watch?v=' + i,
    })

rows.sort(key=lambda r: (r['date'] or '00000000'), reverse=True)
json.dump(rows, open('meta_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total rows', len(rows), '| with title', sum(1 for r in rows if r['title']))
print('desc guitar', sum(1 for r in rows if re.search('guitar', r['desc'], re.I)))
print('desc ukulele', sum(1 for r in rows if re.search('ukulele', r['desc'], re.I)))
print('desc tabs', sum(1 for r in rows if re.search(r'\btabs?\b', r['desc'], re.I)))
