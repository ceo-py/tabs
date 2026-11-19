# -*- coding: utf-8 -*-
"""Collect the `diagram` value each batch-21 build agent recorded in its spec
and write chords_diagram_p23.json (same shape as chords_diagram_p22.json).

    py -3.14 _b21_classify.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC_DIRS = ['b21a_spec', 'b21b_spec', 'b21c_spec']
OUT = os.path.join(ROOT, 'chords_diagram_p23.json')


def main():
    result = {}
    missing = []
    for d in SPEC_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.json'))):
            spec = json.load(open(f, encoding='utf-8'))
            out = spec.get('out', '').replace('\\', '/')
            val = spec.get('diagram')
            if not out:
                missing.append((f, 'no out'))
                continue
            if val not in ('LETTERS', 'DIAGRAM', 'NONE'):
                missing.append((os.path.basename(f), 'diagram=%r' % (val,)))
                continue
            result[out] = val

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    counts = {}
    for v in result.values():
        counts[v] = counts.get(v, 0) + 1
    print('chords_diagram_p23.json: %d cards  %s' % (len(result), counts))
    for out in sorted(result):
        print('  %-58s %s' % (out, result[out]))
    if missing:
        print('\nSPECS NEEDING ATTENTION:')
        for m in missing:
            print('  ', m)


if __name__ == '__main__':
    main()
