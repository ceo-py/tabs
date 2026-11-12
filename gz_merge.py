# -*- coding: utf-8 -*-
import io, json, os, re, sys, glob, collections
sys.path.insert(0, r'D:\MiniMax Code Repos\Guitar Lessons')
sys.stdout.reconfigure(encoding='utf-8')

recs = {}
bad = 0
for f in sorted(glob.glob('gz_meta_part_*.jsonl')):
    for line in io.open(f, encoding='utf-8-sig'):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            bad += 1
            continue
        recs[o['id']] = o
print('parsed records:', len(recs), 'unparsable lines:', bad)

# merge into gz_meta.json (one JSON object per line)
with io.open('gz_meta.json', 'w', encoding='utf-8') as fh:
    for vid in sorted(recs):
        fh.write(json.dumps(recs[vid], ensure_ascii=False) + '\n')
print('wrote gz_meta.json')

# --- content sanity checks -------------------------------------------------
descs = ' '.join((r.get('description') or '') for r in recs.values()).lower()
for kw in ['ukulele', 'piano', 'keyboard', 'bass guitar', 'drum', 'violin', 'mandolin']:
    print(f'description mentions {kw!r}: {descs.count(kw)}')
print('description mentions "guitar":', descs.count('guitar'))
print('availability values:', collections.Counter(r.get('availability') for r in recs.values()))
print('live_status:', collections.Counter(r.get('live_status') for r in recs.values()))
print('missing duration:', sum(1 for r in recs.values() if not r.get('duration')))
print('missing upload_date:', sum(1 for r in recs.values() if not r.get('upload_date')))
print('missing view_count:', sum(1 for r in recs.values() if r.get('view_count') is None))

# play-along / tutorial language
pl = sum(1 for r in recs.values() if 'play along' in (r.get('description') or '').lower())
tu = sum(1 for r in recs.values() if 'tutorial' in (r.get('description') or '').lower())
print('descriptions containing "play along":', pl)
print('descriptions containing "tutorial":', tu)
print('descriptions with NO "play along":', sum(1 for r in recs.values() if 'play along' not in (r.get('description') or '').lower()))

# description-based artist hashtag signal
pat = re.compile(r'video by #([A-Za-z0-9_\'\-]+)', re.I)
n = sum(1 for r in recs.values() if pat.search(r.get('description') or ''))
print('descriptions matching "video by #artist":', n)
