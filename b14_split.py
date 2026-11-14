# -*- coding: utf-8 -*-
"""Split the remaining batch 14 songs over four agents."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(ROOT, 'gz_batches', 'batch14.json'), encoding='utf-8'))

todo = []
for i in items:
    card = os.path.join(ROOT, i['out'].replace('/', os.sep))
    if not os.path.exists(card):
        todo.append(i)

# the three songs that already have a spec but no rendered card go first
spec_dir = os.path.join(ROOT, 'b14_spec')
specced = set()
if os.path.isdir(spec_dir):
    for fn in os.listdir(spec_dir):
        if fn.endswith('.json'):
            spec = json.load(open(os.path.join(spec_dir, fn), encoding='utf-8'))
            specced.add(os.path.basename(spec.get('out', '')))

def key(i):
    return (0 if os.path.basename(i['out']) in specced else 1, i['song'])

todo.sort(key=key)

groups = [todo[0:6], todo[6:12], todo[12:18], todo[18:23]]
for n, g in enumerate(groups, 1):
    p = os.path.join(ROOT, 'b14_assign_%d.json' % n)
    json.dump(g, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('--- agent %d (%d songs) -> %s' % (n, len(g), os.path.basename(p)))
    for i in g:
        spec = 'spec' if os.path.basename(i['out']) in specced else '   '
        print('   %s %-11s %s' % (spec, i['id'], i['song']))
