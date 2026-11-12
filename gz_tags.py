import json, re, csv
from collections import Counter

rows = json.load(open('gz_parsed.json', encoding='utf-8'))
print('parsed rows:', len(rows))
print('keys:', sorted(rows[0].keys()))

# The channel's title grammar ends with a bracketed technique tag.
# Extract everything between the last pair of pipes / brackets.
tag_re = re.compile(r'[|]\s*([^|]{2,60}?)\s*[|]\s*$')
tag_re2 = re.compile(r'[\[\(]\s*([^)\]]{2,60}?)\s*[\]\)]\s*$')

tags = Counter()
for r in rows:
    t = r.get('title', '')
    m = tag_re.search(t) or tag_re2.search(t)
    tags[m.group(1).strip() if m else '(none)'] += 1

print('\n--- technique tags in titles ---')
for k, v in tags.most_common(40):
    print('%5d  %s' % (v, k))
